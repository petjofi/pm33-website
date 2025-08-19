#!/usr/bin/env python3
"""
PM33 Multi-Engine Demo Service
Uses intelligent AI engine selection for optimal performance/quality/cost
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment and add backend to path
load_dotenv()
sys.path.append('app/backend')

from ai_engine_manager import AIEngineManager

app = Flask(__name__)

class PM33MultiEngineService:
    """PM33 Demo Service with multi-engine AI intelligence"""
    
    def __init__(self):
        self.initialized = False
        self.health_status = {}
        self.context_manager = None
        self.ai_manager = None
        self.initialize()
    
    def initialize(self):
        """Initialize all components"""
        print("🎯 Initializing PM33 Multi-Engine Demo Service...")
        
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
        
        # Initialize AI Engine Manager
        try:
            self.ai_manager = AIEngineManager()
            self.health_status['ai_manager'] = 'healthy'
            print("✅ Multi-Engine AI Manager initialized")
        except Exception as e:
            self.health_status['ai_manager'] = f'error: {str(e)}'
            print(f"❌ AI Engine Manager failed: {str(e)}")
        
        # Check overall health
        healthy_components = sum(1 for status in self.health_status.values() if status == 'healthy')
        total_components = len(self.health_status)
        
        if healthy_components >= 1:
            self.initialized = True
            print(f"🎉 {healthy_components}/{total_components} components healthy - Multi-engine service ready!")
        else:
            print(f"⚠️ {healthy_components}/{total_components} components healthy")
    
    def get_health_status(self):
        """Get comprehensive health status"""
        base_status = {
            'initialized': self.initialized,
            'components': self.health_status,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add AI engine details if available
        if self.ai_manager:
            base_status['ai_engines'] = self.ai_manager.get_engine_status()
        
        return base_status
    
    def generate_strategic_response(self, question):
        """Generate strategic response with intelligent engine selection"""
        print(f"\n🎯 === PROCESSING STRATEGIC QUERY ===")
        print(f"📥 Question: '{question}'")
        
        if not self.initialized:
            return self._create_service_error("Service not properly initialized")
        
        try:
            # Step 1: Get relevant context
            context = ""
            if self.context_manager:
                context = self.context_manager.get_relevant_context(question)
                print(f"✅ Context loaded: {len(context)} characters")
            else:
                print("⚠️ No context manager available")
            
            # Step 2: Use AI Engine Manager for intelligent response
            if self.ai_manager:
                ai_response_data = self.ai_manager.get_strategic_response(question, context)
                
                # Create workflow from AI response
                workflow = self._create_workflow_from_ai_response(ai_response_data, question)
                
                return {
                    'response': ai_response_data['response'],
                    'workflow': workflow,
                    'meta': {
                        **ai_response_data['meta'],
                        'service': 'pm33_multi_engine',
                        'context_chars': len(context)
                    }
                }
            else:
                return self._create_service_error("AI Engine Manager not available")
                
        except Exception as e:
            print(f"❌ Strategic response generation failed: {str(e)}")
            return self._create_service_error(f"Strategic analysis failed: {str(e)}")
    
    def _create_workflow_from_ai_response(self, ai_response_data, question):
        """Create workflow structure from AI response"""
        
        # Extract framework and tasks from AI response
        ai_text = ai_response_data['response']
        
        # Try to extract framework
        framework = "Strategic Analysis Framework"
        framework_keywords = {
            'ice': 'ICE Prioritization Framework',
            'rice': 'RICE Scoring Framework',
            'okr': 'OKR Strategic Planning',
            'blue ocean': 'Blue Ocean Strategy',
            'jobs-to-be-done': 'Jobs-to-be-Done Framework',
            'competitive': 'Competitive Strategy Framework'
        }
        
        for keyword, fw_name in framework_keywords.items():
            if keyword in ai_text.lower():
                framework = fw_name
                break
        
        # Extract action items from AI response
        tasks = self._extract_tasks_from_ai_response(ai_text, question)
        
        return {
            'id': f'workflow_{hash(question) % 1000:03d}',
            'name': self._generate_workflow_name(question),
            'strategic_objective': f'Address strategic question with AI-powered analysis: {question}',
            'framework_used': framework,
            'context_factors': [
                'PM33 beta stage - real company context applied',
                f'AI Engine: {ai_response_data["meta"]["engine"]} ({ai_response_data["meta"]["model"]})',
                f'Response time: {ai_response_data["meta"]["response_time"]:.2f}s',
                f'Query optimization: {ai_response_data["meta"].get("engine_selection_reason", "standard selection")}'
            ],
            'tasks': tasks,
            'success_metrics': [
                'Strategic question addressed with AI analysis',
                'Implementation plan created',
                'Progress toward business objectives maintained'
            ],
            'risk_factors': [
                'Implementation depends on resource availability',
                'Market conditions may evolve'
            ]
        }
    
    def _extract_tasks_from_ai_response(self, ai_text, question):
        """Extract actionable tasks from AI response"""
        tasks = []
        
        # Look for numbered lists or action items in AI response
        lines = ai_text.split('\n')
        action_lines = []
        
        for line in lines:
            line = line.strip()
            # Look for action indicators
            if any(indicator in line.lower() for indicator in ['1.', '2.', '3.', '4.', '-', '•', 'action', 'step']):
                if len(line) > 15:  # Meaningful content
                    clean_line = line.strip('1234567890.- •').strip()
                    if clean_line:
                        action_lines.append(clean_line)
        
        # If no clear actions found, create strategic tasks based on question type
        if not action_lines:
            action_lines = self._generate_strategic_tasks(question)
        
        # Convert to structured tasks
        priorities = ['critical', 'high', 'medium', 'low']
        assignees = ['Product Manager', 'Engineering Lead', 'Marketing Lead', 'CEO', 'Growth Lead', 'Data Analyst']
        
        for i, action in enumerate(action_lines[:4]):  # Max 4 tasks
            due_days = 2 + i * 2  # Stagger due dates
            
            tasks.append({
                'id': f't{i+1:03d}',
                'title': action[:80],  # Reasonable title length
                'description': f'Execute: {action}',
                'assignee': assignees[i % len(assignees)],
                'priority': priorities[min(i, len(priorities)-1)],
                'due_date': (datetime.now().strftime('%Y-%m-%d')),  # Simplified for demo
                'estimated_hours': 4 + i * 2,
                'strategic_rationale': 'Based on AI strategic analysis and company context'
            })
        
        return tasks
    
    def _generate_strategic_tasks(self, question):
        """Generate strategic tasks based on question type"""
        question_lower = question.lower()
        
        if 'competitor' in question_lower or 'competition' in question_lower:
            return [
                "Conduct competitive analysis deep dive",
                "Develop differentiation strategy",
                "Accelerate user acquisition to gain first-mover advantage", 
                "Monitor competitor responses and adjust strategy"
            ]
        elif 'budget' in question_lower or 'resource' in question_lower:
            return [
                "Analyze ROI for each budget allocation option",
                "Execute highest ROI resource allocation",
                "Monitor resource utilization and effectiveness",
                "Review and adjust allocation monthly"
            ]
        elif 'user' in question_lower or 'growth' in question_lower:
            return [
                "Design user acquisition strategy",
                "Implement growth experiments",
                "Monitor user engagement metrics",
                "Optimize conversion funnel"
            ]
        else:
            return [
                "Conduct strategic analysis session",
                "Align stakeholders on strategic direction",
                "Create implementation timeline",
                "Set up progress monitoring"
            ]
    
    def _generate_workflow_name(self, question):
        """Generate appropriate workflow name"""
        question_lower = question.lower()
        
        if 'competitor' in question_lower:
            return "Competitive Strategy Response"
        elif 'budget' in question_lower:
            return "Resource Allocation Strategy"
        elif 'user' in question_lower or 'growth' in question_lower:
            return "User Growth Strategy"
        elif 'product' in question_lower:
            return "Product Strategy Framework"
        else:
            return "Strategic Analysis Workflow"
    
    def _create_service_error(self, error_message):
        """Create clear service error response"""
        return {
            'response': f'❌ SERVICE ERROR: {error_message}',
            'workflow': {
                'id': 'service_error',
                'name': '🚨 Service Issue',
                'strategic_objective': 'Resolve service disruption',
                'framework_used': 'Service Recovery Framework',
                'context_factors': [
                    f'Error: {error_message}',
                    'Multi-engine AI system available but degraded'
                ],
                'tasks': [{
                    'id': 't001',
                    'title': 'Debug service configuration',
                    'description': f'Investigate and resolve: {error_message}',
                    'assignee': 'Engineering Team',
                    'priority': 'critical',
                    'due_date': datetime.now().strftime('%Y-%m-%d'),
                    'estimated_hours': 2,
                    'strategic_rationale': 'Service reliability critical for PM demos'
                }],
                'success_metrics': ['Service restored to full functionality'],
                'risk_factors': ['Demo quality impacted until resolution']
            },
            'meta': {
                'engine': 'service_error',
                'response_time': 0.001,
                'timestamp': datetime.now().isoformat()
            }
        }

# Initialize service
demo_service = PM33MultiEngineService()

# Routes
@app.route('/')
def home():
    return render_template('strategic_command_center.html')

@app.route('/demo')
def demo():
    """Legacy clickable demo - redirect to main interface"""
    return render_template('clickable_demo.html')

@app.route('/mockup')
def mockup():
    return render_template('mockup_demo.html')

@app.route('/health')
def health_check():
    return jsonify(demo_service.get_health_status())

@app.route('/api/mock-strategic-response', methods=['POST'])
def strategic_response():
    """Strategic response endpoint with multi-engine intelligence"""
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Handle simple greetings and casual inputs with clear indication
        casual_inputs = ['hi', 'hello', 'hey', 'test', 'what\'s up', 'dude', 'sup', 'yo', 'howdy']
        casual_phrases = ['sun is shining', 'nice weather', 'good morning', 'good day', 'how are you']
        vague_inputs = ['how about it', 'what do you think', 'thoughts', 'hmm', 'ok', 'sure', 'yeah', 'interesting']
        
        question_lower = question.lower().strip()
        
        # Check if it's casual conversation or too vague for strategic analysis
        if ((len(question) < 25 and question_lower in casual_inputs) or 
            question_lower in casual_phrases or 
            question_lower in vague_inputs):
            return jsonify({
                'response': f'👋 Hello! I received: "{question}". I\'m PM33\'s Strategic AI Co-Pilot. For strategic analysis, ask questions about competitive strategy, resource allocation, market positioning, etc.',
                'workflow': {
                    'id': 'greeting',
                    'name': '💬 Ready for Strategic Questions',
                    'strategic_objective': 'Provide strategic PM guidance',
                    'framework_used': 'Conversational Interface',
                    'context_factors': [
                        'PM33 Multi-Engine AI System active',
                        'Company context loaded and ready',
                        'Intelligent engine selection available',
                        'Optimized for performance/quality/cost'
                    ],
                    'tasks': [{
                        'id': 'suggest1',
                        'title': 'Try a strategic question',
                        'description': 'Example: "Our competitor launched features with 10x funding. Strategic response?"',
                        'assignee': 'You',
                        'priority': 'medium',
                        'due_date': datetime.now().strftime('%Y-%m-%d'),
                        'estimated_hours': 0,
                        'strategic_rationale': 'Strategic questions get intelligent AI analysis'
                    }],
                    'success_metrics': ['Ask a strategic PM question'],
                    'risk_factors': []
                }
            })
        
        # Generate strategic response using multi-engine system
        result = demo_service.generate_strategic_response(question)
        
        print(f"✅ Response generated successfully")
        print(f"🎯 === REQUEST COMPLETE ===\n")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Service error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎯 PM33 Multi-Engine Demo Service")
    print("🌐 Demo URL: http://localhost:8000")
    print("🤖 Intelligent AI engine selection (Groq/OpenAI/Anthropic/Together)")
    print("⚡ Optimized for performance/quality/cost with context preservation")
    print("📋 Health check: http://localhost:8000/health")
    print("🔍 Full request logging enabled")
    
    if demo_service.initialized:
        app.run(debug=True, host='127.0.0.1', port=8000)
    else:
        print("❌ Multi-engine service failed to initialize")
        print("🔍 Check component status at startup")
        exit(1)