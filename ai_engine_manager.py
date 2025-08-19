#!/usr/bin/env python3
"""
Multi-Engine AI Manager for PM33
Provides reliable AI responses through multiple providers with intelligent failover
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class AIEngineManager:
    """Manages multiple AI providers with intelligent failover and optimization"""
    
    def __init__(self):
        self.engines = {}
        self.engine_status = {}
        self.response_times = {}
        self.initialize_engines()
    
    def initialize_engines(self):
        """Initialize all available AI engines"""
        print("🎯 Initializing AI Engine Manager...")
        
        # Initialize OpenAI
        self._init_openai()
        
        # Initialize Groq (free tier available)
        self._init_groq()
        
        # Initialize Together AI  
        self._init_together()
        
        # Initialize Anthropic (as fallback)
        self._init_anthropic()
        
        # Show available engines
        available = [name for name, status in self.engine_status.items() if status == 'healthy']
        print(f"✅ {len(available)} AI engines available: {', '.join(available)}")
    
    def _init_openai(self):
        """Initialize OpenAI engine"""
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                self.engine_status['openai'] = 'no_key'
                return
            
            client = openai.OpenAI(api_key=api_key)
            
            # Quick test
            test_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            self.engines['openai'] = client
            self.engine_status['openai'] = 'healthy'
            print("✅ OpenAI engine initialized")
            
        except Exception as e:
            self.engine_status['openai'] = f'error: {str(e)[:50]}...'
            print(f"❌ OpenAI initialization failed: {str(e)}")
    
    def _init_groq(self):
        """Initialize Groq engine (ultra-fast)"""
        try:
            from groq import Groq
            groq_key = os.getenv('GROQ_API_KEY')
            
            if not groq_key:
                self.engine_status['groq'] = 'no_key'
                print("⚡ Groq engine available - need API key from console.groq.com/keys (free)")
                return
            
            client = Groq(api_key=groq_key)
            
            # Quick test
            test_response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            self.engines['groq'] = client
            self.engine_status['groq'] = 'healthy'
            print("✅ Groq engine initialized (ultra-fast inference)")
            
        except Exception as e:
            self.engine_status['groq'] = f'error: {str(e)[:50]}...'
            print(f"❌ Groq initialization failed: {str(e)}")
    
    def _init_together(self):
        """Initialize Together AI engine"""
        try:
            from together import Together
            together_key = os.getenv('TOGETHER_API_KEY')
            
            if not together_key:
                self.engine_status['together'] = 'no_key'
                print("🤝 Together AI available - signup at api.together.xyz/settings/api-keys ($1 free credit)")
                return
            
            client = Together(api_key=together_key)
            
            # Quick test with serverless model
            response = client.chat.completions.create(
                model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            
            self.engines['together'] = client
            self.engine_status['together'] = 'healthy'
            print("✅ Together AI engine initialized (cost-effective)")
            
        except Exception as e:
            self.engine_status['together'] = f'error: {str(e)[:50]}...'
            print(f"❌ Together AI initialization failed: {str(e)}")
    
    def _init_anthropic(self):
        """Initialize Anthropic engine (problematic)"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            if not api_key:
                self.engine_status['anthropic'] = 'no_key'
                return
            
            client = anthropic.Anthropic(api_key=api_key)
            self.engines['anthropic'] = client
            self.engine_status['anthropic'] = 'available_untested'  # Don't test to avoid hangs
            print("🔶 Anthropic engine available (untested due to reliability issues)")
            
        except Exception as e:
            self.engine_status['anthropic'] = f'error: {str(e)[:50]}...'
            print(f"❌ Anthropic initialization failed: {str(e)}")
    
    def get_strategic_response(self, question: str, context: str) -> Dict:
        """Get strategic response with intelligent engine selection optimized for performance/quality/cost"""
        
        # Analyze query complexity and requirements
        query_profile = self._analyze_query_requirements(question, context)
        
        # Select optimal engine based on requirements
        engine_priority = self._select_optimal_engines(query_profile)
        
        print(f"🎯 Query profile: {query_profile['complexity']} complexity, {query_profile['context_size']} context")
        print(f"🚀 Engine priority: {' → '.join(engine_priority)}")
        
        for engine_name in engine_priority:
            if self.engine_status.get(engine_name) == 'healthy':
                try:
                    print(f"🚀 Trying {engine_name} engine...")
                    response = self._call_engine(engine_name, question, context)
                    
                    if response:
                        # Add query profile to response metadata
                        response['meta']['query_profile'] = query_profile
                        response['meta']['engine_selection_reason'] = self._get_selection_reason(engine_name, query_profile)
                        
                        print(f"✅ {engine_name} responded successfully")
                        return response
                        
                except Exception as e:
                    print(f"❌ {engine_name} failed: {str(e)[:100]}...")
                    self.engine_status[engine_name] = 'degraded'
                    continue
        
        # All engines failed - return structured fallback
        print("⚠️ All AI engines failed - returning structured fallback")
        return self._create_fallback_response(question, context)
    
    def _analyze_query_requirements(self, question: str, context: str) -> Dict:
        """Analyze query to determine optimal engine selection"""
        
        # Analyze context size
        context_size = len(context)
        if context_size > 2000:
            context_category = 'large'
        elif context_size > 1000:
            context_category = 'medium'
        else:
            context_category = 'small'
        
        # Analyze query complexity
        complexity_indicators = [
            'strategic', 'framework', 'analysis', 'competitive', 'market',
            'prioritization', 'resource allocation', 'okr', 'roadmap',
            'business model', 'go-to-market', 'positioning'
        ]
        
        question_lower = question.lower()
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in question_lower)
        
        if complexity_score >= 3 or len(question) > 200:
            complexity = 'high'
        elif complexity_score >= 1 or len(question) > 50:
            complexity = 'medium'  
        else:
            complexity = 'low'
        
        # Determine if speed is critical (short questions, demos)
        speed_critical = len(question) < 50 or any(word in question_lower for word in ['quick', 'fast', 'demo', 'test'])
        
        return {
            'complexity': complexity,
            'context_size': context_category,
            'speed_critical': speed_critical,
            'question_length': len(question),
            'context_length': context_size,
            'complexity_score': complexity_score
        }
    
    def _select_optimal_engines(self, query_profile: Dict) -> List[str]:
        """Select optimal engine order based on query requirements"""
        
        # Engine characteristics
        engine_profiles = {
            'groq': {'speed': 10, 'quality': 8, 'cost': 10, 'context_limit': 8192},
            'openai': {'speed': 7, 'quality': 9, 'cost': 6, 'context_limit': 16384},
            'anthropic': {'speed': 5, 'quality': 10, 'cost': 7, 'context_limit': 200000},
            'together': {'speed': 8, 'quality': 8, 'cost': 9, 'context_limit': 8192}
        }
        
        # Score engines based on requirements
        engine_scores = {}
        
        for engine, profile in engine_profiles.items():
            score = 0
            
            # Speed optimization
            if query_profile['speed_critical']:
                score += profile['speed'] * 2
            else:
                score += profile['speed']
            
            # Quality optimization for complex queries
            if query_profile['complexity'] == 'high':
                score += profile['quality'] * 2
            else:
                score += profile['quality']
            
            # Cost optimization (higher is better)
            score += profile['cost']
            
            # Context handling
            if query_profile['context_size'] == 'large' and profile['context_limit'] > 16000:
                score += 3
            
            # Penalize if engine is not healthy
            if self.engine_status.get(engine) != 'healthy':
                score = 0
            
            engine_scores[engine] = score
        
        # Sort by score (descending)
        sorted_engines = sorted(engine_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return engines with score > 0
        return [engine for engine, score in sorted_engines if score > 0]
    
    def _get_selection_reason(self, engine: str, query_profile: Dict) -> str:
        """Get human-readable reason for engine selection"""
        reasons = []
        
        if query_profile['speed_critical']:
            reasons.append('speed-critical query')
        
        if query_profile['complexity'] == 'high':
            reasons.append('high complexity analysis')
        elif query_profile['complexity'] == 'medium':
            reasons.append('medium complexity query')
        
        if query_profile['context_size'] == 'large':
            reasons.append('large context preservation needed')
        
        engine_strengths = {
            'groq': 'ultra-fast inference',
            'openai': 'balanced performance and quality', 
            'anthropic': 'superior reasoning and large context',
            'together': 'cost-effective with good quality'
        }
        
        base_reason = engine_strengths.get(engine, 'available engine')
        
        if reasons:
            return f"{base_reason} - optimized for {', '.join(reasons)}"
        else:
            return base_reason
    
    def _call_engine(self, engine_name: str, question: str, context: str) -> Dict:
        """Call specific AI engine"""
        
        if engine_name == 'openai':
            return self._call_openai(question, context)
        elif engine_name == 'groq':
            return self._call_groq(question, context)
        elif engine_name == 'together':
            return self._call_together(question, context)
        elif engine_name == 'anthropic':
            return self._call_anthropic(question, context)
        else:
            raise Exception(f"Unknown engine: {engine_name}")
    
    def _call_openai(self, question: str, context: str) -> Dict:
        """Call OpenAI with strategic prompt"""
        if 'openai' not in self.engines:
            raise Exception("OpenAI client not available")
        
        client = self.engines['openai']
        
        prompt = self._build_strategic_prompt(question, context)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use the faster, cheaper model
            messages=[
                {"role": "system", "content": "You are PM33's Strategic AI Co-Pilot, an expert Product Manager consultant specializing in strategic analysis and executable frameworks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        response_time = time.time() - start_time
        ai_response = response.choices[0].message.content
        
        return {
            'response': ai_response,
            'meta': {
                'engine': 'openai',
                'model': 'gpt-4o-mini',
                'response_time': response_time,
                'context_chars': len(context),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _call_groq(self, question: str, context: str) -> Dict:
        """Call Groq with ultra-fast inference"""
        if 'groq' not in self.engines:
            raise Exception("Groq client not available")
        
        client = self.engines['groq']
        
        prompt = self._build_strategic_prompt(question, context)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Best balance of speed/quality
            messages=[
                {"role": "system", "content": "You are PM33's Strategic AI Co-Pilot, an expert Product Manager consultant specializing in strategic analysis and executable frameworks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        response_time = time.time() - start_time
        ai_response = response.choices[0].message.content
        
        return {
            'response': ai_response,
            'meta': {
                'engine': 'groq',
                'model': 'llama-3.1-70b-versatile',
                'response_time': response_time,
                'context_chars': len(context),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _call_together(self, question: str, context: str) -> Dict:
        """Call Together AI with cost-effective inference"""
        if 'together' not in self.engines:
            raise Exception("Together AI client not available")
        
        client = self.engines['together']
        
        prompt = self._build_strategic_prompt(question, context)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",  # Serverless model
            messages=[
                {"role": "system", "content": "You are PM33's Strategic AI Co-Pilot, an expert Product Manager consultant specializing in strategic analysis and executable frameworks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        response_time = time.time() - start_time
        ai_response = response.choices[0].message.content
        
        return {
            'response': ai_response,
            'meta': {
                'engine': 'together',
                'model': 'llama-3-70b-chat',
                'response_time': response_time,
                'context_chars': len(context),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _call_anthropic(self, question: str, context: str) -> Dict:
        """Call Anthropic with timeout protection"""
        if 'anthropic' not in self.engines:
            raise Exception("Anthropic client not available")
        
        # Add timeout protection to prevent hangs
        import signal
        
        def timeout_handler(signum, frame):
            raise Exception("Anthropic API timeout after 10 seconds")
        
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second timeout
            
            client = self.engines['anthropic']
            prompt = self._build_strategic_prompt(question, context)
            
            start_time = time.time()
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            signal.alarm(0)  # Cancel timeout
            response_time = time.time() - start_time
            ai_response = response.content[0].text
            
            return {
                'response': ai_response,
                'meta': {
                    'engine': 'anthropic',
                    'model': 'claude-3-haiku',
                    'response_time': response_time,
                    'context_chars': len(context),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            raise e
    
    def _build_strategic_prompt(self, question: str, context: str) -> str:
        """Build strategic prompt optimized for AI engines"""
        
        # Check if question is PM33-specific or general business question
        pm33_keywords = ['pm33', 'our company', 'our product', 'our startup', 'we should', 'our team', 'our users', 'our competitors']
        is_pm33_specific = any(keyword in question.lower() for keyword in pm33_keywords)
        
        if is_pm33_specific:
            # PM33-specific strategic analysis
            return f"""You are PM33's Strategic AI Co-Pilot. Analyze this strategic question using proven PM frameworks.

COMPANY CONTEXT (PM33):
{context[:1200]}

STRATEGIC QUESTION: {question}

Provide a strategic analysis in this format:

**STRATEGIC ANALYSIS:**
[2-3 sentences of strategic assessment considering PM33's specific situation]

**RECOMMENDED FRAMEWORK:**  
[Which PM framework applies: ICE, RICE, OKR, Blue Ocean Strategy, Jobs-to-be-Done, etc.]

**KEY ACTIONS:**
1. [Specific action with assignee]
2. [Specific action with assignee]  
3. [Specific action with assignee]

Focus on PM33's beta stage, limited resources, and strategic positioning in the AI PM tools market."""
        else:
            # General strategic/business question
            return f"""You are a Strategic AI Co-Pilot for Product Managers. Answer this strategic question directly using proven business frameworks.

QUESTION: {question}

Provide a comprehensive strategic analysis in this format:

**STRATEGIC ANALYSIS:**
[Direct answer to the question with strategic insights]

**RECOMMENDED FRAMEWORK:**
[Which business framework applies: Porter's Five Forces, Blue Ocean Strategy, Jobs-to-be-Done, Market Sizing, etc.]

**KEY INSIGHTS:**
1. [Specific strategic insight]
2. [Specific strategic insight]
3. [Specific strategic insight]

Focus on providing actionable strategic guidance for product management and business decisions."""

    def _create_fallback_response(self, question: str, context: str) -> Dict:
        """Create structured fallback when all AI engines fail"""
        
        return {
            'response': f'Strategic analysis system temporarily unavailable. Question received: "{question}". PM33 context loaded ({len(context)} chars). This would normally provide strategic guidance using proven PM frameworks, but AI engines are currently unresponsive.',
            'meta': {
                'engine': 'fallback',
                'model': 'system_fallback',
                'response_time': 0.001,
                'context_chars': len(context),
                'timestamp': datetime.now().isoformat(),
                'available_engines': list(self.engine_status.keys()),
                'engine_health': self.engine_status
            }
        }
    
    def get_engine_status(self) -> Dict:
        """Get health status of all engines"""
        return {
            'engines': self.engine_status,
            'healthy_count': len([s for s in self.engine_status.values() if s == 'healthy']),
            'total_count': len(self.engine_status),
            'timestamp': datetime.now().isoformat()
        }

# Test the engine manager
if __name__ == "__main__":
    manager = AIEngineManager()
    
    print("\n🧪 Testing AI Engine Manager...")
    
    test_question = "Our competitor launched similar features with 10x funding. Strategic response?"
    test_context = "PM33 is a beta-stage AI Strategic Co-Pilot targeting Product Managers. Current stage: 15 signups, targeting 50 beta users. Team: 1 PM + 2 Engineers. Budget: $15,000."
    
    response = manager.get_strategic_response(test_question, test_context)
    
    print(f"\n📊 Response Summary:")
    print(f"Engine: {response['meta']['engine']}")
    print(f"Response time: {response['meta']['response_time']:.2f}s")
    print(f"Response length: {len(response['response'])} chars")
    print(f"Response preview: {response['response'][:150]}...")