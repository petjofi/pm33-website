#!/usr/bin/env python3
"""
PM33 Demo with OpenAI Implementation
Testing alternative AI provider to isolate Anthropic issues
"""

from flask import Flask, render_template, request, jsonify
import openai
import os
import sys
import time
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment and add backend to path
load_dotenv()
sys.path.append('app/backend')

app = Flask(__name__)

class PM33OpenAIService:
    """PM33 Demo Service using OpenAI instead of Anthropic"""
    
    def __init__(self):
        self.initialized = False
        self.health_status = {}
        self.context_manager = None
        self.openai_client = None
        self.initialize()
    
    def initialize(self):
        """Initialize all components with health checks"""
        print("🎯 Initializing PM33 Demo Service with OpenAI...")
        
        # Initialize OpenAI client
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("❌ OPENAI_API_KEY not found, trying with test key...")
                # For demo purposes, we'll try to continue without it
                self.health_status['openai_client'] = 'error: no API key'
            else:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.health_status['openai_client'] = 'healthy'
                print("✅ OpenAI Client initialized")
        except Exception as e:
            self.health_status['openai_client'] = f'error: {str(e)}'
            print(f"❌ OpenAI Client failed: {str(e)}")
        
        # Initialize Context Manager
        try:
            from context_manager import StrategicContextManager
            self.context_manager = StrategicContextManager()
            test_context = self.context_manager.get_relevant_context("test query")
            self.health_status['context_manager'] = 'healthy'
            print(f"✅ Context Manager initialized ({len(test_context)} chars loaded)")
        except Exception as e:
            self.health_status['context_manager'] = f'error: {str(e)}'
            print(f"❌ Context Manager failed: {str(e)}")
        
        # Check overall health
        healthy_components = sum(1 for status in self.health_status.values() if status == 'healthy')
        total_components = len(self.health_status)
        
        if healthy_components >= 1:  # At least context manager working
            self.initialized = True
            print(f"🎉 {healthy_components}/{total_components} components healthy - Demo service ready!")
        else:
            print(f"⚠️ {healthy_components}/{total_components} components healthy")
    
    def get_health_status(self):
        """Get current health status"""
        return {
            'initialized': self.initialized,
            'components': self.health_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_strategic_response(self, question):
        """Generate strategic response - with detailed error tracking"""
        print(f"🔍 Processing question: '{question}'")
        
        if not self.initialized:
            print("❌ Service not initialized")
            return self._create_error_response("Service not properly initialized")
        
        try:
            # Step 1: Get relevant context
            context = ""
            if self.context_manager:
                context = self.context_manager.get_relevant_context(question)
                print(f"✅ Context loaded: {len(context)} characters")
            else:
                print("⚠️ No context manager available")
            
            # Step 2: Build strategic prompt
            strategic_prompt = self._build_strategic_prompt(question, context)
            print(f"✅ Strategic prompt built: {len(strategic_prompt)} characters")
            
            # Step 3: Try AI call with detailed logging
            print("🚀 Making AI API call...")
            start_time = time.time()
            
            if not self.openai_client:
                print("❌ No OpenAI client available")
                return self._create_mock_response(question, context)
            
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are PM33's Strategic AI Co-Pilot, an expert Product Manager consultant."},
                        {"role": "user", "content": strategic_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                ai_time = time.time() - start_time
                ai_response = response.choices[0].message.content
                
                print(f"✅ OpenAI responded in {ai_time:.2f}s: {len(ai_response)} characters")
                print(f"📝 Response preview: {ai_response[:100]}...")
                
            except Exception as api_error:
                print(f"❌ OpenAI API call failed: {str(api_error)}")
                return self._create_mock_response(question, context)
            
            # Step 4: Create workflow structure
            workflow = self._create_simple_workflow(ai_response, question)
            
            return {
                'response': ai_response,
                'workflow': workflow,
                'meta': {
                    'response_time': ai_time,
                    'context_chars': len(context),
                    'timestamp': datetime.now().isoformat(),
                    'ai_provider': 'openai'
                }
            }
            
        except Exception as e:
            print(f"❌ Strategic response generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_response(f"Strategic analysis failed: {str(e)}")
    
    def _build_strategic_prompt(self, question, context):
        """Build strategic prompt with company context"""
        return f"""COMPANY CONTEXT:
{context[:1000]}

STRATEGIC QUESTION: {question}

Please provide a strategic analysis as a Product Manager consultant. Focus on:
1. Strategic assessment of the situation
2. Recommended PM framework to apply
3. 3-4 specific actionable next steps

Be strategic, practical, and PM-focused. Consider PM33's beta stage and resource constraints."""
    
    def _create_simple_workflow(self, ai_response, question):
        """Create simple workflow from AI response"""
        return {
            'id': f'workflow_{hash(question) % 1000:03d}',
            'name': 'Strategic AI Analysis',
            'strategic_objective': f'Address strategic question: {question}',
            'framework_used': 'AI-Generated Strategic Framework',
            'context_factors': [
                'PM33 beta stage - real company context applied',
                'Strategic AI analysis completed',
                f'Response generated via OpenAI'
            ],
            'tasks': [
                {
                    'id': 't001',
                    'title': 'Review AI Strategic Analysis',
                    'description': f'Analyze the strategic recommendations provided',
                    'assignee': 'Product Manager',
                    'priority': 'high',
                    'due_date': datetime.now().strftime('%Y-%m-%d'),
                    'estimated_hours': 2,
                    'strategic_rationale': 'AI-generated strategic analysis requires review and implementation planning'
                }
            ],
            'success_metrics': ['Strategic question addressed with AI analysis'],
            'risk_factors': ['Implementation depends on resource availability']
        }
    
    def _create_mock_response(self, question, context):
        """Create mock response when AI unavailable"""
        print("🔄 Creating mock response due to AI unavailability")
        
        return {
            'response': f'Mock strategic analysis for: "{question}". Based on PM33\'s context ({len(context)} chars), here would be strategic guidance. (AI service unavailable - this is a fallback response for testing)',
            'workflow': {
                'id': 'mock_001',
                'name': 'Mock Strategic Analysis',
                'strategic_objective': f'Demonstrate system functionality for: {question}',
                'framework_used': 'System Testing Framework',
                'context_factors': [
                    'PM33 beta stage context loaded',
                    f'Question processed: {question}',
                    'AI service unavailable - mock response active'
                ],
                'tasks': [
                    {
                        'id': 't001',
                        'title': 'Configure AI Service',
                        'description': 'Set up OpenAI API key to enable real AI responses',
                        'assignee': 'Engineering Team',
                        'priority': 'critical',
                        'due_date': datetime.now().strftime('%Y-%m-%d'),
                        'estimated_hours': 1,
                        'strategic_rationale': 'Real AI responses needed for demo functionality'
                    }
                ],
                'success_metrics': ['AI service configured and responding'],
                'risk_factors': ['Demo limited without AI integration']
            },
            'meta': {
                'response_time': 0.01,
                'context_chars': len(context),
                'timestamp': datetime.now().isoformat(),
                'ai_provider': 'mock'
            }
        }
    
    def _create_error_response(self, error_message):
        """Create clear error response"""
        print(f"🚨 Creating error response: {error_message}")
        
        return {
            'response': f'❌ ERROR: {error_message}',
            'workflow': {
                'id': 'error_001',
                'name': '🚨 Service Error',
                'strategic_objective': 'Diagnose and fix service issue',
                'framework_used': 'Error Recovery Framework',
                'context_factors': [
                    f'Error: {error_message}',
                    'Service diagnostics needed'
                ],
                'tasks': [
                    {
                        'id': 't001',
                        'title': 'Debug Service Error',
                        'description': f'Investigate: {error_message}',
                        'assignee': 'Engineering Team',
                        'priority': 'critical',
                        'due_date': datetime.now().strftime('%Y-%m-%d'),
                        'estimated_hours': 1,
                        'strategic_rationale': 'Service must be functional for demos'
                    }
                ],
                'success_metrics': ['Error resolved and service restored'],
                'risk_factors': ['Demo blocked until resolution']
            }
        }

# Initialize service
demo_service = PM33OpenAIService()

# Routes
@app.route('/')
def home():
    return render_template('mockup_demo.html')

@app.route('/health')
def health_check():
    return jsonify(demo_service.get_health_status())

@app.route('/api/mock-strategic-response', methods=['POST'])
def strategic_response():
    """Strategic response endpoint with detailed logging"""
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        print(f"\n🎯 === NEW REQUEST ===")
        print(f"📥 Received question: '{question}'")
        
        if not question:
            print("❌ Empty question provided")
            return jsonify({'error': 'No question provided'}), 400
        
        # Generate strategic response with full logging
        result = demo_service.generate_strategic_response(question)
        
        print(f"✅ Response generated successfully")
        print(f"📤 Sending response with {len(result.get('response', ''))} chars")
        print(f"🎯 === REQUEST COMPLETE ===\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Service error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎯 PM33 OpenAI Demo Service")
    print("🌐 Demo URL: http://localhost:8002")
    print("🤖 Using OpenAI instead of Anthropic for AI calls")
    print("📋 Health check: http://localhost:8002/health")
    print("🔍 Full request logging enabled")
    app.run(debug=True, host='127.0.0.1', port=8002)