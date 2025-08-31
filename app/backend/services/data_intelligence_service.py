"""
PM33 Data Intelligence Service
Connects PM tool integration data to AI engines for strategic analysis
"""

import asyncio
import logging
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
import asyncpg
import numpy as np

from ..ai_engine_manager import AIEngineManager

logger = logging.getLogger(__name__)

@dataclass
class ProjectInsight:
    """Strategic insight about a project"""
    project_id: str
    project_name: str
    strategic_impact_score: float  # 0.0 to 1.0
    health_score: float  # 0.0 to 1.0
    velocity_trend: str  # 'accelerating', 'stable', 'declining'
    key_insights: List[str]
    risk_factors: List[str]
    recommendations: List[str]

@dataclass
class WorkItemAnalysis:
    """AI analysis of work items"""
    item_id: str
    title: str
    strategic_priority: str  # 'critical', 'high', 'medium', 'low'
    complexity_score: float  # 0.0 to 1.0
    urgency_score: float  # 0.0 to 1.0
    business_value: str  # 'high', 'medium', 'low'
    blockers_detected: List[str]
    suggested_actions: List[str]

@dataclass
class TeamProductivity:
    """Team productivity analysis"""
    team_name: str
    members: List[str]
    velocity_score: float  # 0.0 to 1.0
    collaboration_score: float  # 0.0 to 1.0
    efficiency_trends: Dict[str, float]
    improvement_areas: List[str]

class DataIntelligenceService:
    """
    Transforms PM tool data into strategic intelligence using multi-AI analysis
    
    Features:
    - Real-time analysis of synced PM tool data
    - Strategic impact scoring for projects and work items
    - Team productivity and collaboration insights
    - Predictive risk detection and recommendations
    - Cross-project pattern recognition
    """
    
    def __init__(self, database_pool: asyncpg.Pool):
        self.database_pool = database_pool
        self.ai_manager = AIEngineManager()
        self.analysis_cache: Dict[str, Any] = {}  # TTL cache for expensive analyses
        
    async def analyze_tenant_portfolio(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Comprehensive strategic analysis of tenant's PM portfolio"""
        logger.info(f"Starting portfolio analysis for tenant {tenant_id}")
        
        try:
            # Get all integration data for tenant
            integration_data = await self._get_tenant_integration_data(tenant_id)
            
            if not integration_data['projects']:
                return self._create_empty_portfolio_analysis()
            
            # Multi-dimensional analysis
            project_insights = await self._analyze_projects(integration_data['projects'], integration_data['work_items'])
            team_productivity = await self._analyze_team_productivity(integration_data['users'], integration_data['work_items'])
            strategic_recommendations = await self._generate_strategic_recommendations(project_insights, team_productivity, integration_data)
            portfolio_health = await self._calculate_portfolio_health(project_insights)
            
            # Compile comprehensive analysis
            portfolio_analysis = {
                'tenant_id': str(tenant_id),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'portfolio_health': portfolio_health,
                'project_insights': [asdict(insight) for insight in project_insights],
                'team_productivity': [asdict(team) for team in team_productivity],
                'strategic_recommendations': strategic_recommendations,
                'key_metrics': {
                    'total_projects': len(integration_data['projects']),
                    'active_work_items': len([item for item in integration_data['work_items'] if item['status'] not in ['Done', 'Closed', 'Resolved']]),
                    'team_members': len(integration_data['users']),
                    'avg_project_health': np.mean([p.health_score for p in project_insights]) if project_insights else 0,
                    'high_impact_projects': len([p for p in project_insights if p.strategic_impact_score > 0.7]),
                    'at_risk_projects': len([p for p in project_insights if p.health_score < 0.4])
                },
                'data_freshness': {
                    'last_sync': integration_data.get('last_sync_time', 'Unknown'),
                    'data_sources': integration_data.get('integration_types', []),
                    'total_integrations': len(integration_data.get('integration_types', []))
                }
            }
            
            # Store analysis for historical tracking
            await self._store_portfolio_analysis(tenant_id, portfolio_analysis)
            
            return portfolio_analysis
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed for tenant {tenant_id}: {str(e)}")
            raise
    
    async def _get_tenant_integration_data(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Fetch all integration data for a tenant"""
        async with self.database_pool.acquire() as connection:
            await connection.execute(
                "SELECT set_config('app.current_tenant_id', $1, false)",
                str(tenant_id)
            )
            
            # Get projects
            projects = await connection.fetch("""
                SELECT p.*, ti.integration_type, ti.integration_name, ti.last_sync_at
                FROM integration_projects p
                JOIN tenant_integrations ti ON p.integration_id = ti.id
                WHERE p.tenant_id = $1 AND p.status = 'active'
                ORDER BY p.updated_at DESC
            """, tenant_id)
            
            # Get work items
            work_items = await connection.fetch("""
                SELECT w.*, ti.integration_type, p.name as project_name
                FROM integration_work_items w
                JOIN tenant_integrations ti ON w.integration_id = ti.id
                LEFT JOIN integration_projects p ON w.project_id = p.id
                WHERE w.tenant_id = $1
                ORDER BY w.updated_at DESC
                LIMIT 1000
            """, tenant_id)
            
            # Get users
            users = await connection.fetch("""
                SELECT u.*, ti.integration_type
                FROM integration_users u
                JOIN tenant_integrations ti ON u.integration_id = ti.id
                WHERE u.tenant_id = $1 AND u.is_active = true
            """, tenant_id)
            
            # Get integration types and sync status
            integrations = await connection.fetch("""
                SELECT integration_type, integration_name, last_sync_at, status
                FROM tenant_integrations
                WHERE tenant_id = $1 AND status = 'active'
            """, tenant_id)
            
            return {
                'projects': [dict(p) for p in projects],
                'work_items': [dict(w) for w in work_items],
                'users': [dict(u) for u in users],
                'integration_types': [i['integration_type'] for i in integrations],
                'last_sync_time': max([i['last_sync_at'] for i in integrations if i['last_sync_at']], default=None)
            }
    
    async def _analyze_projects(self, projects: List[Dict], work_items: List[Dict]) -> List[ProjectInsight]:
        """AI-powered analysis of projects"""
        project_insights = []
        
        for project in projects:
            # Get work items for this project
            project_work_items = [item for item in work_items if item.get('project_id') == project['id']]
            
            # Calculate basic metrics
            total_items = len(project_work_items)
            completed_items = len([item for item in project_work_items if item['status'] in ['Done', 'Closed', 'Resolved']])
            in_progress_items = len([item for item in project_work_items if item['status'] in ['In Progress', 'In Development', 'Active']])
            
            completion_rate = completed_items / total_items if total_items > 0 else 0
            active_work_ratio = in_progress_items / total_items if total_items > 0 else 0
            
            # AI analysis of project health and strategic impact
            project_context = self._build_project_context(project, project_work_items)
            ai_analysis = await self._get_ai_project_analysis(project_context)
            
            # Calculate health score
            health_score = self._calculate_project_health_score(completion_rate, active_work_ratio, project_work_items, ai_analysis)
            
            # Determine velocity trend
            velocity_trend = self._analyze_velocity_trend(project_work_items)
            
            insight = ProjectInsight(
                project_id=project['id'],
                project_name=project['name'],
                strategic_impact_score=ai_analysis.get('strategic_impact_score', 0.5),
                health_score=health_score,
                velocity_trend=velocity_trend,
                key_insights=ai_analysis.get('key_insights', []),
                risk_factors=ai_analysis.get('risk_factors', []),
                recommendations=ai_analysis.get('recommendations', [])
            )
            
            project_insights.append(insight)
        
        return project_insights
    
    def _build_project_context(self, project: Dict, work_items: List[Dict]) -> str:
        """Build context string for AI analysis"""
        context_parts = [
            f"Project: {project['name']}",
            f"Description: {project.get('description', 'No description available')}",
            f"Type: {project.get('project_type', 'Unknown')}",
            f"Lead: {project.get('lead_name', 'Not assigned')}",
            f"Total work items: {len(work_items)}",
        ]
        
        # Add work item statistics
        if work_items:
            statuses = {}
            priorities = {}
            types = {}
            
            for item in work_items:
                statuses[item['status']] = statuses.get(item['status'], 0) + 1
                priorities[item.get('priority', 'None')] = priorities.get(item.get('priority', 'None'), 0) + 1
                types[item['work_item_type']] = types.get(item['work_item_type'], 0) + 1
            
            context_parts.extend([
                f"Work item statuses: {dict(statuses)}",
                f"Priority distribution: {dict(priorities)}",
                f"Work item types: {dict(types)}"
            ])
            
            # Add recent high-priority items
            high_priority_items = [item for item in work_items if item.get('priority') in ['Critical', 'High', 'Highest']][:5]
            if high_priority_items:
                context_parts.append("Recent high-priority items:")
                for item in high_priority_items:
                    context_parts.append(f"- {item['title']} ({item['status']})")
        
        return "\n".join(context_parts)
    
    async def _get_ai_project_analysis(self, project_context: str) -> Dict[str, Any]:
        """Get AI analysis of project using multi-engine system"""
        analysis_prompt = f"""
        Analyze this PM project data and provide strategic insights:

        {project_context}

        Please provide:
        1. Strategic impact score (0.0 to 1.0) - how critical is this project to business success?
        2. Key insights (3-4 bullet points about project state)
        3. Risk factors (2-3 potential issues or concerns)
        4. Recommendations (2-3 actionable next steps)

        Respond in JSON format:
        {{
            "strategic_impact_score": 0.0-1.0,
            "key_insights": ["insight1", "insight2", "insight3"],
            "risk_factors": ["risk1", "risk2"],
            "recommendations": ["rec1", "rec2", "rec3"]
        }}
        """
        
        try:
            # Use AI Engine Manager for intelligent analysis
            ai_response = self.ai_manager.get_strategic_response(
                analysis_prompt, 
                context="Project portfolio analysis for strategic decision-making"
            )
            
            # Extract JSON from AI response
            response_text = ai_response.get('response', '{}')
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                else:
                    # Fallback parsing
                    analysis_result = self._parse_ai_analysis_fallback(response_text)
            except json.JSONDecodeError:
                analysis_result = self._parse_ai_analysis_fallback(response_text)
            
            # Validate and normalize
            return self._validate_project_analysis(analysis_result)
            
        except Exception as e:
            logger.warning(f"AI project analysis failed: {str(e)}, using fallback")
            return self._create_fallback_project_analysis(project_context)
    
    def _parse_ai_analysis_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        lines = response_text.split('\n')
        
        # Extract insights, risks, and recommendations from text
        insights = []
        risks = []
        recommendations = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if 'insight' in line.lower():
                current_section = 'insights'
            elif 'risk' in line.lower():
                current_section = 'risks'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif line.startswith(('-', '•', '*')) or line[0:2].isdigit():
                clean_line = line.strip('-•* ').strip('1234567890. ')
                if len(clean_line) > 10:  # Meaningful content
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'risks':
                        risks.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)
        
        # Calculate strategic impact based on keywords
        impact_keywords = ['critical', 'important', 'strategic', 'key', 'essential', 'vital']
        impact_score = 0.5  # Default
        for keyword in impact_keywords:
            if keyword in response_text.lower():
                impact_score = min(impact_score + 0.1, 1.0)
        
        return {
            'strategic_impact_score': impact_score,
            'key_insights': insights[:4],
            'risk_factors': risks[:3],
            'recommendations': recommendations[:3]
        }
    
    def _validate_project_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize AI analysis results"""
        validated = {
            'strategic_impact_score': max(0.0, min(1.0, analysis.get('strategic_impact_score', 0.5))),
            'key_insights': analysis.get('key_insights', [])[:4],
            'risk_factors': analysis.get('risk_factors', [])[:3],
            'recommendations': analysis.get('recommendations', [])[:3]
        }
        
        # Ensure we have minimum content
        if not validated['key_insights']:
            validated['key_insights'] = ['Project analysis completed', 'Strategic assessment in progress']
        
        if not validated['risk_factors']:
            validated['risk_factors'] = ['Monitor for potential blockers', 'Track resource allocation']
        
        if not validated['recommendations']:
            validated['recommendations'] = ['Continue current execution', 'Regular status reviews']
        
        return validated
    
    def _create_fallback_project_analysis(self, project_context: str) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        return {
            'strategic_impact_score': 0.6,  # Moderate impact default
            'key_insights': [
                'Project data successfully captured from PM tool',
                'Multi-dimensional analysis framework applied',
                'Strategic context integrated for decision-making'
            ],
            'risk_factors': [
                'Requires ongoing monitoring and adjustment',
                'Dependencies on external factors may impact timeline'
            ],
            'recommendations': [
                'Maintain regular team communication and updates',
                'Continue tracking progress against strategic objectives',
                'Review and adjust priorities based on changing business needs'
            ]
        }
    
    def _calculate_project_health_score(self, completion_rate: float, active_work_ratio: float, 
                                      work_items: List[Dict], ai_analysis: Dict) -> float:
        """Calculate comprehensive project health score"""
        # Base score from completion metrics
        base_score = completion_rate * 0.4 + min(active_work_ratio * 2, 1.0) * 0.3
        
        # Factor in AI strategic impact
        strategic_factor = ai_analysis.get('strategic_impact_score', 0.5) * 0.2
        
        # Factor in risk assessment
        risk_count = len(ai_analysis.get('risk_factors', []))
        risk_penalty = min(risk_count * 0.05, 0.1)  # Max 10% penalty
        
        # Recent activity factor
        recent_updates = len([item for item in work_items 
                            if item.get('updated_at') and 
                            (datetime.now(timezone.utc) - datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))).days <= 7])
        activity_factor = min(recent_updates / max(len(work_items), 1), 1.0) * 0.1
        
        final_score = base_score + strategic_factor + activity_factor - risk_penalty
        return max(0.0, min(1.0, final_score))
    
    def _analyze_velocity_trend(self, work_items: List[Dict]) -> str:
        """Analyze project velocity trend"""
        if not work_items:
            return 'stable'
        
        # Group by week for trend analysis
        weekly_completions = {}
        for item in work_items:
            if item['status'] in ['Done', 'Closed', 'Resolved'] and item.get('updated_at'):
                try:
                    updated_date = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                    week_key = updated_date.strftime('%Y-W%U')
                    weekly_completions[week_key] = weekly_completions.get(week_key, 0) + 1
                except:
                    continue
        
        if len(weekly_completions) < 2:
            return 'stable'
        
        # Simple trend analysis
        recent_weeks = sorted(weekly_completions.keys())[-3:]  # Last 3 weeks
        if len(recent_weeks) >= 2:
            recent_avg = sum(weekly_completions[week] for week in recent_weeks[-2:]) / 2
            older_avg = sum(weekly_completions[week] for week in recent_weeks[:-2] or recent_weeks[-1:]) / max(len(recent_weeks[:-2]), 1)
            
            if recent_avg > older_avg * 1.2:
                return 'accelerating'
            elif recent_avg < older_avg * 0.8:
                return 'declining'
        
        return 'stable'
    
    async def _analyze_team_productivity(self, users: List[Dict], work_items: List[Dict]) -> List[TeamProductivity]:
        """Analyze team productivity patterns"""
        # Group users by project/team (simplified for demo)
        team_productivity = []
        
        if not users:
            return team_productivity
        
        # Create a general team analysis
        active_members = [user['display_name'] for user in users if user.get('is_active', True)]
        
        # Calculate team velocity based on work item assignments
        team_work_items = [item for item in work_items if item.get('assignee_name') in active_members]
        completed_items = len([item for item in team_work_items if item['status'] in ['Done', 'Closed', 'Resolved']])
        
        velocity_score = min(completed_items / max(len(team_work_items), 1), 1.0) if team_work_items else 0.5
        collaboration_score = min(len(set(item.get('assignee_name') for item in team_work_items if item.get('assignee_name'))) / max(len(active_members), 1), 1.0)
        
        productivity = TeamProductivity(
            team_name='Integrated PM Team',
            members=active_members,
            velocity_score=velocity_score,
            collaboration_score=collaboration_score,
            efficiency_trends={'weekly_completion': velocity_score, 'collaboration_index': collaboration_score},
            improvement_areas=self._identify_improvement_areas(velocity_score, collaboration_score, work_items)
        )
        
        team_productivity.append(productivity)
        
        return team_productivity
    
    def _identify_improvement_areas(self, velocity_score: float, collaboration_score: float, work_items: List[Dict]) -> List[str]:
        """Identify team improvement opportunities"""
        improvements = []
        
        if velocity_score < 0.6:
            improvements.append('Increase delivery velocity and completion rate')
        
        if collaboration_score < 0.5:
            improvements.append('Enhance cross-team collaboration and work distribution')
        
        # Check for bottlenecks in work item statuses
        status_counts = {}
        for item in work_items:
            status_counts[item['status']] = status_counts.get(item['status'], 0) + 1
        
        blocked_items = status_counts.get('Blocked', 0) + status_counts.get('On Hold', 0)
        if blocked_items > len(work_items) * 0.1:  # More than 10% blocked
            improvements.append('Address workflow bottlenecks and blocked items')
        
        if not improvements:
            improvements.append('Maintain current performance and explore optimization opportunities')
        
        return improvements
    
    async def _generate_strategic_recommendations(self, project_insights: List[ProjectInsight], 
                                               team_productivity: List[TeamProductivity],
                                               integration_data: Dict) -> List[Dict[str, Any]]:
        """Generate strategic recommendations using AI analysis"""
        
        # Build comprehensive context for AI recommendations
        context = self._build_strategic_context(project_insights, team_productivity, integration_data)
        
        recommendation_prompt = f"""
        Based on this PM portfolio analysis, provide strategic recommendations:

        {context}

        Please provide 4-6 strategic recommendations in this JSON format:
        {{
            "recommendations": [
                {{
                    "category": "strategic|operational|tactical",
                    "priority": "high|medium|low", 
                    "title": "Recommendation Title",
                    "description": "Detailed recommendation",
                    "expected_impact": "Description of expected outcome",
                    "implementation_effort": "low|medium|high",
                    "timeline": "immediate|1-2 weeks|1-2 months"
                }}
            ]
        }}
        """
        
        try:
            ai_response = self.ai_manager.get_strategic_response(recommendation_prompt, "Strategic portfolio analysis")
            response_text = ai_response.get('response', '{}')
            
            # Extract recommendations
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                recommendations_data = json.loads(json_match.group())
                return recommendations_data.get('recommendations', [])
            
        except Exception as e:
            logger.warning(f"AI recommendations failed: {str(e)}, using fallback")
        
        # Fallback recommendations
        return self._generate_fallback_recommendations(project_insights, team_productivity)
    
    def _build_strategic_context(self, project_insights: List[ProjectInsight], 
                               team_productivity: List[TeamProductivity],
                               integration_data: Dict) -> str:
        """Build strategic context for AI recommendations"""
        context_parts = [
            f"Portfolio Overview: {len(project_insights)} active projects from {len(integration_data.get('integration_types', []))} PM tools",
            f"Team Size: {len(integration_data.get('users', []))} active team members",
            f"Active Work Items: {integration_data.get('total_work_items', 0)}"
        ]
        
        # High-impact projects
        high_impact = [p for p in project_insights if p.strategic_impact_score > 0.7]
        if high_impact:
            context_parts.append(f"High-Impact Projects ({len(high_impact)}):")
            for project in high_impact[:3]:
                context_parts.append(f"- {project.project_name}: Health {project.health_score:.1f}, Trend: {project.velocity_trend}")
        
        # At-risk projects
        at_risk = [p for p in project_insights if p.health_score < 0.4]
        if at_risk:
            context_parts.append(f"At-Risk Projects ({len(at_risk)}):")
            for project in at_risk:
                context_parts.append(f"- {project.project_name}: Health {project.health_score:.1f}")
        
        # Team productivity summary
        if team_productivity:
            team = team_productivity[0]
            context_parts.append(f"Team Productivity: Velocity {team.velocity_score:.1f}, Collaboration {team.collaboration_score:.1f}")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_recommendations(self, project_insights: List[ProjectInsight], 
                                         team_productivity: List[TeamProductivity]) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when AI fails"""
        recommendations = []
        
        # Portfolio health recommendation
        avg_health = np.mean([p.health_score for p in project_insights]) if project_insights else 0.5
        if avg_health < 0.6:
            recommendations.append({
                'category': 'strategic',
                'priority': 'high',
                'title': 'Improve Portfolio Health',
                'description': 'Several projects show declining health scores. Focus on addressing bottlenecks and resource allocation.',
                'expected_impact': 'Increased delivery predictability and team satisfaction',
                'implementation_effort': 'medium',
                'timeline': '1-2 weeks'
            })
        
        # Team productivity recommendation
        if team_productivity and team_productivity[0].velocity_score < 0.5:
            recommendations.append({
                'category': 'operational',
                'priority': 'high',
                'title': 'Optimize Team Velocity',
                'description': 'Team velocity is below optimal levels. Review workflow processes and remove impediments.',
                'expected_impact': 'Faster delivery cycles and improved throughput',
                'implementation_effort': 'medium',
                'timeline': '1-2 weeks'
            })
        
        # Always include strategic planning recommendation
        recommendations.append({
            'category': 'strategic',
            'priority': 'medium',
            'title': 'Regular Strategic Reviews',
            'description': 'Implement weekly strategic reviews using PM33 data intelligence for proactive decision-making.',
            'expected_impact': 'Enhanced strategic alignment and faster course corrections',
            'implementation_effort': 'low',
            'timeline': 'immediate'
        })
        
        return recommendations
    
    async def _calculate_portfolio_health(self, project_insights: List[ProjectInsight]) -> Dict[str, Any]:
        """Calculate overall portfolio health metrics"""
        if not project_insights:
            return {
                'overall_score': 0.5,
                'health_distribution': {'healthy': 0, 'at_risk': 0, 'critical': 0},
                'strategic_alignment': 0.5,
                'velocity_trend': 'unknown'
            }
        
        overall_score = np.mean([p.health_score for p in project_insights])
        strategic_alignment = np.mean([p.strategic_impact_score for p in project_insights])
        
        health_distribution = {
            'healthy': len([p for p in project_insights if p.health_score >= 0.7]),
            'at_risk': len([p for p in project_insights if 0.4 <= p.health_score < 0.7]),
            'critical': len([p for p in project_insights if p.health_score < 0.4])
        }
        
        # Overall velocity trend
        trend_counts = {}
        for project in project_insights:
            trend_counts[project.velocity_trend] = trend_counts.get(project.velocity_trend, 0) + 1
        
        dominant_trend = max(trend_counts.keys(), key=lambda k: trend_counts[k]) if trend_counts else 'stable'
        
        return {
            'overall_score': overall_score,
            'health_distribution': health_distribution,
            'strategic_alignment': strategic_alignment,
            'velocity_trend': dominant_trend,
            'total_projects': len(project_insights)
        }
    
    def _create_empty_portfolio_analysis(self) -> Dict[str, Any]:
        """Create analysis structure for empty portfolio"""
        return {
            'portfolio_health': {
                'overall_score': 0.0,
                'health_distribution': {'healthy': 0, 'at_risk': 0, 'critical': 0},
                'strategic_alignment': 0.0,
                'velocity_trend': 'unknown',
                'total_projects': 0
            },
            'project_insights': [],
            'team_productivity': [],
            'strategic_recommendations': [{
                'category': 'strategic',
                'priority': 'high',
                'title': 'Connect PM Tools',
                'description': 'Start by connecting your Jira, Linear, or Monday.com accounts to enable data-driven insights.',
                'expected_impact': 'Unlock strategic intelligence and workflow automation capabilities',
                'implementation_effort': 'low',
                'timeline': 'immediate'
            }],
            'key_metrics': {
                'total_projects': 0,
                'active_work_items': 0,
                'team_members': 0,
                'avg_project_health': 0,
                'high_impact_projects': 0,
                'at_risk_projects': 0
            }
        }
    
    async def _store_portfolio_analysis(self, tenant_id: uuid.UUID, analysis: Dict[str, Any]):
        """Store portfolio analysis for historical tracking"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                await connection.execute("""
                    INSERT INTO portfolio_analyses (
                        tenant_id, analysis_data, portfolio_health_score,
                        total_projects, high_impact_projects, at_risk_projects,
                        created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
                """,
                    tenant_id,
                    json.dumps(analysis),
                    analysis['portfolio_health']['overall_score'],
                    analysis['key_metrics']['total_projects'],
                    analysis['key_metrics']['high_impact_projects'],
                    analysis['key_metrics']['at_risk_projects']
                )
                
        except Exception as e:
            logger.error(f"Failed to store portfolio analysis: {str(e)}")
            # Don't raise - analysis storage failure shouldn't break the main flow