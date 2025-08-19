#!/usr/bin/env python3
"""
PM33 Interactive Mockup Demo
Shows the complete envisioned product with clickable interactions
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
        # Fallback to mock response if AI fails
        return generate_fallback_response(question, str(e))

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
    print("🌐 Demo URL: http://localhost:5003")  
    print("🧠 Now connected to Strategic AI Engine!")
    app.run(debug=True, host='0.0.0.0', port=5003)
                'strategic_objective': 'Establish clear competitive advantage within 8 weeks by leveraging our AI-native approach while competitors are still building basic features.',
                'framework_used': 'Blue Ocean Strategy + Jobs-to-be-Done Analysis',
                'context_factors': [
                    'PM33 is in beta stage with 15 signups so far',
                    'Main competitor: Productboard (Series C, $100M+ funding)',
                    'Our advantage: Strategic AI + executable workflows',
                    'Current runway: 6 months at current burn rate'
                ],
                'tasks': [
                    {
                        'id': 't001',
                        'title': 'Competitive Feature Gap Analysis',
                        'description': 'Analyze competitor features vs PM33 unique capabilities',
                        'assignee': 'Product Manager',
                        'priority': 'high',
                        'due_date': '2025-08-20',
                        'estimated_hours': 8,
                        'strategic_rationale': 'Understand where we can\'t compete vs where we dominate'
                    },
                    {
                        'id': 't002', 
                        'title': 'Double Down on Strategic AI Messaging',
                        'description': 'Refine messaging around "PMO transformation" value prop',
                        'assignee': 'Marketing Lead',
                        'priority': 'critical',
                        'due_date': '2025-08-18',
                        'estimated_hours': 12,
                        'strategic_rationale': 'Differentiate on strategic intelligence, not features'
                    },
                    {
                        'id': 't003',
                        'title': 'Accelerate Beta User Acquisition',
                        'description': 'Reach 50 beta users before competitor gains momentum',
                        'assignee': 'Growth Lead',
                        'priority': 'critical', 
                        'due_date': '2025-08-25',
                        'estimated_hours': 40,
                        'strategic_rationale': 'First-mover advantage in AI strategic PM tools'
                    },
                    {
                        'id': 't004',
                        'title': 'Strategic Partnership Outreach',
                        'description': 'Partner with PM communities and thought leaders',
                        'assignee': 'Business Development',
                        'priority': 'medium',
                        'due_date': '2025-08-30',
                        'estimated_hours': 20,
                        'strategic_rationale': 'Build distribution moat while competitor focuses on product'
                    }
                ],
                'success_metrics': [
                    '50 active beta users by Aug 25',
                    '80% of users ask >3 strategic questions/week',
                    '90% positive feedback on strategic advice quality',
                    '20% beta-to-paid conversion intent'
                ],
                'risk_factors': [
                    'Competitor may copy our messaging approach',
                    'Limited runway for extended competition',
                    'Beta users may churn if competitor launches first'
                ]
            }
        })
    
    elif 'budget' in question or 'hire' in question or 'marketing' in question:
        return jsonify({
            'response': 'Based on your current metrics and strategic priorities, here\'s your resource allocation framework:',
            'workflow': {
                'id': 'resource_allocation_001',
                'name': 'Beta50 Resource Optimization Plan', 
                'strategic_objective': 'Achieve 50 beta users within 2 weeks by optimizing resource allocation between product development and user acquisition.',
                'framework_used': 'ICE Prioritization + Growth Accounting Model',
                'context_factors': [
                    'Current team: 1 PM + 2 engineers',
                    'Available budget: $15,000',
                    'Goal: 50 beta users by Aug 25',
                    'Current conversion: LinkedIn outreach 15%'
                ],
                'tasks': [
                    {
                        'id': 't005',
                        'title': 'Invest 70% Budget in Targeted LinkedIn Ads',
                        'description': 'Run LinkedIn ads targeting Senior PMs at Series A-C companies',
                        'assignee': 'Growth Lead',
                        'priority': 'critical',
                        'due_date': '2025-08-17',
                        'estimated_hours': 16,
                        'strategic_rationale': 'Higher ROI than hiring at current stage'
                    },
                    {
                        'id': 't006',
                        'title': 'Hire Part-time Marketing Specialist',
                        'description': 'Bring in experienced SaaS marketing specialist for 20h/week',
                        'assignee': 'CEO',
                        'priority': 'high',
                        'due_date': '2025-08-19',
                        'estimated_hours': 8,
                        'strategic_rationale': 'Marketing expertise gap is limiting growth'
                    },
                    {
                        'id': 't007',
                        'title': 'Defer Non-Critical Feature Development',
                        'description': 'Focus engineering on demo stability, defer advanced features',
                        'assignee': 'Engineering Lead',
                        'priority': 'medium',
                        'due_date': '2025-08-18',
                        'estimated_hours': 4,
                        'strategic_rationale': 'User acquisition more critical than feature expansion'
                    }
                ],
                'success_metrics': [
                    'Cost per beta signup <$300',
                    '50 beta signups by Aug 25',
                    '70% of budget allocated to growth vs development',
                    'Part-time marketer hired within 1 week'
                ],
                'risk_factors': [
                    'Ad performance may be lower than projected',
                    'Product stability issues during user influx',
                    'Engineering team capacity constraints'
                ]
            }
        })
    
    else:
        return jsonify({
            'response': 'Based on your company context and strategic frameworks, here\'s your analysis:',
            'workflow': {
                'id': 'strategic_analysis_001',
                'name': 'Strategic Decision Framework',
                'strategic_objective': 'Make data-driven strategic decisions that align with PM33\'s current stage and market position.',
                'framework_used': 'Strategic Decision Tree + OKR Alignment',
                'context_factors': [
                    'Early-stage startup with limited resources',
                    'AI-native product in emerging market',
                    'Strong technical team, growing user interest'
                ],
                'tasks': [
                    {
                        'id': 't008',
                        'title': 'Stakeholder Alignment Session',
                        'description': 'Align team on strategic priorities and trade-offs',
                        'assignee': 'Product Manager',
                        'priority': 'high',
                        'due_date': '2025-08-18',
                        'estimated_hours': 4,
                        'strategic_rationale': 'Ensure team alignment on strategic direction'
                    },
                    {
                        'id': 't009',
                        'title': 'Data Collection & Analysis',
                        'description': 'Gather relevant metrics to inform decision',
                        'assignee': 'Data Analyst',
                        'priority': 'high',
                        'due_date': '2025-08-20',
                        'estimated_hours': 12,
                        'strategic_rationale': 'Data-driven decisions reduce strategic risk'
                    }
                ],
                'success_metrics': [
                    'Decision made within 1 week',
                    'Team alignment score >8/10',
                    'Implementation plan created'
                ],
                'risk_factors': [
                    'Analysis paralysis',
                    'Conflicting stakeholder priorities'
                ]
            }
        })

if __name__ == '__main__':
    print("🎯 PM33 Interactive Mockup Demo")
    print("🌐 Demo URL: http://localhost:5003")  
    print("💡 Complete product vision with clickable interactions")
    app.run(debug=True, host='0.0.0.0', port=5003)