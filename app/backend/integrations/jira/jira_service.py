"""
PM33 Jira Integration Service
Connects to Atlassian Jira API with tenant isolation and data sync
"""

import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import aiohttp
import asyncpg
from dataclasses import dataclass

from ..base.integration_base import BaseIntegration, SyncResult, FieldMapping, IntegrationConfig

logger = logging.getLogger(__name__)

@dataclass
class JiraProject:
    """Jira project data model"""
    key: str
    name: str
    id: str
    project_type: str
    lead: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

@dataclass 
class JiraIssue:
    """Jira issue data model"""
    key: str
    id: str
    summary: str
    description: Optional[str]
    issue_type: str
    status: str
    priority: str
    assignee: Optional[str]
    reporter: str
    created: datetime
    updated: datetime
    project_key: str
    labels: List[str] = None
    components: List[str] = None

class JiraIntegration(BaseIntegration):
    """
    Jira integration implementation
    
    Features:
    - Atlassian OAuth 2.0 authentication
    - Projects and issues sync with tenant isolation
    - Incremental sync with change detection
    - AI-powered field mapping for PM33 strategic context
    - Usage tracking for billing
    """
    
    def __init__(self, database_pool: asyncpg.Pool, config: IntegrationConfig):
        super().__init__(database_pool, config)
        self.base_url = "https://api.atlassian.com/ex/jira"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cloud_id: Optional[str] = None
        
    async def authenticate(self) -> bool:
        """Authenticate with Jira using OAuth token"""
        try:
            credentials = self.decrypt_credentials()
            access_token = credentials.get('access_token')
            
            if not access_token:
                self.logger.error("No access token found in credentials")
                return False
            
            # Get accessible resources (cloud ID)
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            
            async with self.session.get("https://api.atlassian.com/oauth/token/accessible-resources") as response:
                if response.status == 200:
                    resources = await response.json()
                    if resources:
                        self.cloud_id = resources[0]['id']  # Use first available resource
                        self.base_url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}"
                        self.logger.info(f"Authenticated with Jira cloud ID: {self.cloud_id}")
                        return True
                    else:
                        self.logger.error("No accessible Jira resources found")
                        return False
                else:
                    self.logger.error(f"Failed to get accessible resources: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Jira authentication failed: {str(e)}")
            return False
    
    async def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test connection to Jira"""
        try:
            if not await self.authenticate():
                return False, "Authentication failed"
            
            # Test with a simple API call
            async with self.session.get(f"{self.base_url}/rest/api/3/myself") as response:
                if response.status == 200:
                    user_info = await response.json()
                    return True, f"Connected as {user_info.get('displayName', 'Unknown User')}"
                else:
                    return False, f"Connection test failed: {response.status}"
                    
        except Exception as e:
            return False, f"Connection test error: {str(e)}"
        finally:
            if self.session:
                await self.session.close()
    
    async def sync_data(self, incremental: bool = True) -> SyncResult:
        """Sync Jira projects and issues to PM33"""
        start_time = datetime.now(timezone.utc)
        result = SyncResult(
            success=False,
            records_synced=0,
            records_updated=0, 
            records_created=0,
            errors=[],
            sync_duration_seconds=0,
            last_sync_at=start_time
        )
        
        try:
            if not await self.authenticate():
                result.errors.append("Authentication failed")
                return result
            
            # Sync projects first
            projects = await self._sync_projects()
            result.records_created += len(projects)
            
            # Sync issues for each project
            total_issues = 0
            for project in projects:
                issues = await self._sync_project_issues(project.key, incremental)
                total_issues += len(issues)
                
                # Log usage
                await self.log_usage("sync_issues", api_calls=len(issues) // 50 + 1)
            
            result.records_created += total_issues
            result.records_synced = result.records_created
            result.success = True
            
            # Store sync metadata
            await self.store_synced_data("sync_summary", [{
                "sync_type": "jira_full_sync",
                "projects_synced": len(projects),
                "issues_synced": total_issues,
                "sync_timestamp": start_time.isoformat()
            }])
            
        except Exception as e:
            result.errors.append(f"Sync error: {str(e)}")
            self.logger.error(f"Jira sync failed: {str(e)}")
        
        finally:
            if self.session:
                await self.session.close()
                
            result.sync_duration_seconds = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            
            await self.update_sync_status(result)
        
        return result
    
    async def _sync_projects(self) -> List[JiraProject]:
        """Sync Jira projects"""
        projects = []
        
        try:
            async with self.session.get(f"{self.base_url}/rest/api/3/project") as response:
                if response.status == 200:
                    projects_data = await response.json()
                    
                    for project_data in projects_data:
                        project = JiraProject(
                            key=project_data['key'],
                            name=project_data['name'],
                            id=project_data['id'],
                            project_type=project_data.get('projectTypeKey', 'unknown'),
                            lead=project_data.get('lead', {}).get('displayName'),
                            description=project_data.get('description'),
                            url=project_data.get('self')
                        )
                        projects.append(project)
                        
                        # Store project data
                        await self.store_synced_data("project", [{
                            "key": project.key,
                            "name": project.name,
                            "id": project.id,
                            "type": project.project_type,
                            "lead": project.lead,
                            "description": project.description
                        }])
                        
                else:
                    self.logger.error(f"Failed to fetch projects: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Project sync error: {str(e)}")
        
        return projects
    
    async def _sync_project_issues(self, project_key: str, incremental: bool = True) -> List[JiraIssue]:
        """Sync issues for a specific project"""
        issues = []
        start_at = 0
        max_results = 50
        
        # Build JQL query
        jql = f"project = {project_key}"
        if incremental and self.config.last_sync_at:
            # Only sync issues updated since last sync
            last_sync = self.config.last_sync_at.strftime('%Y-%m-%d %H:%M')
            jql += f" AND updated >= '{last_sync}'"
        
        try:
            while True:
                params = {
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": "summary,description,issuetype,status,priority,assignee,reporter,created,updated,labels,components"
                }
                
                async with self.session.get(f"{self.base_url}/rest/api/3/search", params=params) as response:
                    if response.status == 200:
                        search_result = await response.json()
                        batch_issues = search_result.get('issues', [])
                        
                        if not batch_issues:
                            break
                        
                        for issue_data in batch_issues:
                            fields = issue_data['fields']
                            
                            issue = JiraIssue(
                                key=issue_data['key'],
                                id=issue_data['id'],
                                summary=fields['summary'],
                                description=fields.get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text', '') if fields.get('description') else None,
                                issue_type=fields['issuetype']['name'],
                                status=fields['status']['name'],
                                priority=fields.get('priority', {}).get('name', 'None'),
                                assignee=fields.get('assignee', {}).get('displayName') if fields.get('assignee') else None,
                                reporter=fields['reporter']['displayName'],
                                created=datetime.fromisoformat(fields['created'].replace('Z', '+00:00')),
                                updated=datetime.fromisoformat(fields['updated'].replace('Z', '+00:00')),
                                project_key=project_key,
                                labels=[label for label in fields.get('labels', [])],
                                components=[comp['name'] for comp in fields.get('components', [])]
                            )
                            
                            issues.append(issue)
                            
                            # Store issue data for AI analysis
                            await self.store_synced_data("issue", [{
                                "key": issue.key,
                                "id": issue.id,
                                "title": issue.summary,
                                "description": issue.description,
                                "type": issue.issue_type,
                                "status": issue.status,
                                "priority": issue.priority,
                                "assignee": issue.assignee,
                                "reporter": issue.reporter,
                                "project": project_key,
                                "labels": issue.labels,
                                "components": issue.components,
                                "created_at": issue.created.isoformat(),
                                "updated_at": issue.updated.isoformat()
                            }])
                        
                        start_at += max_results
                        
                        # Check if we have more results
                        if start_at >= search_result.get('total', 0):
                            break
                            
                    else:
                        self.logger.error(f"Failed to fetch issues for project {project_key}: {response.status}")
                        break
                        
        except Exception as e:
            self.logger.error(f"Issue sync error for project {project_key}: {str(e)}")
        
        return issues
    
    async def get_available_fields(self) -> List[Dict[str, Any]]:
        """Get available Jira fields for mapping"""
        fields = [
            {"name": "summary", "type": "string", "description": "Issue summary/title"},
            {"name": "description", "type": "text", "description": "Issue description"},
            {"name": "issuetype", "type": "string", "description": "Issue type (Bug, Story, Task, etc.)"},
            {"name": "status", "type": "string", "description": "Issue status"},
            {"name": "priority", "type": "string", "description": "Issue priority"},
            {"name": "assignee", "type": "string", "description": "Assigned user"},
            {"name": "reporter", "type": "string", "description": "Reporter user"},
            {"name": "project", "type": "string", "description": "Project key"},
            {"name": "labels", "type": "array", "description": "Issue labels"},
            {"name": "components", "type": "array", "description": "Issue components"},
            {"name": "created", "type": "datetime", "description": "Creation timestamp"},
            {"name": "updated", "type": "datetime", "description": "Last update timestamp"}
        ]
        
        return fields
    
    def get_default_field_mappings(self) -> List[FieldMapping]:
        """Get default field mappings for Jira to PM33"""
        return [
            FieldMapping("summary", "title", confidence=1.0, is_required=True),
            FieldMapping("description", "description", confidence=1.0),
            FieldMapping("issuetype", "work_item_type", confidence=0.9),
            FieldMapping("status", "status", confidence=1.0),
            FieldMapping("priority", "priority", confidence=0.9),
            FieldMapping("assignee", "assignee", confidence=1.0),
            FieldMapping("project", "project", confidence=1.0, is_required=True),
            FieldMapping("labels", "tags", confidence=0.8),
            FieldMapping("created", "created_at", confidence=1.0),
            FieldMapping("updated", "updated_at", confidence=1.0)
        ]