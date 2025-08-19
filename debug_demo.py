#!/usr/bin/env python3
"""
Debug version of PM33 demo to isolate the hanging issue
"""

from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>PM33 Debug Demo</title></head>
    <body>
        <h1>🎯 PM33 Debug Demo</h1>
        <p>If you can see this, Flask is working!</p>
        <p><a href="/health">Check Health</a></p>
        <p><a href="/test">Test API</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Flask server working',
        'api_key_loaded': bool(os.getenv('ANTHROPIC_API_KEY'))
    })

@app.route('/test')
def test_ai():
    try:
        import anthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'PM33 test successful'"}]
        )
        
        return jsonify({
            'status': 'success',
            'ai_response': response.content[0].text
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    print("🎯 Starting PM33 Debug Demo...")
    print("🌐 Will run on: http://localhost:8001")
    print("🔍 Testing basic Flask functionality...")
    
    # Test if this hangs too
    app.run(debug=True, host='127.0.0.1', port=8001)