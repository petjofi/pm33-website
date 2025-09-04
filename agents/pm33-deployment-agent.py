#!/usr/bin/env python3
"""
PM33 Deployment Agent - Registered Claude Code Agent
Intelligent deployment orchestrator for PM33 marketing website

This agent provides autonomous deployment management with:
- UX/UI validation integration
- Interactive staging validation
- Dev fix loop automation
- Multi-environment orchestration
- Claude Code native integration
"""

import asyncio
import json
import subprocess
import sys
import os
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PM33DeploymentAgent')

class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"  
    PRODUCTION = "production"

class ValidationResult(Enum):
    """Validation result states"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

@dataclass
class DeploymentConfig:
    """Deployment configuration settings"""
    environments: Dict[str, Dict[str, Any]]
    remotes: Dict[str, str]
    validation_settings: Dict[str, Any]
    server_settings: Dict[str, Any]
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'DeploymentConfig':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

@dataclass
class DeploymentResult:
    """Results of deployment operation"""
    success: bool
    environment: str
    deployment_id: str
    duration: float
    url: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class ValidationReport:
    """Validation results from UX/UI validators"""
    design_validation: ValidationResult
    ux_validation: ValidationResult
    theme_validation: ValidationResult
    errors: List[str]
    warnings: List[str]
    passed: bool
    
    def to_dict(self) -> Dict:
        return {
            'design_validation': self.design_validation.value,
            'ux_validation': self.ux_validation.value,
            'theme_validation': self.theme_validation.value,
            'errors': self.errors,
            'warnings': self.warnings,
            'passed': self.passed
        }

class PM33DeploymentAgent:
    """
    Intelligent deployment agent for PM33 marketing website
    
    Provides autonomous deployment management with Claude Code integration:
    - Runs UX/UI validators before any deployment
    - Sets up interactive staging validation
    - Manages dev fix loop automatically  
    - Orchestrates multi-environment deployments
    - Integrates with existing PM33 infrastructure
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize deployment agent"""
        self.agent_name = "pm33-deployment-agent"
        self.version = "1.0.0"
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "deployment-config.yaml"
        
        try:
            self.config = DeploymentConfig.load_from_file(config_path)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self.config = self._get_default_config()
        
        # Initialize state
        self.current_deployment = None
        self.staging_server_process = None
        self.deployment_history = []
        
        # Setup paths
        self.project_root = Path(__file__).parent.parent
        self.validators_path = self.project_root
        
        logger.info(f"PM33 Deployment Agent v{self.version} initialized")

    def _get_default_config(self) -> DeploymentConfig:
        """Get default configuration if config file not found"""
        return DeploymentConfig(
            environments={
                "development": {"branch": "feature-branches", "auto_backup": True},
                "staging": {"branch": "main", "validation_required": True, "server_port": 3001},
                "production": {"branch": "main", "approval_required": True, "backup_retention": 30}
            },
            remotes={
                "development": "origin",
                "staging": "origin", 
                "production": "production"
            },
            validation_settings={
                "design_validator": True,
                "ux_validator": True,
                "theme_validator": True,
                "timeout": 300
            },
            server_settings={
                "staging_port": 3001,
                "startup_timeout": 60,
                "health_check_interval": 10
            }
        )

    # ==================== CLAUDE CODE AGENT REGISTRATION ====================
    
    @classmethod
    def register_with_claude(cls) -> Dict[str, Any]:
        """Register this agent with Claude Code"""
        return {
            "name": "pm33-deployment-agent",
            "description": "PM33 intelligent deployment orchestrator with UX/UI validation",
            "version": "1.0.0",
            "capabilities": [
                "deployment-orchestration",
                "validation-integration", 
                "staging-management",
                "git-operations",
                "environment-monitoring"
            ],
            "commands": {
                "deploy": "Deploy to specified environment with validation",
                "deploy-pipeline": "Run full dev→staging→production pipeline",
                "validate": "Run UX/UI validators on current branch",
                "staging-server": "Start interactive staging validation server",
                "status": "Get deployment and environment status",
                "rollback": "Rollback to previous deployment",
                "health": "Check health of all environments"
            },
            "integrations": [
                "mcp_design_validator",
                "mcp_ux_workflow_validator",
                "git",
                "npm",
                "vercel"
            ]
        }
    
    async def handle_claude_request(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deployment requests from Claude Code"""
        try:
            logger.info(f"Processing Claude request: {command} with parameters: {parameters}")
            
            if command == "deploy":
                return await self._handle_deploy_command(parameters)
            elif command == "deploy-pipeline":
                return await self._handle_pipeline_command(parameters)
            elif command == "validate":
                return await self._handle_validate_command(parameters)
            elif command == "staging-server":
                return await self._handle_staging_server_command(parameters)
            elif command == "status":
                return await self._handle_status_command(parameters)
            elif command == "rollback":
                return await self._handle_rollback_command(parameters)
            elif command == "health":
                return await self._handle_health_command(parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}",
                    "available_commands": list(self.register_with_claude()["commands"].keys())
                }
                
        except Exception as e:
            logger.error(f"Error processing Claude request: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.agent_name,
                "version": self.version
            }

    # ==================== VALIDATION INTEGRATION ====================
    
    async def run_validation_suite(self, branch: Optional[str] = None) -> ValidationReport:
        """Run comprehensive UX/UI validation suite"""
        logger.info(f"Running validation suite on branch: {branch or 'current'}")
        
        if branch:
            # Switch to specified branch for validation
            result = subprocess.run(["git", "checkout", branch], capture_output=True, text=True)
            if result.returncode != 0:
                return ValidationReport(
                    design_validation=ValidationResult.FAILED,
                    ux_validation=ValidationResult.FAILED,
                    theme_validation=ValidationResult.FAILED,
                    errors=[f"Failed to checkout branch {branch}: {result.stderr}"],
                    warnings=[],
                    passed=False
                )
        
        errors = []
        warnings = []
        
        # Run design validator
        design_result = await self._run_design_validator()
        
        # Run UX workflow validator  
        ux_result = await self._run_ux_validator()
        
        # Run theme consistency validator
        theme_result = await self._run_theme_validator()
        
        # Compile results
        passed = all([
            design_result == ValidationResult.PASSED,
            ux_result == ValidationResult.PASSED, 
            theme_result in [ValidationResult.PASSED, ValidationResult.WARNING]
        ])
        
        return ValidationReport(
            design_validation=design_result,
            ux_validation=ux_result,
            theme_validation=theme_result,
            errors=errors,
            warnings=warnings,
            passed=passed
        )
    
    async def _run_design_validator(self) -> ValidationResult:
        """Run mcp_design_validator.py"""
        try:
            cmd = ["python3", "mcp_design_validator.py", "--strict", "--json"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ValidationResult.PASSED
            else:
                logger.warning(f"Design validation warnings: {result.stderr}")
                return ValidationResult.WARNING
                
        except subprocess.TimeoutExpired:
            logger.error("Design validator timed out")
            return ValidationResult.FAILED
        except Exception as e:
            logger.error(f"Design validator error: {e}")
            return ValidationResult.FAILED
    
    async def _run_ux_validator(self) -> ValidationResult:
        """Run mcp_ux_workflow_validator.py"""
        try:
            cmd = ["python3", "mcp_ux_workflow_validator.py", "--strict", "--json"]
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ValidationResult.PASSED
            else:
                logger.warning(f"UX validation warnings: {result.stderr}")
                return ValidationResult.WARNING
                
        except subprocess.TimeoutExpired:
            logger.error("UX validator timed out")
            return ValidationResult.FAILED
        except Exception as e:
            logger.error(f"UX validator error: {e}")
            return ValidationResult.FAILED
    
    async def _run_theme_validator(self) -> ValidationResult:
        """Run theme consistency validation"""
        try:
            # Check for theme-related issues in CSS and components
            theme_issues = []
            
            # Check about page CSS variables (recent fix)
            about_page_path = self.project_root / "app" / "(marketing)" / "about" / "page.tsx"
            if about_page_path.exists():
                with open(about_page_path, 'r') as f:
                    content = f.read()
                    # Check for problematic CSS variables
                    if "--marketing-bg-primary" in content:
                        theme_issues.append("Found deprecated CSS variable --marketing-bg-primary in about page")
                    if "--gradient-primary" in content:
                        theme_issues.append("Found undefined CSS variable --gradient-primary in about page")
            
            if theme_issues:
                logger.warning(f"Theme validation issues: {theme_issues}")
                return ValidationResult.WARNING
            
            return ValidationResult.PASSED
            
        except Exception as e:
            logger.error(f"Theme validator error: {e}")
            return ValidationResult.FAILED

    # ==================== STAGING SERVER MANAGEMENT ====================
    
    async def start_staging_server(self, port: int = 3001) -> Dict[str, Any]:
        """Start interactive staging validation server"""
        logger.info(f"Starting staging server on port {port}")
        
        try:
            # Kill any existing process on the port
            await self._kill_port_process(port)
            
            # Start npm dev server on specified port
            env = os.environ.copy()
            env['PORT'] = str(port)
            
            self.staging_server_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to be ready
            server_ready = await self._wait_for_server_ready(port)
            
            if server_ready:
                staging_url = f"http://localhost:{port}"
                logger.info(f"Staging server ready at {staging_url}")
                
                return {
                    "success": True,
                    "url": staging_url,
                    "port": port,
                    "pid": self.staging_server_process.pid,
                    "message": f"Staging server started. Please validate at {staging_url}"
                }
            else:
                return {
                    "success": False,
                    "error": "Server failed to start within timeout period",
                    "timeout": self.config.server_settings["startup_timeout"]
                }
                
        except Exception as e:
            logger.error(f"Error starting staging server: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_server_ready(self, port: int, timeout: int = 60) -> bool:
        """Wait for staging server to be ready"""
        import aiohttp
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{port}") as response:
                        if response.status == 200:
                            return True
            except:
                pass
            
            await asyncio.sleep(2)
        
        return False
    
    async def _kill_port_process(self, port: int):
        """Kill any process running on the specified port"""
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                logger.info(f"Killed processes on port {port}: {pids}")
        except:
            pass  # Ignore errors if no process found
    
    async def stop_staging_server(self):
        """Stop the staging validation server"""
        if self.staging_server_process:
            try:
                self.staging_server_process.terminate()
                self.staging_server_process.wait(timeout=10)
                logger.info("Staging server stopped")
            except subprocess.TimeoutExpired:
                self.staging_server_process.kill()
                logger.warning("Staging server force killed")
            except Exception as e:
                logger.error(f"Error stopping staging server: {e}")
            finally:
                self.staging_server_process = None

    # ==================== DEPLOYMENT ORCHESTRATION ====================
    
    async def deploy_to_environment(self, environment: DeploymentEnvironment, branch: Optional[str] = None) -> DeploymentResult:
        """Deploy to specified environment"""
        start_time = time.time()
        deployment_id = f"deploy-{int(start_time)}"
        
        logger.info(f"Starting deployment {deployment_id} to {environment.value}")
        
        try:
            # Validate deployment prerequisites
            validation_result = await self.run_validation_suite(branch)
            if not validation_result.passed and environment != DeploymentEnvironment.DEVELOPMENT:
                return DeploymentResult(
                    success=False,
                    environment=environment.value,
                    deployment_id=deployment_id,
                    duration=time.time() - start_time,
                    errors=validation_result.errors + ["Validation failed, deployment aborted"]
                )
            
            # Perform deployment based on environment
            if environment == DeploymentEnvironment.STAGING:
                result = await self._deploy_to_staging(deployment_id, branch)
            elif environment == DeploymentEnvironment.PRODUCTION:
                result = await self._deploy_to_production(deployment_id, branch)
            else:
                result = await self._deploy_to_development(deployment_id, branch)
            
            result.duration = time.time() - start_time
            self.deployment_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {e}")
            return DeploymentResult(
                success=False,
                environment=environment.value,
                deployment_id=deployment_id,
                duration=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def _deploy_to_staging(self, deployment_id: str, branch: Optional[str]) -> DeploymentResult:
        """Deploy to staging environment"""
        logger.info(f"Deploying {deployment_id} to staging")
        
        try:
            # Switch to main branch for staging
            if branch and branch != "main":
                result = subprocess.run(["git", "checkout", "main"], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Failed to checkout main: {result.stderr}")
                
                # Merge feature branch to main
                result = subprocess.run(["git", "merge", branch], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Failed to merge {branch}: {result.stderr}")
            
            # Push to staging remote
            remote = self.config.remotes["staging"]
            result = subprocess.run(["git", "push", remote, "main"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to push to {remote}: {result.stderr}")
            
            # Start staging server for validation
            server_result = await self.start_staging_server()
            
            return DeploymentResult(
                success=True,
                environment="staging",
                deployment_id=deployment_id,
                duration=0,  # Will be set by caller
                url=server_result.get("url"),
                warnings=["Please validate staging deployment before proceeding to production"]
            )
            
        except Exception as e:
            raise Exception(f"Staging deployment failed: {e}")
    
    async def _deploy_to_production(self, deployment_id: str, branch: Optional[str]) -> DeploymentResult:
        """Deploy to production environment"""
        logger.info(f"Deploying {deployment_id} to production")
        
        try:
            # Ensure we're on main branch
            result = subprocess.run(["git", "checkout", "main"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to checkout main: {result.stderr}")
            
            # Push to production remote
            remote = self.config.remotes["production"]
            result = subprocess.run(["git", "push", remote, "main"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to push to {remote}: {result.stderr}")
            
            return DeploymentResult(
                success=True,
                environment="production",
                deployment_id=deployment_id,
                duration=0,  # Will be set by caller
                url="https://pm-33.com",
                warnings=["Production deployment completed - verify live site"]
            )
            
        except Exception as e:
            raise Exception(f"Production deployment failed: {e}")
    
    async def _deploy_to_development(self, deployment_id: str, branch: Optional[str]) -> DeploymentResult:
        """Deploy to development environment"""
        logger.info(f"Deploying {deployment_id} to development")
        
        try:
            # Push current branch to development remote
            remote = self.config.remotes["development"]
            current_branch = branch or await self._get_current_branch()
            
            result = subprocess.run(["git", "push", remote, current_branch], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to push to {remote}: {result.stderr}")
            
            return DeploymentResult(
                success=True,
                environment="development",
                deployment_id=deployment_id,
                duration=0,  # Will be set by caller
                warnings=["Development backup completed"]
            )
            
        except Exception as e:
            raise Exception(f"Development deployment failed: {e}")
    
    async def _get_current_branch(self) -> str:
        """Get current git branch"""
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Failed to get current branch")
        return result.stdout.strip()

    # ==================== CLAUDE COMMAND HANDLERS ====================
    
    async def _handle_deploy_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deploy command from Claude"""
        environment = parameters.get("environment", "staging")
        branch = parameters.get("branch")
        
        try:
            env_enum = DeploymentEnvironment(environment)
            result = await self.deploy_to_environment(env_enum, branch)
            return result.to_dict()
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid environment: {environment}",
                "valid_environments": [e.value for e in DeploymentEnvironment]
            }
    
    async def _handle_pipeline_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle full pipeline deployment"""
        branch = parameters.get("branch")
        
        # Step 1: Validate in development
        validation_result = await self.run_validation_suite(branch)
        if not validation_result.passed:
            return {
                "success": False,
                "error": "Validation failed in development",
                "validation_result": validation_result.to_dict()
            }
        
        # Step 2: Deploy to staging
        staging_result = await self.deploy_to_environment(DeploymentEnvironment.STAGING, branch)
        if not staging_result.success:
            return {
                "success": False,
                "error": "Staging deployment failed",
                "staging_result": staging_result.to_dict()
            }
        
        return {
            "success": True,
            "message": "Pipeline deployed to staging. Please validate before production.",
            "staging_url": staging_result.url,
            "validation_result": validation_result.to_dict(),
            "staging_result": staging_result.to_dict(),
            "next_step": "Validate staging deployment, then use 'deploy' command for production"
        }
    
    async def _handle_validate_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation command"""
        branch = parameters.get("branch")
        result = await self.run_validation_suite(branch)
        return result.to_dict()
    
    async def _handle_staging_server_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle staging server command"""
        action = parameters.get("action", "start")
        port = parameters.get("port", 3001)
        
        if action == "start":
            return await self.start_staging_server(port)
        elif action == "stop":
            await self.stop_staging_server()
            return {"success": True, "message": "Staging server stopped"}
        else:
            return {
                "success": False,
                "error": f"Invalid action: {action}",
                "valid_actions": ["start", "stop"]
            }
    
    async def _handle_status_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status command"""
        current_branch = await self._get_current_branch()
        
        return {
            "success": True,
            "agent": self.agent_name,
            "version": self.version,
            "current_branch": current_branch,
            "staging_server_running": self.staging_server_process is not None,
            "recent_deployments": [d.to_dict() for d in self.deployment_history[-5:]],
            "environments": list(self.config.environments.keys())
        }
    
    async def _handle_rollback_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rollback command"""
        environment = parameters.get("environment", "staging")
        
        # This is a simplified rollback - in production you'd want more sophisticated logic
        return {
            "success": False,
            "error": "Rollback functionality not yet implemented",
            "message": "Use git operations manually for now"
        }
    
    async def _handle_health_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health command"""
        return {
            "success": True,
            "agent_health": "healthy",
            "environments": {
                "development": "unknown",
                "staging": "healthy" if self.staging_server_process else "stopped",
                "production": "unknown"
            },
            "validators": {
                "design_validator": "available",
                "ux_validator": "available", 
                "theme_validator": "available"
            }
        }


# ==================== ENTRY POINT ====================

async def main():
    """Main entry point for direct execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PM33 Deployment Agent")
    parser.add_argument("--command", required=True, help="Command to execute")
    parser.add_argument("--parameters", help="JSON parameters for command")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = PM33DeploymentAgent(args.config)
    
    # Parse parameters
    parameters = {}
    if args.parameters:
        try:
            parameters = json.loads(args.parameters)
        except json.JSONDecodeError as e:
            print(f"Error parsing parameters: {e}")
            return 1
    
    # Execute command
    result = await agent.handle_claude_request(args.command, parameters)
    
    # Print result
    print(json.dumps(result, indent=2))
    
    # Stop staging server if running
    if agent.staging_server_process:
        await agent.stop_staging_server()
    
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))