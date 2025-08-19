#!/usr/bin/env python3
"""
PM33 Quick Demo with Simplified AI Integration
Uses lighter AI calls to avoid timeouts
"""

from flask import Flask, render_template, request, jsonify
import anthropic
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Anthropic client
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ERROR: ANTHROPIC_API_KEY not found in environment!")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)
print(f"✅ Anthropic client initialized with API key: {api_key[:15]}...")

@app.route('/')
def home():
    return render_template('mockup_demo.html')

@app.route('/api/mock-strategic-response', methods=['POST'])
def quick_strategic_response():
    """Quick strategic response with lighter AI calls"""
    try:
        data = request.json
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Check if it's just a greeting
        if is_simple_greeting(question):
            return jsonify({
                'response': '👋 Hi! I\'m your Strategic AI Co-Pilot. Ask me any strategic product management question and I\'ll provide analysis with executable workflows.',
                'workflow': {
                    'id': 'greeting',
                    'name': '💬 Ready for Strategic Questions',
                    'strategic_objective': 'I\'m here to help with strategic product management decisions.',
                    'framework_used': 'None needed',
                    'context_factors': [
                        'PM33 Strategic AI Co-Pilot active',
                        'Company context: Beta stage, targeting 50 users',
                        'PM frameworks available: ICE, RICE, OKR, JTBD, Blue Ocean',
                        'Ready to generate executable workflows'
                    ],
                    'tasks': [
                        {
                            'id': 'suggest1',
                            'title': 'Try asking about competitive strategy',
                            'description': 'Example: "Competitor launched similar features, how should we respond?"',
                            'assignee': 'You',
                            'priority': 'medium',
                            'due_date': '2025-08-15',
                            'estimated_hours': 0,
                            'strategic_rationale': 'Strategic questions get strategic responses'
                        }
                    ],
                    'success_metrics': [
                        'Ask a strategic product management question',
                        'Receive context-aware analysis',
                        'Get executable workflows'
                    ],
                    'risk_factors': []
                }
            })
        
        # Generate quick strategic response
        print(f"🧠 Generating AI response for: {question}")
        print(f"🔑 API Key available: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")
        
        context_prompt = f"""
You are PM33's Strategic AI Co-Pilot. PM33 is a beta-stage AI Strategic Co-Pilot targeting Product Managers.

Company Context:
- Stage: Beta (15 signups, targeting 50 by Aug 25)
- Team: 1 PM + 2 Engineers
- Budget: $15,000 available
- Competitors: Productboard, Aha!, etc.
- Value prop: Replace Transform PMs into PMOs 

Question: {question}

Provide a strategic response with:
1. Brief analysis (2-3 sentences)
2. Suggested framework (ICE, RICE, OKR, Blue Ocean, etc.)
3. 3-4 specific actionable tasks with assignees and priorities

Keep response concise but strategic.
"""
        
        print("🚀 Making API call to Claude...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Use faster model
            max_tokens=500,  # Limit tokens for speed
            messages=[{"role": "user", "content": context_prompt}]
        )
        
        ai_response = response.content[0].text
        print(f"✅ AI Response received: {ai_response[:100]}...")
        print(f"📊 Response length: {len(ai_response)} characters")
        
        # Parse the response and create workflow
        workflow = create_workflow_from_response(ai_response, question)
        
        return jsonify({
            'response': ai_response,
            'workflow': workflow
        })
        
    except Exception as e:
        print(f"⚠️ AI Error: {str(e)}")
        return generate_fallback_response(question, str(e))

def is_simple_greeting(question):
    """Check if the question is just a simple greeting"""
    greetings = ['hi', 'hello', 'hey', 'test', 'testing']
    question_lower = question.lower().strip()
    return question_lower in greetings or len(question_lower) < 5

def create_workflow_from_response(ai_response, question):
    """Create a workflow structure from AI response"""
    
    # Determine framework based on question type
    framework = "Strategic Decision Framework"
    if "competitor" in question.lower():
        framework = "Blue Ocean Strategy + Competitive Analysis"
    elif "budget" in question.lower() or "priorit" in question.lower():
        framework = "ICE Prioritization Framework"
    elif "market" in question.lower():
        framework = "Jobs-to-be-Done Analysis"
    
    # Generate tasks based on question type
    tasks = []
    base_date = datetime.now()
    
    if "competitor" in question.lower():
        tasks = [
            {
                'id': 't001',
                'title': 'Competitive Analysis Deep Dive',
                'description': 'Analyze competitor features vs PM33 unique capabilities',
                'assignee': 'Product Manager',
                'priority': 'high',
                'due_date': (base_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                'estimated_hours': 8,
                'strategic_rationale': 'Understand competitive positioning'
            },
            {
                'id': 't002',
                'title': 'Differentiation Strategy Update',
                'description': 'Refine messaging around strategic AI advantage',
                'assignee': 'Marketing Lead',
                'priority': 'critical',
                'due_date': (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'estimated_hours': 6,
                'strategic_rationale': 'Clear differentiation messaging'
            },
            {
                'id': 't003',
                'title': 'Accelerate User Acquisition',
                'description': 'Fast-track beta user outreach to 50 users',
                'assignee': 'Growth Lead',
                'priority': 'critical',
                'due_date': (base_date + timedelta(days=10)).strftime('%Y-%m-%d'),
                'estimated_hours': 20,
                'strategic_rationale': 'First-mover advantage in AI PM tools'
            }
        ]
    elif "budget" in question.lower():
        tasks = [
            {
                'id': 't001',
                'title': 'ROI Analysis: Marketing vs Development',
                'description': 'Calculate expected ROI for budget allocation options',
                'assignee': 'Product Manager',
                'priority': 'high',
                'due_date': (base_date + timedelta(days=2)).strftime('%Y-%m-%d'),
                'estimated_hours': 4,
                'strategic_rationale': 'Data-driven budget decisions'
            },
            {
                'id': 't002',
                'title': 'Execute Highest ROI Option',
                'description': 'Implement the budget allocation with best expected returns',
                'assignee': 'CEO',
                'priority': 'critical',
                'due_date': (base_date + timedelta(days=7)).strftime('%Y-%m-%d'),
                'estimated_hours': 16,
                'strategic_rationale': 'Maximize limited resources impact'
            }
        ]
    else:
        tasks = [
            {
                'id': 't001',
                'title': 'Strategic Analysis Session',
                'description': 'Deep dive analysis of the strategic question',
                'assignee': 'Product Manager',
                'priority': 'high',
                'due_date': (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
                'estimated_hours': 6,
                'strategic_rationale': 'Thorough strategic thinking required'
            },
            {
                'id': 't002',
                'title': 'Implementation Planning',
                'description': 'Create detailed execution plan',
                'assignee': 'Team Lead',
                'priority': 'high',
                'due_date': (base_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                'estimated_hours': 8,
                'strategic_rationale': 'Strategic plans need execution'
            }
        ]
    
    return {
        'id': f'workflow_{hash(question) % 1000:03d}',
        'name': 'PM33 Strategic Response Workflow',
        'strategic_objective': f'Address the strategic question: {question[:100]}...',
        'framework_used': framework,
        'context_factors': [
            'PM33 beta stage - 15 signups, targeting 50',
            'Limited resources: $15k budget, 3-person team',
            'AI Strategic Co-Pilot market positioning',
            'Competitive landscape: Productboard, Aha!, etc.'
        ],
        'tasks': tasks,
        'success_metrics': [
            'Strategic question addressed within 1 week',
            'Action plan implemented',
            'Progress toward 50 beta users maintained'
        ],
        'risk_factors': [
            'Resource constraints may impact timeline',
            'Market conditions evolving rapidly'
        ]
    }

def generate_fallback_response(question, error_msg=""):
    """Generate fallback response if AI fails"""
    return jsonify({
        'response': f'Strategic analysis in progress... (Fallback mode active)',
        'workflow': {
            'id': 'fallback_001',
            'name': 'Strategic Analysis Framework (Offline Mode)',
            'strategic_objective': 'Address strategic question with available frameworks.',
            'framework_used': 'Strategic Decision Framework',
            'context_factors': [
                'PM33 beta stage - 15 signups, targeting 50',
                'Limited resources: $15k budget, 3-person team',
                'AI engine temporarily unavailable'
            ],
            'tasks': [
                {
                    'id': 't001',
                    'title': 'Manual Strategic Analysis',
                    'description': 'Conduct offline strategic analysis',
                    'assignee': 'Product Manager',
                    'priority': 'high',
                    'due_date': '2025-08-18',
                    'estimated_hours': 4,
                    'strategic_rationale': 'AI engine needs troubleshooting'
                }
            ],
            'success_metrics': ['Strategic analysis completed manually'],
            'risk_factors': ['AI engine downtime affecting response quality']
        }
    })

if __name__ == '__main__':
    print("🎯 PM33 Quick Demo - Optimized AI Integration")
    print("🌐 Demo URL: http://localhost:5007")
    print("⚡ Uses Claude Haiku for faster responses")
    print("🧠 Lighter AI calls to avoid timeouts")
    app.run(debug=True, host='127.0.0.1', port=5007)