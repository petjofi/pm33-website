"""
PM33 Company Context Learning Service
Builds tenant-specific AI memory using Pinecone vector database and PM tool data
"""

import asyncio
import logging
import uuid
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import asyncpg
import numpy as np

# Vector database imports
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    print("⚠️ Pinecone not available - install with: pip install pinecone-client")
    PINECONE_AVAILABLE = False

# Embedding generation
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️ OpenAI not available for embeddings - install with: pip install openai")
    OPENAI_AVAILABLE = False

from ..ai_engine_manager import AIEngineManager

logger = logging.getLogger(__name__)

@dataclass
class CompanyContext:
    """Company context entry for vector storage"""
    context_id: str
    tenant_id: uuid.UUID
    context_type: str  # project, work_item, user, insight, pattern
    title: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    relevance_score: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class ContextInsight:
    """AI-generated insight from company context"""
    insight_id: str
    tenant_id: uuid.UUID
    insight_type: str  # pattern, trend, opportunity, risk
    title: str
    description: str
    confidence_score: float  # 0.0 to 1.0
    supporting_contexts: List[str]  # Context IDs
    actionable_recommendations: List[str]
    created_at: datetime

class CompanyContextLearning:
    """
    Builds and maintains tenant-specific company context using vector embeddings
    
    Features:
    - Automatic context extraction from PM tool data
    - Vector similarity search for relevant context retrieval
    - AI-powered pattern recognition and insight generation
    - Company-specific memory that improves over time
    - Strategic context for personalized AI team responses
    """
    
    def __init__(self, database_pool: asyncpg.Pool, pinecone_api_key: str = None, openai_api_key: str = None):
        self.database_pool = database_pool
        self.ai_manager = AIEngineManager()
        
        # Pinecone configuration
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_client = None
        self.index_name = "pm33-company-context"
        
        # OpenAI for embeddings
        self.openai_api_key = openai_api_key
        self.openai_client = None
        
        # Context cache
        self.context_cache: Dict[str, CompanyContext] = {}
        self.cache_ttl = 3600  # 1 hour TTL
        
        self.initialize_vector_db()
    
    def initialize_vector_db(self):
        """Initialize Pinecone vector database"""
        if not PINECONE_AVAILABLE or not self.pinecone_api_key:
            logger.warning("Pinecone not available - context learning will use fallback storage")
            return
        
        try:
            # Initialize Pinecone
            self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
            
            # Create index if it doesn't exist
            if self.index_name not in self.pinecone_client.list_indexes().names():
                self.pinecone_client.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI text-embedding-ada-002 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Get index reference
            self.index = self.pinecone_client.Index(self.index_name)
            
            logger.info("✅ Pinecone vector database initialized")
            
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {str(e)}")
            self.pinecone_client = None
        
        # Initialize OpenAI for embeddings
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI client initialized for embeddings")
            except Exception as e:
                logger.error(f"OpenAI initialization failed: {str(e)}")
    
    async def learn_from_integration_data(self, tenant_id: uuid.UUID, integration_data: Dict[str, Any]) -> int:
        """
        Extract and learn company context from PM tool integration data
        Returns number of context entries processed
        """
        logger.info(f"Learning company context for tenant {tenant_id}")
        
        try:
            contexts_processed = 0
            
            # Process projects
            if 'projects' in integration_data:
                for project in integration_data['projects']:
                    context = await self._extract_project_context(tenant_id, project)
                    if context:
                        await self._store_context(context)
                        contexts_processed += 1
            
            # Process work items
            if 'work_items' in integration_data:
                for work_item in integration_data['work_items'][:50]:  # Limit for demo
                    context = await self._extract_work_item_context(tenant_id, work_item)
                    if context:
                        await self._store_context(context)
                        contexts_processed += 1
            
            # Generate insights from learned contexts
            await self._generate_context_insights(tenant_id)
            
            logger.info(f"Processed {contexts_processed} context entries for tenant {tenant_id}")
            return contexts_processed
            
        except Exception as e:
            logger.error(f"Context learning failed for tenant {tenant_id}: {str(e)}")
            return 0
    
    async def _extract_project_context(self, tenant_id: uuid.UUID, project: Dict[str, Any]) -> Optional[CompanyContext]:
        """Extract context from project data"""
        try:
            # Build rich context content
            context_parts = [
                f"Project: {project.get('name', 'Unknown')}",
                f"Description: {project.get('description', 'No description')}",
                f"Type: {project.get('project_type', 'Unknown')}",
                f"Lead: {project.get('lead_name', 'Not assigned')}",
                f"Integration: {project.get('integration_type', 'unknown')} tool"
            ]
            
            # Add strategic context if available
            if project.get('ai_summary'):
                context_parts.append(f"AI Summary: {project['ai_summary']}")
            
            if project.get('strategic_context'):
                strategic_data = project['strategic_context']
                if isinstance(strategic_data, dict):
                    for key, value in strategic_data.items():
                        context_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            
            content = "\n".join(context_parts)
            
            return CompanyContext(
                context_id=f"project_{project['id']}",
                tenant_id=tenant_id,
                context_type="project",
                title=project.get('name', 'Unnamed Project'),
                content=content,
                metadata={
                    'project_id': project['id'],
                    'integration_type': project.get('integration_type'),
                    'project_type': project.get('project_type'),
                    'lead': project.get('lead_name'),
                    'status': project.get('status', 'unknown')
                },
                created_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to extract project context: {str(e)}")
            return None
    
    async def _extract_work_item_context(self, tenant_id: uuid.UUID, work_item: Dict[str, Any]) -> Optional[CompanyContext]:
        """Extract context from work item data"""
        try:
            # Build rich context content
            context_parts = [
                f"Work Item: {work_item.get('title', 'Untitled')}",
                f"Type: {work_item.get('work_item_type', 'Unknown')}",
                f"Status: {work_item.get('status', 'Unknown')}",
                f"Priority: {work_item.get('priority', 'Not set')}",
                f"Assignee: {work_item.get('assignee_name', 'Unassigned')}"
            ]
            
            # Add description if available
            if work_item.get('description'):
                context_parts.append(f"Description: {work_item['description'][:500]}...")
            
            # Add labels and components
            if work_item.get('labels'):
                context_parts.append(f"Labels: {', '.join(work_item['labels'])}")
            
            if work_item.get('components'):
                context_parts.append(f"Components: {', '.join(work_item['components'])}")
            
            # Add AI analysis if available
            if work_item.get('ai_summary'):
                context_parts.append(f"AI Summary: {work_item['ai_summary']}")
            
            # Add strategic scores
            if work_item.get('strategic_impact_score'):
                context_parts.append(f"Strategic Impact: {work_item['strategic_impact_score']:.2f}")
            
            content = "\n".join(context_parts)
            
            return CompanyContext(
                context_id=f"work_item_{work_item['id']}",
                tenant_id=tenant_id,
                context_type="work_item",
                title=work_item.get('title', 'Untitled Work Item'),
                content=content,
                metadata={
                    'work_item_id': work_item['id'],
                    'work_item_type': work_item.get('work_item_type'),
                    'status': work_item.get('status'),
                    'priority': work_item.get('priority'),
                    'assignee': work_item.get('assignee_name'),
                    'project_id': work_item.get('project_id'),
                    'strategic_impact_score': work_item.get('strategic_impact_score', 0)
                },
                created_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to extract work item context: {str(e)}")
            return None
    
    async def _store_context(self, context: CompanyContext):
        """Store context in vector database and local storage"""
        try:
            # Generate embedding if vector DB is available
            if self.pinecone_client and self.openai_client:
                embedding = await self._generate_embedding(context.content)
                context.embedding = embedding
                
                # Store in Pinecone
                self.index.upsert(
                    vectors=[(
                        context.context_id,
                        embedding,
                        {
                            'tenant_id': str(context.tenant_id),
                            'context_type': context.context_type,
                            'title': context.title,
                            'content': context.content[:1000],  # Limit content in metadata
                            **context.metadata
                        }
                    )]
                )
                
                logger.debug(f"Stored context {context.context_id} in Pinecone")
            
            # Store in PostgreSQL for persistence
            await self._store_context_in_db(context)
            
            # Cache locally
            self.context_cache[context.context_id] = context
            
        except Exception as e:
            logger.error(f"Failed to store context {context.context_id}: {str(e)}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    async def _store_context_in_db(self, context: CompanyContext):
        """Store context in PostgreSQL for persistence"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(context.tenant_id)
                )
                
                await connection.execute("""
                    INSERT INTO company_contexts (
                        context_id, tenant_id, context_type, title, content,
                        metadata, embedding_vector, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (tenant_id, context_id) 
                    DO UPDATE SET
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding_vector = EXCLUDED.embedding_vector,
                        updated_at = EXCLUDED.updated_at
                """,
                    context.context_id,
                    context.tenant_id,
                    context.context_type,
                    context.title,
                    context.content,
                    json.dumps(context.metadata),
                    json.dumps(context.embedding) if context.embedding else None,
                    context.created_at,
                    datetime.now(timezone.utc)
                )
                
        except Exception as e:
            logger.error(f"Failed to store context in DB: {str(e)}")
            # Don't raise - vector storage is more important than DB persistence
    
    async def get_relevant_context(self, tenant_id: uuid.UUID, query: str, limit: int = 10) -> List[CompanyContext]:
        """Get relevant company context for a query using vector similarity"""
        try:
            if not self.pinecone_client or not self.openai_client:
                return await self._get_relevant_context_fallback(tenant_id, query, limit)
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search Pinecone for similar contexts
            results = self.index.query(
                vector=query_embedding,
                filter={'tenant_id': str(tenant_id)},
                top_k=limit,
                include_metadata=True
            )
            
            # Convert results to CompanyContext objects
            relevant_contexts = []
            for match in results['matches']:
                metadata = match['metadata']
                context = CompanyContext(
                    context_id=match['id'],
                    tenant_id=uuid.UUID(metadata['tenant_id']),
                    context_type=metadata['context_type'],
                    title=metadata['title'],
                    content=metadata['content'],
                    metadata={k: v for k, v in metadata.items() if k not in ['tenant_id', 'context_type', 'title', 'content']},
                    relevance_score=match['score']
                )
                relevant_contexts.append(context)
            
            logger.info(f"Retrieved {len(relevant_contexts)} relevant contexts for query")
            return relevant_contexts
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {str(e)}")
            return await self._get_relevant_context_fallback(tenant_id, query, limit)
    
    async def _get_relevant_context_fallback(self, tenant_id: uuid.UUID, query: str, limit: int) -> List[CompanyContext]:
        """Fallback context retrieval using simple text matching"""
        try:
            # Get contexts from cache and database
            cached_contexts = [ctx for ctx in self.context_cache.values() if ctx.tenant_id == tenant_id]
            
            # Simple relevance scoring based on keyword matching
            query_words = set(query.lower().split())
            scored_contexts = []
            
            for context in cached_contexts:
                content_words = set(context.content.lower().split())
                title_words = set(context.title.lower().split())
                
                # Calculate relevance score
                content_overlap = len(query_words.intersection(content_words))
                title_overlap = len(query_words.intersection(title_words)) * 2  # Weight title matches more
                
                relevance_score = (content_overlap + title_overlap) / max(len(query_words), 1)
                context.relevance_score = relevance_score
                
                if relevance_score > 0:
                    scored_contexts.append(context)
            
            # Sort by relevance and return top matches
            scored_contexts.sort(key=lambda x: x.relevance_score, reverse=True)
            return scored_contexts[:limit]
            
        except Exception as e:
            logger.error(f"Fallback context retrieval failed: {str(e)}")
            return []
    
    async def _generate_context_insights(self, tenant_id: uuid.UUID):
        """Generate AI insights from learned company context"""
        try:
            # Get recent contexts for analysis
            recent_contexts = [
                ctx for ctx in self.context_cache.values() 
                if ctx.tenant_id == tenant_id and 
                ctx.created_at and 
                (datetime.now(timezone.utc) - ctx.created_at).days <= 30
            ]
            
            if len(recent_contexts) < 5:  # Need minimum contexts for meaningful insights
                return
            
            # Build context summary for AI analysis
            context_summary = self._build_context_summary(recent_contexts)
            
            # Generate insights using AI
            insight_prompt = f"""
            Analyze this company context data and identify key patterns, trends, and strategic insights:

            {context_summary}

            Please provide insights in this JSON format:
            {{
                "patterns": [
                    {{"type": "pattern_type", "description": "pattern description", "confidence": 0.0-1.0}}
                ],
                "trends": [
                    {{"type": "trend_type", "description": "trend description", "confidence": 0.0-1.0}}
                ],
                "opportunities": [
                    {{"description": "opportunity description", "potential_impact": "high/medium/low"}}
                ],
                "risks": [
                    {{"description": "risk description", "severity": "critical/high/medium/low"}}
                ]
            }}
            """
            
            ai_response = self.ai_manager.get_strategic_response(insight_prompt, "Company context analysis")
            
            # Process and store insights
            await self._process_context_insights(tenant_id, ai_response, recent_contexts)
            
            logger.info(f"Generated context insights for tenant {tenant_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate context insights: {str(e)}")
    
    def _build_context_summary(self, contexts: List[CompanyContext]) -> str:
        """Build summary of contexts for AI analysis"""
        summary_parts = [f"Company Context Analysis - {len(contexts)} contexts:"]
        
        # Group by type
        context_by_type = {}
        for context in contexts:
            if context.context_type not in context_by_type:
                context_by_type[context.context_type] = []
            context_by_type[context.context_type].append(context)
        
        # Summarize each type
        for context_type, type_contexts in context_by_type.items():
            summary_parts.append(f"\n{context_type.title()}s ({len(type_contexts)}):")
            for context in type_contexts[:5]:  # Limit to top 5 per type
                summary_parts.append(f"- {context.title}: {context.content[:200]}...")
        
        return "\n".join(summary_parts)
    
    async def _process_context_insights(self, tenant_id: uuid.UUID, ai_response: Dict[str, Any], 
                                      source_contexts: List[CompanyContext]):
        """Process and store AI-generated context insights"""
        try:
            response_text = ai_response.get('response', '{}')
            
            # Try to extract JSON insights
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                insights_data = json.loads(json_match.group())
            else:
                insights_data = self._parse_insights_fallback(response_text)
            
            # Create insight objects
            context_ids = [ctx.context_id for ctx in source_contexts]
            
            # Store patterns as insights
            for pattern in insights_data.get('patterns', []):
                insight = ContextInsight(
                    insight_id=f"pattern_{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    insight_type="pattern",
                    title=f"Pattern: {pattern.get('type', 'Unknown')}",
                    description=pattern.get('description', ''),
                    confidence_score=pattern.get('confidence', 0.5),
                    supporting_contexts=context_ids,
                    actionable_recommendations=[],
                    created_at=datetime.now(timezone.utc)
                )
                await self._store_insight(insight)
            
            # Store opportunities
            for opportunity in insights_data.get('opportunities', []):
                insight = ContextInsight(
                    insight_id=f"opportunity_{uuid.uuid4().hex[:8]}",
                    tenant_id=tenant_id,
                    insight_type="opportunity",
                    title=f"Opportunity: {opportunity.get('description', '')[:50]}...",
                    description=opportunity.get('description', ''),
                    confidence_score=0.7,  # Default confidence for opportunities
                    supporting_contexts=context_ids,
                    actionable_recommendations=self._generate_opportunity_recommendations(opportunity),
                    created_at=datetime.now(timezone.utc)
                )
                await self._store_insight(insight)
                
        except Exception as e:
            logger.error(f"Failed to process context insights: {str(e)}")
    
    def _parse_insights_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback insight parsing when JSON extraction fails"""
        return {
            'patterns': [{'type': 'general', 'description': 'Company context patterns identified', 'confidence': 0.6}],
            'trends': [],
            'opportunities': [{'description': 'Context-driven optimization opportunities available', 'potential_impact': 'medium'}],
            'risks': []
        }
    
    def _generate_opportunity_recommendations(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for opportunities"""
        impact = opportunity.get('potential_impact', 'medium')
        
        if impact == 'high':
            return [
                'Prioritize this opportunity in strategic planning',
                'Allocate dedicated resources for implementation',
                'Monitor progress with weekly reviews'
            ]
        elif impact == 'medium':
            return [
                'Include in quarterly planning cycle',
                'Evaluate resource requirements',
                'Track impact metrics'
            ]
        else:
            return [
                'Consider in long-term roadmap',
                'Monitor for changing conditions'
            ]
    
    async def _store_insight(self, insight: ContextInsight):
        """Store context insight in database"""
        try:
            async with self.database_pool.acquire() as connection:
                await connection.execute(
                    "SELECT set_config('app.current_tenant_id', $1, false)",
                    str(insight.tenant_id)
                )
                
                await connection.execute("""
                    INSERT INTO context_insights (
                        insight_id, tenant_id, insight_type, title, description,
                        confidence_score, supporting_contexts, actionable_recommendations,
                        created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (tenant_id, insight_id) DO NOTHING
                """,
                    insight.insight_id,
                    insight.tenant_id,
                    insight.insight_type,
                    insight.title,
                    insight.description,
                    insight.confidence_score,
                    insight.supporting_contexts,
                    json.dumps(insight.actionable_recommendations),
                    insight.created_at
                )
                
        except Exception as e:
            logger.error(f"Failed to store context insight: {str(e)}")
    
    async def get_tenant_context_summary(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Get summary of learned context for a tenant"""
        try:
            tenant_contexts = [ctx for ctx in self.context_cache.values() if ctx.tenant_id == tenant_id]
            
            summary = {
                'total_contexts': len(tenant_contexts),
                'context_types': {},
                'recent_contexts': 0,
                'learning_health': 'good',
                'key_insights': [],
                'context_coverage': {}
            }
            
            # Group by type and count
            for context in tenant_contexts:
                context_type = context.context_type
                if context_type not in summary['context_types']:
                    summary['context_types'][context_type] = 0
                summary['context_types'][context_type] += 1
                
                # Count recent contexts (last 7 days)
                if context.created_at and (datetime.now(timezone.utc) - context.created_at).days <= 7:
                    summary['recent_contexts'] += 1
            
            # Assess learning health
            if summary['total_contexts'] > 50:
                summary['learning_health'] = 'excellent'
            elif summary['total_contexts'] > 20:
                summary['learning_health'] = 'good'
            elif summary['total_contexts'] > 5:
                summary['learning_health'] = 'fair'
            else:
                summary['learning_health'] = 'needs_data'
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get context summary: {str(e)}")
            return {'total_contexts': 0, 'learning_health': 'error'}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for monitoring"""
        return {
            'pinecone_available': self.pinecone_client is not None,
            'openai_available': self.openai_client is not None,
            'vector_storage_active': PINECONE_AVAILABLE and self.pinecone_client is not None,
            'embedding_generation_active': OPENAI_AVAILABLE and self.openai_client is not None,
            'cached_contexts': len(self.context_cache),
            'index_name': self.index_name if self.pinecone_client else None,
            'learning_mode': 'vector_enhanced' if self.pinecone_client else 'fallback'
        }