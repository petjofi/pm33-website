#!/usr/bin/env python3
"""
PM33 MCP Server - Think Hard, Answer Short Implementation
"""

import asyncio
import json
import sys
from typing import Dict, List, Any
import anthropic
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class PM33McpServer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key and api_key != 'your_api_key_here':
            self.claude = anthropic.Anthropic(api_key=api_key)
        else:
            self.claude = None
            
        self.think_hard_prefix = """
        THINK HARD: Analyze thoroughly but respond concisely.
        Consider: context, implications, trade-offs, risks, opportunities.
        OUTPUT: Brief, actionable insight only.
        """
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "pm33-analyze-ai-project": {
                                    "description": "Analyze AI project status with think hard, answer short principle"
                                }
                            }
                        },
                        "serverInfo": {
                            "name": "pm33-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "pm33-analyze-ai-project",
                                "description": "Analyze AI project status and provide concise actionable insights",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "project_name": {
                                            "type": "string",
                                            "description": "Name of the AI project to analyze"
                                        }
                                    },
                                    "required": ["project_name"]
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "pm33-analyze-ai-project":
                    result = await self.analyze_ai_project(arguments.get("project_name", ""))
                    return {
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
            
            return {
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
        except Exception as e:
            return {
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def analyze_ai_project(self, project_name: str) -> str:
        """Core MCP command - think hard, answer short"""
        
        if not self.claude:
            return """**Status**: Red - No API key configured
**Key Issue**: Missing ANTHROPIC_API_KEY in environment
**Action**: Set API key in .env file
**Timeline**: Immediate fix needed"""
        
        if not project_name:
            return """**Status**: Red - No project specified
**Key Issue**: Missing project name parameter
**Action**: Provide project name to analyze
**Timeline**: Immediate"""
        
        prompt = self.think_hard_prefix + f"""
        AI Project Analysis Request: {project_name}
        
        Analyze this AI project thoroughly but respond in exactly this format:
        **Status**: [Red/Yellow/Green] - [one sentence status]
        **Key Issue**: [main blocker or concern]
        **Action**: [specific next step]
        **Timeline**: [weeks to meaningful impact]
        
        Think deeply about: technical risks, market timing, resource constraints, competitive landscape.
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            return f"""**Status**: Red - API Error
**Key Issue**: {str(e)}
**Action**: Check API key and connection
**Timeline**: Immediate fix needed"""

async def main():
    """Run MCP server with stdio transport"""
    server = PM33McpServer()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(json.dumps({
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }))
            sys.stdout.flush()

if __name__ == "__main__":
    print("PM33 MCP Server starting...", file=sys.stderr)
    asyncio.run(main())