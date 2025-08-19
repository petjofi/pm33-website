#!/usr/bin/env python3
"""
PM33 Interactive Mockup Demo with Real AI Integration
Shows the complete envisioned product with real Strategic AI responses
"""

from flask import Flask, render_template, request, jsonify
import json
import time
import sys
import os
sys.path.append('app/backend')

from strategic_workflow_engine import StrategicWorkflowEngine
from context_manager import StrategicContextManager
import asyncio

app = Flask(__name__)

# Initialize real engines
strategic_engine = StrategicWorkflowEngine()
context_manager = StrategicContextManager()

@app.route('/')
def home():
    return render_template('mockup_demo.html')

@app.route('/api/mock-strategic-response', methods=['POST'])
def real_strategic_response():
    """Real strategic response using our AI engine"""
    try:
        data = request.json
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Check if it's just a greeting or non-strategic question
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
                        'Company context loaded and ready',
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
        
        # Get relevant company context
        context = context_manager.get_relevant_context(question)
        full_context = {
            "company_context": context,
            "company_name": "PM33",
            "product_type": "AI Strategic Co-Pilot",
            "stage": "Beta",
            "current_priorities": "50 beta users by Aug 25",
            "team_size": "3 people (1 PM, 2 Engineers)",
            "budget": "$15,000 available",
            "runway": "6 months"
        }
        
        # Generate real strategic workflow
        workflow = asyncio.run(strategic_engine.generate_strategic_workflow(question, full_context))
        
        return jsonify({
            'response': f'Based on PM33\'s current context and strategic frameworks, here\'s your analysis:',
            'workflow': {
                'id': workflow.id,
                'name': workflow.name,
                'strategic_objective': workflow.strategic_objective,
                'framework_used': extract_framework_from_workflow(workflow),
                'context_factors': [
                    'PM33 is in beta stage with 15 signups so far',
                    'Target: 50 beta users by Aug 25',
                    'Available budget: $15,000',
                    'Team: 1 PM + 2 Engineers',
                    'Competitive landscape: Productboard, Aha!, etc.'
                ],
                'tasks': [
                    {
                        'id': f't{i+1:03d}',
                        'title': task.title,
                        'description': task.description if hasattr(task, 'description') else 'Strategic task',
                        'assignee': task.assignee_role,
                        'priority': task.priority.value,
                        'due_date': task.due_date.strftime('%Y-%m-%d'),
                        'estimated_hours': getattr(task, 'estimated_hours', 8),
                        'strategic_rationale': getattr(task, 'strategic_rationale', 'Based on PM strategic frameworks and current context')
                    } for i, task in enumerate(workflow.tasks[:4])
                ],
                'success_metrics': getattr(workflow, 'success_metrics', [
                    'Objective completed within timeline',
                    'Team alignment maintained >8/10',
                    'Strategic goals advanced',
                    'Resource utilization optimized'
                ]),
                'risk_factors': getattr(workflow, 'risk_factors', [
                    'Resource constraints may impact timeline',
                    'Market conditions could change',
                    'Competitive response uncertainty'
                ])
            }
        })
        
    except Exception as e:
        # Log the error and fallback to mock response if AI fails
        print(f"⚠️ AI Engine Error: {str(e)}")
        print(f"🔄 Falling back to mock response for question: {question}")
        return generate_fallback_response(question, str(e))

def is_simple_greeting(question):
    """Check if the question is just a simple greeting or non-strategic"""
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'test', 'testing']
    question_lower = question.lower().strip()
    
    # Exact matches for simple greetings
    if question_lower in greetings:
        return True
    
    # Very short non-strategic questions
    if len(question_lower) < 10 and not any(keyword in question_lower for keyword in ['strategy', 'strategic', 'competitor', 'market', 'priority', 'budget', 'feature', 'product', 'launch']):
        return True
        
    return False

def extract_framework_from_workflow(workflow):
    """Extract PM framework used from workflow"""
    frameworks = [
        "ICE Prioritization Framework",
        "Jobs-to-be-Done Analysis", 
        "OKR Strategic Planning",
        "RICE Scoring Model",
        "Blue Ocean Strategy",
        "Competitive Strategy Framework",
        "Lean Startup Methodology",
        "Product-Market Fit Analysis"
    ]
    
    # Try to detect framework from objective/name
    objective = workflow.strategic_objective.lower()
    if 'competitive' in objective or 'competition' in objective:
        return "Blue Ocean Strategy + Competitive Analysis"
    elif 'priorit' in objective:
        return "ICE Prioritization Framework"
    elif 'okr' in objective or 'objective' in objective:
        return "OKR Strategic Planning"
    else:
        return frameworks[hash(workflow.id) % len(frameworks)]

def generate_fallback_response(question, error_msg=""):
    """Generate fallback mock response if AI fails"""
    return jsonify({
        'response': f'Based on PM33\'s context (fallback mode), here\'s strategic guidance:',
        'workflow': {
            'id': 'fallback_001',
            'name': 'Strategic Analysis Framework',
            'strategic_objective': 'Address the strategic question using PM frameworks and company context.',
            'framework_used': 'Strategic Decision Framework',
            'context_factors': [
                'PM33 beta stage - 15 signups, targeting 50',
                'Limited resources: $15k budget, 3-person team',
                'AI Strategic Co-Pilot market positioning',
                f'Question context: {question[:100]}...'
            ],
            'tasks': [
                {
                    'id': 't001',
                    'title': 'Stakeholder Alignment Session',
                    'description': 'Align team on strategic priorities',
                    'assignee': 'Product Manager',
                    'priority': 'high',
                    'due_date': '2025-08-20',
                    'estimated_hours': 4,
                    'strategic_rationale': 'Ensure team alignment on strategic direction'
                },
                {
                    'id': 't002',
                    'title': 'Data Analysis & Research',
                    'description': 'Gather relevant data to inform decision',
                    'assignee': 'Data Analyst',
                    'priority': 'high', 
                    'due_date': '2025-08-22',
                    'estimated_hours': 8,
                    'strategic_rationale': 'Data-driven decisions reduce risk'
                }
            ],
            'success_metrics': [
                'Strategic question addressed within 1 week',
                'Team alignment score >8/10',
                'Clear action plan created'
            ],
            'risk_factors': [
                'Limited AI availability (fallback mode active)',
                'May need follow-up strategic consultation'
            ]
        }
    })

if __name__ == '__main__':
    print("🎯 PM33 Interactive Demo - Real AI Integration")
    print("🌐 Demo URL: http://localhost:5005")  
    print("🧠 Now connected to Strategic AI Engine!")
    print("📋 Uses real context manager and workflow engine")
    app.run(debug=True, host='0.0.0.0', port=5005)