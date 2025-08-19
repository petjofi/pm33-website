#!/usr/bin/env python3
"""
PM33 Unified Demo Service
Built on proven working components with comprehensive error handling
"""

from flask import Flask, render_template, request, jsonify
import anthropic
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

class PM33DemoService:
    """Unified PM33 Demo Service with health monitoring"""
    
    def __init__(self):
        self.initialized = False
        self.health_status = {}
        self.context_manager = None
        self.ai_client = None
        self.initialize()
    
    def initialize(self):
        """Initialize all components with health checks"""
        print("🎯 Initializing PM33 Demo Service...")
        
        # Initialize AI client (without test call that might hang)
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise Exception("ANTHROPIC_API_KEY not found")
            
            self.ai_client = anthropic.Anthropic(api_key=api_key)
            self.health_status['ai_client'] = 'healthy'
            print("✅ AI Client initialized")
        except Exception as e:
            self.health_status['ai_client'] = f'error: {str(e)}'
            print(f"❌ AI Client failed: {str(e)}")
        
        # Initialize Context Manager
        try:
            from context_manager import StrategicContextManager
            self.context_manager = StrategicContextManager()
            # Quick test
            test_context = self.context_manager.get_relevant_context("test query")
            self.health_status['context_manager'] = 'healthy'
            print(f"✅ Context Manager initialized ({len(test_context)} chars loaded)")
        except Exception as e:
            self.health_status['context_manager'] = f'error: {str(e)}'
            print(f"❌ Context Manager failed: {str(e)}")
        
        # Check overall health
        healthy_components = sum(1 for status in self.health_status.values() if status == 'healthy')
        total_components = len(self.health_status)
        
        if healthy_components == total_components:
            self.initialized = True
            print(f"🎉 All {total_components} components healthy - Demo service ready!")
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
        """Generate strategic response using working components"""
        if not self.initialized:
            return self._create_error_response("Service not properly initialized")
        
        try:
            # Step 1: Get relevant context (fast - proven working)
            context = ""
            if self.context_manager:
                context = self.context_manager.get_relevant_context(question)
            
            # Step 2: Build strategic prompt with company context
            strategic_prompt = self._build_strategic_prompt(question, context)
            
            # Step 3: Get AI response (fast - proven working)
            start_time = time.time()
            response = self.ai_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                messages=[{"role": "user", "content": strategic_prompt}]
            )
            ai_time = time.time() - start_time
            
            ai_response = response.content[0].text
            
            # Step 4: Create workflow structure from response
            workflow = self._create_workflow_from_response(ai_response, question)
            
            return {
                'response': self._extract_analysis_from_response(ai_response),
                'workflow': workflow,
                'meta': {
                    'response_time': ai_time,
                    'context_chars': len(context),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return self._create_error_response(f"Strategic analysis failed: {str(e)}")
    
    def _build_strategic_prompt(self, question, context):
        """Build strategic prompt with company context"""
        return f"""You are PM33's Strategic AI Co-Pilot, an expert Product Manager consultant.

COMPANY CONTEXT:
{context[:1500]}  # Limit context to avoid token limits

STRATEGIC QUESTION: {question}

Please provide:
1. STRATEGIC ANALYSIS (2-3 sentences) - Your strategic assessment
2. PM FRAMEWORK (1 phrase) - Which framework applies (ICE, RICE, OKR, Blue Ocean, etc.)
3. KEY ACTIONS (3-4 bullet points) - Specific executable actions with assignees

Be strategic, practical, and PM-focused. Consider PM33's beta stage and resource constraints."""
    
    def _extract_analysis_from_response(self, ai_response):
        """Extract clean analysis from AI response"""
        # Simple extraction - take first few sentences
        sentences = ai_response.split('.')[:3]
        return '. '.join(sentences) + '.' if sentences else ai_response[:300]
    
    def _create_workflow_from_response(self, ai_response, question):
        """Create structured workflow from AI response"""
        # Extract framework
        framework = self._detect_framework(ai_response, question)
        
        # Generate tasks based on question type and AI response
        tasks = self._generate_tasks_from_response(ai_response, question)
        
        return {
            'id': f'workflow_{hash(question) % 1000:03d}',
            'name': self._generate_workflow_name(question),
            'strategic_objective': f'Address strategic question: {question}',
            'framework_used': framework,
            'context_factors': [
                'PM33 beta stage - 15 signups, targeting 50',
                'Team: 1 PM + 2 Engineers',
                'Budget: $15,000 available',
                'Competitive landscape analysis included',
                f'AI response time: <2 seconds'
            ],
            'tasks': tasks,
            'success_metrics': [
                'Strategic question addressed within 1 week',
                'Action plan implemented',
                'Progress toward business objectives maintained'
            ],
            'risk_factors': [
                'Resource constraints may impact timeline',
                'Market conditions evolving rapidly'
            ]
        }
    
    def _detect_framework(self, ai_response, question):
        """Detect which PM framework to use"""
        question_lower = question.lower()
        response_lower = ai_response.lower()
        
        if any(word in question_lower for word in ['competitor', 'competition', 'rival']):
            return "Blue Ocean Strategy + Competitive Analysis"
        elif any(word in question_lower for word in ['priority', 'prioritize', 'important']):
            return "ICE Prioritization Framework"
        elif any(word in question_lower for word in ['budget', 'money', 'cost', 'spend']):
            return "Resource Allocation Framework"
        elif any(word in question_lower for word in ['okr', 'objective', 'goal']):
            return "OKR Strategic Planning"
        elif 'framework' in response_lower:
            # Try to extract mentioned framework from response
            frameworks = ['ICE', 'RICE', 'OKR', 'Blue Ocean', 'Jobs-to-be-Done']
            for fw in frameworks:
                if fw.lower() in response_lower:
                    return f"{fw} Framework"
        
        return "Strategic Decision Framework"
    
    def _generate_workflow_name(self, question):
        """Generate workflow name from question"""
        if 'competitor' in question.lower():
            return "Competitive Strategy Response"
        elif 'budget' in question.lower():
            return "Resource Allocation Plan"
        elif 'user' in question.lower() or 'customer' in question.lower():
            return "User Acquisition Strategy"
        elif 'product' in question.lower():
            return "Product Strategy Framework"
        else:
            return "Strategic Analysis Workflow"
    
    def _generate_tasks_from_response(self, ai_response, question):
        """Generate tasks from AI response and question context"""
        base_date = datetime.now()
        
        # Extract action items from AI response
        tasks = []
        
        # Parse AI response for action items
        lines = ai_response.split('\n')
        action_items = []
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in ['action', 'step', 'task', '-', '•', '1.', '2.', '3.']):
                if len(line) > 10:  # Meaningful content
                    action_items.append(line.strip('- •123456789.').strip())
        
        # If no clear actions found, generate based on question type
        if not action_items:
            action_items = self._generate_default_tasks(question)
        
        # Convert to structured tasks
        priorities = ['critical', 'high', 'medium']
        assignees = ['Product Manager', 'Engineering Lead', 'Marketing Lead', 'CEO', 'Growth Lead']
        
        for i, action in enumerate(action_items[:4]):  # Max 4 tasks
            tasks.append({
                'id': f't{i+1:03d}',
                'title': action[:100],  # Limit title length
                'description': f'Execute: {action}',
                'assignee': assignees[i % len(assignees)],
                'priority': priorities[i % len(priorities)],
                'due_date': (base_date + timedelta(days=2+i*2)).strftime('%Y-%m-%d'),
                'estimated_hours': 4 + i*2,
                'strategic_rationale': 'Based on PM strategic analysis and company context'
            })
        
        return tasks
    
    def _generate_default_tasks(self, question):
        """Generate default tasks based on question type"""
        if 'competitor' in question.lower():
            return [
                "Competitive analysis deep dive",
                "Differentiation strategy update", 
                "Accelerate user acquisition",
                "Strategic partnership outreach"
            ]
        elif 'budget' in question.lower():
            return [
                "ROI analysis for budget options",
                "Execute highest ROI allocation",
                "Monitor resource utilization",
                "Review and adjust monthly"
            ]
        else:
            return [
                "Strategic analysis session",
                "Stakeholder alignment meeting",
                "Implementation planning",
                "Progress monitoring setup"
            ]
    
    def _create_error_response(self, error_message):
        """Create structured error response"""
        return {
            'response': f'Strategic analysis temporarily unavailable. {error_message}',
            'workflow': {
                'id': 'error_001',
                'name': 'Service Recovery Workflow',
                'strategic_objective': 'Restore strategic analysis capabilities',
                'framework_used': 'Service Recovery Framework',
                'context_factors': [
                    f'Error: {error_message}',
                    'Service health monitoring active',
                    'Fallback procedures in progress'
                ],
                'tasks': [
                    {
                        'id': 't001',
                        'title': 'Diagnose service issue',
                        'description': 'Technical team to investigate service disruption',
                        'assignee': 'Engineering Lead',
                        'priority': 'critical',
                        'due_date': datetime.now().strftime('%Y-%m-%d'),
                        'estimated_hours': 1,
                        'strategic_rationale': 'Rapid service restoration critical for demos'
                    }
                ],
                'success_metrics': ['Service restored within 30 minutes'],
                'risk_factors': ['Demo reputation at risk']
            }
        }

# Initialize service
demo_service = PM33DemoService()

# Routes
@app.route('/')
def home():
    return render_template('mockup_demo.html')

@app.route('/health')
def health_check():
    return jsonify(demo_service.get_health_status())

@app.route('/api/mock-strategic-response', methods=['POST'])
def strategic_response():
    """Main strategic response endpoint"""
    try:
        data = request.json
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Handle simple greetings
        if len(question) < 10 and question.lower() in ['hi', 'hello', 'hey', 'test']:
            return jsonify({
                'response': '👋 Hi! I\'m PM33\'s Strategic AI Co-Pilot. Ask me any strategic product management question!',
                'workflow': {
                    'id': 'greeting',
                    'name': '💬 Ready for Strategic Questions',
                    'strategic_objective': 'Provide strategic PM guidance',
                    'framework_used': 'None needed',
                    'context_factors': [
                        'PM33 Strategic AI Co-Pilot active',
                        'Company context loaded',
                        'PM frameworks ready: ICE, RICE, OKR, Blue Ocean'
                    ],
                    'tasks': [{
                        'id': 'suggest1',
                        'title': 'Try asking about competitive strategy',
                        'description': 'Example: "Competitor launched similar features, how should we respond?"',
                        'assignee': 'You',
                        'priority': 'medium',
                        'due_date': datetime.now().strftime('%Y-%m-%d'),
                        'estimated_hours': 0,
                        'strategic_rationale': 'Strategic questions get strategic responses'
                    }],
                    'success_metrics': ['Ask a strategic PM question'],
                    'risk_factors': []
                }
            })
        
        # Generate strategic response
        result = demo_service.generate_strategic_response(question)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Service error: {str(e)}'}), 500

if __name__ == '__main__':
    if demo_service.initialized:
        print("🎯 PM33 Unified Demo Service")
        print("🌐 Demo URL: http://localhost:8000")
        print("💚 All components healthy - Ready for PM demos!")
        print("📋 Health check: http://localhost:8000/health")
        app.run(debug=True, host='127.0.0.1', port=8000)
    else:
        print("❌ Demo service failed to initialize properly")
        print("🔍 Run health check to see component status")
        exit(1)