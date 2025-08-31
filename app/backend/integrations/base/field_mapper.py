"""
PM33 AI-Powered Field Mapping Service
Intelligent field mapping between PM tools and PM33 with confidence scoring
"""

import uuid
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import asyncpg
import aiohttp
from dataclasses import dataclass, asdict
import re

logger = logging.getLogger(__name__)

@dataclass
class FieldMappingSuggestion:
    """AI-generated field mapping suggestion"""
    source_field: str
    target_field: str
    confidence_score: float  # 0.0 to 1.0
    transformation_rule: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    is_required: bool = False
    examples: List[Tuple[str, str]] = None  # (source_value, mapped_value) examples

@dataclass
class FieldAnalysis:
    """Analysis of a source field"""
    field_name: str
    field_type: str
    sample_values: List[str]
    value_patterns: List[str]
    null_percentage: float
    uniqueness_score: float
    semantic_category: str

class AIFieldMapper:
    """
    AI-powered field mapping service for PM tool integrations
    
    Features:
    - Semantic field analysis and categorization
    - AI-powered mapping suggestions with confidence scores
    - Transformation rule generation
    - Mapping validation and testing
    - Learning from user feedback
    """
    
    def __init__(self, database_pool: asyncpg.Pool, ai_service_config: Dict[str, str]):
        self.database_pool = database_pool
        self.ai_service_config = ai_service_config
        self.openai_api_key = ai_service_config.get("openai_api_key")
        self.claude_api_key = ai_service_config.get("claude_api_key")
        
        # PM33 target schema - what fields we want to map to
        self.pm33_target_schema = {
            "work_items": {
                "title": {"type": "string", "required": True, "description": "Work item title/summary"},
                "description": {"type": "text", "required": False, "description": "Detailed description"},
                "work_item_type": {"type": "string", "required": True, "description": "Type of work (Bug, Feature, Task, etc.)"},
                "status": {"type": "string", "required": True, "description": "Current status"},
                "priority": {"type": "string", "required": False, "description": "Priority level"},
                "assignee": {"type": "string", "required": False, "description": "Assigned person"},
                "reporter": {"type": "string", "required": False, "description": "Person who created the item"},
                "project": {"type": "string", "required": True, "description": "Project/workspace identifier"},
                "tags": {"type": "array", "required": False, "description": "Labels or tags"},
                "estimated_effort": {"type": "number", "required": False, "description": "Effort estimate in hours/points"},
                "created_at": {"type": "datetime", "required": True, "description": "Creation timestamp"},
                "updated_at": {"type": "datetime", "required": True, "description": "Last update timestamp"}
            },
            "projects": {
                "name": {"type": "string", "required": True, "description": "Project name"},
                "key": {"type": "string", "required": True, "description": "Unique project identifier"},
                "description": {"type": "text", "required": False, "description": "Project description"},
                "project_type": {"type": "string", "required": False, "description": "Type of project"},
                "lead": {"type": "string", "required": False, "description": "Project lead/owner"},
                "status": {"type": "string", "required": False, "description": "Project status"}
            }
        }
    
    async def analyze_source_fields(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        integration_type: str,
        sample_data: List[Dict[str, Any]]
    ) -> List[FieldAnalysis]:
        """
        Analyze source fields from PM tool data
        """
        field_analyses = []
        
        if not sample_data:
            return field_analyses
        
        # Get all unique fields across samples
        all_fields = set()
        for record in sample_data:
            all_fields.update(record.keys())
        
        # Analyze each field
        for field_name in all_fields:
            analysis = await self._analyze_single_field(field_name, sample_data)
            field_analyses.append(analysis)
        
        return field_analyses
    
    async def _analyze_single_field(
        self,
        field_name: str,
        sample_data: List[Dict[str, Any]]
    ) -> FieldAnalysis:
        """Analyze a single field across sample data"""
        
        values = []
        null_count = 0
        
        for record in sample_data:
            value = record.get(field_name)
            if value is None or value == "":
                null_count += 1
            else:
                values.append(str(value))
        
        # Basic statistics
        total_count = len(sample_data)
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        unique_values = set(values)
        uniqueness_score = len(unique_values) / len(values) if values else 0
        
        # Sample values (up to 5 examples)
        sample_values = list(unique_values)[:5]
        
        # Detect patterns
        patterns = self._detect_value_patterns(values)
        
        # Determine field type
        field_type = self._determine_field_type(values)
        
        # Semantic categorization
        semantic_category = self._categorize_field_semantically(field_name, values)
        
        return FieldAnalysis(
            field_name=field_name,
            field_type=field_type,
            sample_values=sample_values,
            value_patterns=patterns,
            null_percentage=null_percentage,
            uniqueness_score=uniqueness_score,
            semantic_category=semantic_category
        )
    
    def _detect_value_patterns(self, values: List[str]) -> List[str]:
        """Detect common patterns in field values"""
        patterns = []
        
        if not values:
            return patterns
        
        # Email pattern
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if any(email_pattern.match(v) for v in values[:10]):
            patterns.append("email")
        
        # Date pattern
        date_patterns = [
            re.compile(r'^\d{4}-\d{2}-\d{2}'),  # ISO date
            re.compile(r'^\d{1,2}/\d{1,2}/\d{4}'),  # US date
            re.compile(r'^\d{1,2}-\d{1,2}-\d{4}'),  # EU date
        ]
        if any(any(pattern.match(v) for pattern in date_patterns) for v in values[:10]):
            patterns.append("date")
        
        # URL pattern
        url_pattern = re.compile(r'^https?://')
        if any(url_pattern.match(v) for v in values[:10]):
            patterns.append("url")
        
        # ID pattern (alphanumeric codes)
        id_pattern = re.compile(r'^[A-Z]+-\d+$')  # Like JIRA-123
        if any(id_pattern.match(v) for v in values[:10]):
            patterns.append("id_code")
        
        # Number pattern
        if all(v.replace('.', '').replace('-', '').isdigit() for v in values[:10] if v):
            patterns.append("numeric")
        
        return patterns
    
    def _determine_field_type(self, values: List[str]) -> str:
        """Determine the data type of a field"""
        if not values:
            return "unknown"
        
        # Check if all values are numeric
        try:
            [float(v) for v in values[:10] if v]
            return "number"
        except ValueError:
            pass
        
        # Check if values look like booleans
        boolean_values = {"true", "false", "yes", "no", "1", "0", "on", "off"}
        if all(v.lower() in boolean_values for v in values[:10] if v):
            return "boolean"
        
        # Check if values look like dates
        date_keywords = ["date", "time", "created", "updated", "modified"]
        if any(keyword in " ".join(values[:10]).lower() for keyword in date_keywords):
            return "datetime"
        
        # Check text length to distinguish string vs text
        avg_length = sum(len(v) for v in values[:10]) / len([v for v in values[:10] if v]) if values else 0
        if avg_length > 100:
            return "text"
        else:
            return "string"
    
    def _categorize_field_semantically(self, field_name: str, values: List[str]) -> str:
        """Categorize field based on semantic meaning"""
        field_lower = field_name.lower()
        
        # Identity fields
        if any(keyword in field_lower for keyword in ["id", "key", "identifier", "uuid"]):
            return "identity"
        
        # Title/name fields
        if any(keyword in field_lower for keyword in ["title", "name", "summary", "subject"]):
            return "title"
        
        # Description fields
        if any(keyword in field_lower for keyword in ["description", "body", "content", "detail"]):
            return "description"
        
        # Status/state fields
        if any(keyword in field_lower for keyword in ["status", "state", "stage", "phase"]):
            return "status"
        
        # Priority fields
        if any(keyword in field_lower for keyword in ["priority", "severity", "urgency", "importance"]):
            return "priority"
        
        # People fields
        if any(keyword in field_lower for keyword in ["assignee", "owner", "reporter", "creator", "author"]):
            return "person"
        
        # Time fields
        if any(keyword in field_lower for keyword in ["created", "updated", "modified", "date", "time"]):
            return "timestamp"
        
        # Classification fields
        if any(keyword in field_lower for keyword in ["type", "category", "kind", "class"]):
            return "classification"
        
        # Effort/size fields
        if any(keyword in field_lower for keyword in ["points", "estimate", "effort", "hours", "size"]):
            return "effort"
        
        # Tags/labels
        if any(keyword in field_lower for keyword in ["tag", "label", "component"]):
            return "tags"
        
        return "other"
    
    async def generate_mapping_suggestions(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        integration_type: str,
        field_analyses: List[FieldAnalysis],
        target_entity: str = "work_items"
    ) -> List[FieldMappingSuggestion]:
        """
        Generate AI-powered field mapping suggestions
        """
        suggestions = []
        
        # Get target schema for the entity
        target_schema = self.pm33_target_schema.get(target_entity, {})
        
        # Rule-based mapping first (high confidence)
        rule_based_suggestions = self._generate_rule_based_mappings(field_analyses, target_schema)
        suggestions.extend(rule_based_suggestions)
        
        # AI-powered mapping for unmapped fields
        unmapped_fields = [
            fa for fa in field_analyses 
            if not any(s.source_field == fa.field_name for s in suggestions)
        ]
        
        if unmapped_fields and (self.openai_api_key or self.claude_api_key):
            ai_suggestions = await self._generate_ai_mappings(
                unmapped_fields, 
                target_schema, 
                integration_type
            )
            suggestions.extend(ai_suggestions)
        
        # Store suggestions in database
        await self._store_mapping_suggestions(tenant_id, integration_id, suggestions)
        
        return suggestions
    
    def _generate_rule_based_mappings(
        self,
        field_analyses: List[FieldAnalysis],
        target_schema: Dict[str, Any]
    ) -> List[FieldMappingSuggestion]:
        """Generate high-confidence rule-based mappings"""
        suggestions = []
        
        # Define mapping rules based on field names and semantics
        mapping_rules = {
            # Title/Summary mappings
            "title": ["summary", "title", "subject", "name", "heading"],
            "description": ["description", "body", "content", "details", "notes"],
            "status": ["status", "state", "stage", "phase"],
            "priority": ["priority", "severity", "urgency", "importance"],
            "work_item_type": ["type", "issuetype", "kind", "category", "item_type"],
            "assignee": ["assignee", "assigned_to", "owner", "responsible"],
            "reporter": ["reporter", "creator", "author", "created_by"],
            "project": ["project", "workspace", "board", "repo", "repository"],
            "tags": ["labels", "tags", "components", "categories"],
            "estimated_effort": ["story_points", "points", "estimate", "effort", "hours"],
            "created_at": ["created", "created_at", "creation_date", "date_created"],
            "updated_at": ["updated", "updated_at", "modified", "last_modified"]
        }
        
        for target_field, source_patterns in mapping_rules.items():
            if target_field not in target_schema:
                continue
                
            # Find matching source field
            for field_analysis in field_analyses:
                field_name_lower = field_analysis.field_name.lower()
                
                # Check for exact or partial matches
                for pattern in source_patterns:
                    if pattern in field_name_lower or field_name_lower in pattern:
                        confidence = self._calculate_rule_based_confidence(
                            field_analysis, pattern, target_field
                        )
                        
                        if confidence > 0.7:  # High confidence threshold
                            suggestions.append(FieldMappingSuggestion(
                                source_field=field_analysis.field_name,
                                target_field=target_field,
                                confidence_score=confidence,
                                reasoning=f"Rule-based match: '{pattern}' pattern",
                                is_required=target_schema[target_field].get("required", False)
                            ))
                            break  # Only map to first high-confidence match
        
        return suggestions
    
    def _calculate_rule_based_confidence(
        self,
        field_analysis: FieldAnalysis,
        pattern: str,
        target_field: str
    ) -> float:
        """Calculate confidence score for rule-based mapping"""
        base_confidence = 0.8
        
        # Exact match gets higher confidence
        if field_analysis.field_name.lower() == pattern:
            base_confidence = 0.95
        
        # Adjust based on field characteristics
        if field_analysis.null_percentage > 50:
            base_confidence -= 0.1  # High null rate reduces confidence
        
        if field_analysis.semantic_category == "other":
            base_confidence -= 0.1  # Unknown semantic category
        
        # Type compatibility check
        expected_types = {
            "title": ["string"],
            "description": ["text", "string"],
            "status": ["string"],
            "created_at": ["datetime"],
            "estimated_effort": ["number"]
        }
        
        if target_field in expected_types:
            if field_analysis.field_type not in expected_types[target_field]:
                base_confidence -= 0.2
        
        return max(0.0, min(1.0, base_confidence))
    
    async def _generate_ai_mappings(
        self,
        unmapped_fields: List[FieldAnalysis],
        target_schema: Dict[str, Any],
        integration_type: str
    ) -> List[FieldMappingSuggestion]:
        """Generate AI-powered mapping suggestions"""
        suggestions = []
        
        # Prepare context for AI
        context = {
            "integration_type": integration_type,
            "unmapped_fields": [asdict(fa) for fa in unmapped_fields],
            "target_schema": target_schema,
            "task": "field_mapping"
        }
        
        try:
            # Use OpenAI for structured field mapping
            if self.openai_api_key:
                ai_mappings = await self._call_openai_field_mapping(context)
                suggestions.extend(ai_mappings)
            
        except Exception as e:
            logger.error(f"AI mapping generation failed: {str(e)}")
        
        return suggestions
    
    async def _call_openai_field_mapping(self, context: Dict[str, Any]) -> List[FieldMappingSuggestion]:
        """Call OpenAI API for field mapping suggestions"""
        suggestions = []
        
        prompt = self._build_field_mapping_prompt(context)
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert in data integration and field mapping for project management tools. Provide accurate field mappings with confidence scores."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        suggestions = self._parse_ai_mapping_response(content)
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
        
        return suggestions
    
    def _build_field_mapping_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for AI field mapping"""
        return f"""
        I need help mapping fields from a {context['integration_type']} integration to our PM33 schema.

        Source fields to map:
        {json.dumps(context['unmapped_fields'], indent=2)}

        Target PM33 schema:
        {json.dumps(context['target_schema'], indent=2)}

        Please suggest field mappings in this JSON format:
        {{
            "mappings": [
                {{
                    "source_field": "source_field_name",
                    "target_field": "target_field_name", 
                    "confidence_score": 0.85,
                    "reasoning": "Explanation for this mapping",
                    "transformation_rule": {{"type": "direct"}} // if transformation needed
                }}
            ]
        }}

        Rules:
        1. Only suggest mappings with confidence >= 0.6
        2. Consider field names, types, and semantic meaning
        3. Provide clear reasoning for each mapping
        4. Include transformation rules if needed
        5. Don't force mappings - only suggest good matches
        """
    
    def _parse_ai_mapping_response(self, response: str) -> List[FieldMappingSuggestion]:
        """Parse AI response into field mapping suggestions"""
        suggestions = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                for mapping in data.get("mappings", []):
                    suggestions.append(FieldMappingSuggestion(
                        source_field=mapping["source_field"],
                        target_field=mapping["target_field"],
                        confidence_score=mapping["confidence_score"],
                        reasoning=mapping.get("reasoning"),
                        transformation_rule=mapping.get("transformation_rule")
                    ))
                    
        except Exception as e:
            logger.error(f"Failed to parse AI mapping response: {str(e)}")
        
        return suggestions
    
    async def _store_mapping_suggestions(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        suggestions: List[FieldMappingSuggestion]
    ):
        """Store mapping suggestions in database"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                for suggestion in suggestions:
                    await connection.execute(
                        """
                        INSERT INTO integration_field_mappings (
                            tenant_id, integration_id, source_field, target_field,
                            transformation_rule, confidence_score, is_ai_suggested,
                            is_required
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (tenant_id, integration_id, source_field, target_field) 
                        DO UPDATE SET
                            confidence_score = EXCLUDED.confidence_score,
                            is_ai_suggested = EXCLUDED.is_ai_suggested,
                            updated_at = NOW()
                        """,
                        tenant_id,
                        integration_id,
                        suggestion.source_field,
                        suggestion.target_field,
                        suggestion.transformation_rule or {},
                        suggestion.confidence_score,
                        suggestion.reasoning is not None,  # AI-suggested if has reasoning
                        suggestion.is_required
                    )
                    
        except Exception as e:
            logger.error(f"Failed to store mapping suggestions: {str(e)}")
    
    async def validate_mappings(
        self,
        tenant_id: uuid.UUID,
        integration_id: uuid.UUID,
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate field mappings against test data"""
        validation_results = {
            "total_mappings": 0,
            "successful_mappings": 0,
            "failed_mappings": 0,
            "mapping_details": []
        }
        
        try:
            # Get stored mappings
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(tenant_id)
                )
                
                mappings = await connection.fetch(
                    """
                    SELECT source_field, target_field, transformation_rule, confidence_score
                    FROM integration_field_mappings
                    WHERE tenant_id = $1 AND integration_id = $2
                    AND is_user_approved = true
                    """,
                    tenant_id,
                    integration_id
                )
                
                validation_results["total_mappings"] = len(mappings)
                
                # Test each mapping
                for mapping in mappings:
                    success_count = 0
                    total_tests = min(len(test_data), 10)  # Test on up to 10 records
                    
                    for record in test_data[:total_tests]:
                        source_value = record.get(mapping["source_field"])
                        if source_value is not None:
                            # Apply transformation if any
                            try:
                                transformed_value = self._apply_transformation(
                                    source_value,
                                    mapping["transformation_rule"]
                                )
                                success_count += 1
                            except Exception:
                                pass  # Transformation failed
                    
                    success_rate = success_count / total_tests if total_tests > 0 else 0
                    
                    mapping_detail = {
                        "source_field": mapping["source_field"],
                        "target_field": mapping["target_field"],
                        "confidence_score": float(mapping["confidence_score"]),
                        "success_rate": success_rate,
                        "tests_run": total_tests
                    }
                    
                    validation_results["mapping_details"].append(mapping_detail)
                    
                    if success_rate > 0.8:
                        validation_results["successful_mappings"] += 1
                    else:
                        validation_results["failed_mappings"] += 1
                        
        except Exception as e:
            logger.error(f"Mapping validation failed: {str(e)}")
        
        return validation_results
    
    def _apply_transformation(self, value: Any, transformation_rule: Dict[str, Any]) -> Any:
        """Apply transformation rule to a value"""
        if not transformation_rule:
            return value
        
        transform_type = transformation_rule.get("type", "direct")
        
        if transform_type == "direct":
            return value
        elif transform_type == "lowercase":
            return str(value).lower()
        elif transform_type == "uppercase":
            return str(value).upper()
        elif transform_type == "extract_email":
            match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(value))
            return match.group(0) if match else None
        elif transform_type == "split_first":
            parts = str(value).split(transformation_rule.get("delimiter", " "))
            return parts[0] if parts else None
        
        return value