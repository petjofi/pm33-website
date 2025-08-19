"""
PM33 Strategic Context Manager
Loads and manages company context for strategic AI responses
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from datetime import datetime

class StrategicContextManager:
    """Manages company context for strategic AI responses"""
    
    def __init__(self, context_path: str = None):
        self.context_path = context_path or "/Users/ssaper/Desktop/my-projects/pm33-claude-execution/strategy/context"
        self.context_cache = {}
        self.load_all_context()
    
    def load_all_context(self):
        """Load all context files into memory"""
        context_files = {
            'company_profile': 'company/company-profile.md',
            'business_model': 'company/business-model.md',
            'ideal_customer_profile': 'gtm/ideal-customer-profile.md',
            'customer_segments': 'gtm/customer-segments.md',
            'current_priorities': 'operations/current-priorities.md',
            'team_structure': 'operations/team-structure.md',
            'direct_competitors': 'competitive/direct-competitors.md',
            'competitive_advantages': 'competitive/competitive-advantages.md',
            'product_strategy': 'product/product-strategy.md',
            'financial_position': 'financial/financial-position.md'
        }
        
        for context_key, file_path in context_files.items():
            full_path = os.path.join(self.context_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.context_cache[context_key] = {
                            'content': content,
                            'file_path': full_path,
                            'last_updated': os.path.getmtime(full_path),
                            'summary': self._extract_summary(content)
                        }
                except Exception as e:
                    print(f"Error loading context file {full_path}: {e}")
    
    def _extract_summary(self, content: str) -> str:
        """Extract key summary points from markdown content"""
        lines = content.split('\n')
        summary_points = []
        
        # Extract headers and first few bullet points
        for line in lines[:50]:  # First 50 lines for summary
            line = line.strip()
            if line.startswith('#') or line.startswith('-') or line.startswith('*'):
                if len(line) < 200:  # Avoid very long lines
                    summary_points.append(line)
        
        return '\n'.join(summary_points[:10])  # Top 10 summary points
    
    def get_relevant_context(self, query: str, context_types: List[str] = None) -> str:
        """Get context relevant to a strategic query"""
        if context_types is None:
            context_types = self._identify_relevant_context_types(query)
        
        relevant_context = []
        
        for context_type in context_types:
            if context_type in self.context_cache:
                context_data = self.context_cache[context_type]
                relevant_context.append(f"## {context_type.replace('_', ' ').title()}")
                relevant_context.append(context_data['summary'])
                relevant_context.append("")
        
        return '\n'.join(relevant_context)
    
    def _identify_relevant_context_types(self, query: str) -> List[str]:
        """Identify what context types are relevant for a query"""
        query_lower = query.lower()
        relevant_types = []
        
        # Keyword-based context matching
        context_keywords = {
            'company_profile': ['company', 'mission', 'vision', 'values', 'business model'],
            'ideal_customer_profile': ['customer', 'user', 'target', 'market', 'audience', 'icp'],
            'current_priorities': ['priority', 'goals', 'objectives', 'focus', 'timeline', 'deadline'],
            'direct_competitors': ['competitor', 'competition', 'competitive', 'market', 'rival'],
            'product_strategy': ['product', 'feature', 'roadmap', 'development', 'technology'],
            'financial_position': ['budget', 'funding', 'revenue', 'cost', 'money', 'financial'],
            'team_structure': ['team', 'hiring', 'resources', 'people', 'capacity']
        }
        
        for context_type, keywords in context_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                relevant_types.append(context_type)
        
        # Always include company profile and current priorities for strategic context
        if 'company_profile' not in relevant_types:
            relevant_types.insert(0, 'company_profile')
        if 'current_priorities' not in relevant_types:
            relevant_types.append('current_priorities')
        
        return relevant_types
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of available context"""
        summary = {
            'total_context_files': len(self.context_cache),
            'context_categories': list(self.context_cache.keys()),
            'last_updated': max([ctx['last_updated'] for ctx in self.context_cache.values()]) if self.context_cache else None,
            'context_health': self._assess_context_health()
        }
        return summary
    
    def _assess_context_health(self) -> Dict[str, Any]:
        """Assess completeness and freshness of context"""
        required_contexts = [
            'company_profile', 'ideal_customer_profile', 
            'current_priorities', 'direct_competitors'
        ]
        
        missing_contexts = [ctx for ctx in required_contexts if ctx not in self.context_cache]
        
        # Check freshness (context older than 7 days is stale)
        stale_threshold = 7 * 24 * 60 * 60  # 7 days in seconds
        current_time = datetime.now().timestamp()
        
        stale_contexts = []
        for ctx_name, ctx_data in self.context_cache.items():
            if current_time - ctx_data['last_updated'] > stale_threshold:
                stale_contexts.append(ctx_name)
        
        return {
            'completeness_score': (len(required_contexts) - len(missing_contexts)) / len(required_contexts),
            'missing_contexts': missing_contexts,
            'stale_contexts': stale_contexts,
            'total_contexts_loaded': len(self.context_cache)
        }
    
    def update_context(self, context_type: str, content: str) -> bool:
        """Update specific context content"""
        if context_type not in self.context_cache:
            return False
        
        file_path = self.context_cache[context_type]['file_path']
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Refresh cache
            self.context_cache[context_type] = {
                'content': content,
                'file_path': file_path,
                'last_updated': datetime.now().timestamp(),
                'summary': self._extract_summary(content)
            }
            return True
        except Exception as e:
            print(f"Error updating context {context_type}: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    context_manager = StrategicContextManager()
    
    print("=== PM33 Strategic Context Manager ===")
    print(f"Loaded {len(context_manager.context_cache)} context files")
    
    # Test context retrieval
    test_queries = [
        "Our competitor just launched a similar feature. How should we respond?",
        "Should we hire more engineers or invest in marketing?",
        "What's our ideal customer profile for the next quarter?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        relevant_context = context_manager.get_relevant_context(query)
        print(f"Relevant context length: {len(relevant_context)} characters")
        
    # Context health check
    health = context_manager.get_context_summary()
    print(f"\nContext Health: {health}")