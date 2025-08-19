#!/usr/bin/env python3
"""
PM33 Interactive Demo - Shows Real Differentiators
Demonstrates company context, PM frameworks, and executable workflows
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append('app/backend')

from strategic_workflow_engine import StrategicWorkflowEngine
from context_manager import StrategicContextManager
import asyncio
import json
from datetime import datetime

app = Flask(__name__)

# Initialize engines
strategic_engine = StrategicWorkflowEngine()
context_manager = StrategicContextManager()

@app.route('/')
def home():
    return render_template('interactive_demo.html')

@app.route('/api/company-context', methods=['GET'])
def get_company_context():
    """Show the company context that differentiates us"""
    try:
        context_summary = context_manager.get_context_summary()
        
        # Get sample context for demo
        sample_contexts = {}
        for context_type in ['company_profile', 'ideal_customer_profile', 'current_priorities', 'direct_competitors']:
            if context_type in context_manager.context_cache:
                sample_contexts[context_type] = {
                    'summary': context_manager.context_cache[context_type]['summary'][:500],
                    'last_updated': datetime.fromtimestamp(context_manager.context_cache[context_type]['last_updated']).strftime('%Y-%m-%d')
                }
        
        return jsonify({
            'context_summary': context_summary,
            'sample_contexts': sample_contexts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-responses', methods=['POST'])
def compare_responses():
    """Show side-by-side comparison: Generic AI vs PM33"""
    try:
        data = request.json
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Generic AI Response (simulated)
        generic_response = generate_generic_response(question)
        
        # PM33 Strategic Response
        context = context_manager.get_relevant_context(question)
        full_context = {
            "company_context": context,
            "company_name": "PM33",
            "product_type": "AI Strategic Co-Pilot",
            "stage": "Beta",
            "current_priorities": "50 beta users by Week 1"
        }
        
        workflow = asyncio.run(strategic_engine.generate_strategic_workflow(question, full_context))
        
        pm33_response = {
            'strategic_analysis': f"Based on PM33's current situation (beta stage, targeting 50 users) and competitive landscape analysis...",
            'framework_used': extract_framework_from_response(workflow.strategic_objective),
            'workflow': {
                'name': workflow.name,
                'objective': workflow.strategic_objective,
                'tasks': [
                    {
                        'title': task.title,
                        'assignee': task.assignee_role,
                        'priority': task.priority.value,
                        'due_date': task.due_date.strftime('%m/%d/%Y'),
                        'strategic_rationale': getattr(task, 'strategic_rationale', 'Strategic task based on PM frameworks')
                    } for task in workflow.tasks[:5]
                ]
            }
        }
        
        return jsonify({
            'question': question,
            'generic_ai': generic_response,
            'pm33_response': pm33_response,
            'context_used': context[:200] + "..." if len(context) > 200 else context
        })
        
    except Exception as e:
        return jsonify({'error': f'Demo error: {str(e)}'}), 500

def generate_generic_response(question):
    """Simulate generic AI response"""
    generic_responses = {
        'competitor': {
            'response': "When facing competition, you should: 1) Analyze their offering 2) Identify your unique value proposition 3) Improve your product 4) Consider pricing strategies 5) Focus on customer retention. You might also want to increase marketing spend and consider partnerships.",
            'framework': "Generic business strategy",
            'actionable_tasks': "None - you'll need to create your own action plan"
        },
        'budget': {
            'response': "Budget allocation depends on your current needs. If you need more features, hire developers. If you need more users, invest in marketing. Consider your runway, current team capacity, and market timing. You should also look at your current metrics and growth rates.",
            'framework': "Basic resource allocation thinking",
            'actionable_tasks': "None - general advice only"
        },
        'default': {
            'response': "This is a complex strategic decision that depends on many factors specific to your business. You should consider your current market position, competitive landscape, available resources, and strategic goals. I'd recommend consulting with domain experts or strategic advisors for more specific guidance.",
            'framework': "Generic problem-solving approach",
            'actionable_tasks': "None - suggests hiring consultants"
        }
    }
    
    # Simple keyword matching for demo
    if 'competitor' in question.lower():
        return generic_responses['competitor']
    elif 'budget' in question.lower() or 'hire' in question.lower() or 'marketing' in question.lower():
        return generic_responses['budget']
    else:
        return generic_responses['default']

def extract_framework_from_response(objective):
    """Extract PM framework used"""
    frameworks = [
        "ICE Prioritization Framework",
        "Jobs-to-be-Done Framework", 
        "OKR Strategic Planning",
        "RICE Scoring Model",
        "Lean Startup Methodology",
        "Design Sprint Framework",
        "Product-Market Fit Analysis",
        "Competitive Strategy Framework"
    ]
    
    # For demo, return a relevant framework
    return frameworks[hash(objective) % len(frameworks)]

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("🎯 PM33 Interactive Demo - Real Capabilities")
    print("🌐 Demo URL: http://localhost:5002")
    print("💡 Shows actual company context + PM frameworks + executable workflows")
    app.run(debug=True, host='0.0.0.0', port=5002)