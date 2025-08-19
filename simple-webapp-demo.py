#!/usr/bin/env python3
"""
Simple Web App Demo for PM33 Strategic AI Co-Pilot
Works around API timeout issues by using direct engine calls
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.append('app/backend')

from strategic_workflow_engine import StrategicWorkflowEngine
import asyncio
import json

app = Flask(__name__)

# Initialize the strategic engine
engine = StrategicWorkflowEngine()

@app.route('/')
def home():
    return render_template('demo.html')

@app.route('/api/strategic-chat', methods=['POST'])
def strategic_chat():
    try:
        data = request.json
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Context for PM33
        context = {
            "company_name": data.get('company_name', 'Your Company'),
            "product_type": data.get('product_type', 'Your Product'),
            "stage": data.get('stage', 'current_stage')
        }
        
        # Generate strategic workflow
        workflow = asyncio.run(engine.generate_strategic_workflow(question, context))
        
        # Format response for web interface
        response_data = {
            'response': f"Here's your strategic analysis with executable plan:",
            'workflow': {
                'id': workflow.id,
                'name': workflow.name,
                'objective': workflow.strategic_objective,
                'tasks': [
                    {
                        'title': task.title,
                        'assignee': task.assignee_role,
                        'priority': task.priority.value,
                        'due_date': task.due_date.strftime('%m/%d/%Y'),
                        'description': task.description if hasattr(task, 'description') else ''
                    } for task in workflow.tasks[:6]  # First 6 tasks
                ]
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Strategic AI error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    print("🎯 PM33 Strategic AI Co-Pilot Web Demo")
    print("🌐 Starting web server at: http://localhost:5000")
    print("🎤 Demo ready for Product Manager presentations!")
    app.run(debug=True, host='0.0.0.0', port=5001)