#!/usr/bin/env python3
"""
PM33 Staging Server Manager
Manages staging server lifecycle for interactive user validation
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
import psutil
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict


@dataclass
class ServerStatus:
    """Server status data structure"""
    pid: Optional[int] = None
    port: int = 3001
    status: str = "stopped"  # stopped, starting, running, error, stopping
    url: Optional[str] = None
    health_check_url: Optional[str] = None
    startup_time: Optional[float] = None
    last_health_check: Optional[float] = None
    error_message: Optional[str] = None


class StagingServerManager:
    """Manages PM33 staging server for interactive validation workflows"""
    
    def __init__(self, project_root: Path, port: int = 3001):
        self.project_root = Path(project_root)
        self.port = port
        self.status = ServerStatus(port=port)
        self.process: Optional[subprocess.Popen] = None
        
        # Server configuration
        self.startup_timeout = 60  # seconds
        self.health_check_timeout = 10  # seconds
        self.health_check_interval = 5  # seconds
        self.max_startup_retries = 3
        
        # Health check endpoints
        self.health_endpoints = [
            {"path": "/", "expected_status": 200},
            {"path": "/about", "expected_status": 200},
            {"path": "/pricing", "expected_status": 200}
        ]
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Build server URLs
        self.status.url = f"http://localhost:{self.port}"
        self.status.health_check_url = f"{self.status.url}/api/health"
    
    async def start_staging_server(self, branch: Optional[str] = None, build_first: bool = True) -> Dict[str, Any]:
        """
        Start staging server with optional branch checkout and build
        
        Args:
            branch: Git branch to checkout before starting
            build_first: Whether to run build before starting server
            
        Returns:
            Dict with server status and startup results
        """
        
        self.logger.info(f"🚀 Starting staging server on port {self.port}")
        
        if self.status.status == "running":
            return {
                "success": True,
                "message": f"Staging server already running on {self.status.url}",
                "status": asdict(self.status)
            }
        
        startup_results = {
            "success": False,
            "branch_checkout": None,
            "build_result": None,
            "server_start": None,
            "health_check": None,
            "final_status": None
        }
        
        try:
            # Step 1: Checkout branch if specified
            if branch:
                checkout_result = await self._checkout_branch(branch)
                startup_results["branch_checkout"] = checkout_result
                
                if not checkout_result.get("success"):
                    return {**startup_results, "error": "Branch checkout failed"}
            
            # Step 2: Build if requested
            if build_first:
                build_result = await self._build_project()
                startup_results["build_result"] = build_result
                
                if not build_result.get("success"):
                    return {**startup_results, "error": "Build failed"}
            
            # Step 3: Start server
            server_result = await self._start_development_server()
            startup_results["server_start"] = server_result
            
            if not server_result.get("success"):
                return {**startup_results, "error": "Server start failed"}
            
            # Step 4: Wait for server to be ready
            health_result = await self._wait_for_server_ready()
            startup_results["health_check"] = health_result
            
            if health_result.get("success"):
                startup_results["success"] = True
                startup_results["final_status"] = asdict(self.status)
                
                self.logger.info(f"✅ Staging server ready: {self.status.url}")
                
                return startup_results
            else:
                await self._cleanup_failed_server()
                return {**startup_results, "error": "Health check failed"}
                
        except Exception as e:
            self.logger.error(f"❌ Server startup failed: {e}")
            await self._cleanup_failed_server()
            
            return {
                **startup_results,
                "error": str(e),
                "final_status": asdict(self.status)
            }
    
    async def stop_staging_server(self, force: bool = False) -> Dict[str, Any]:
        """
        Stop staging server gracefully or forcefully
        
        Args:
            force: Whether to force-kill the process
            
        Returns:
            Dict with stop results
        """
        
        if self.status.status == "stopped":
            return {
                "success": True,
                "message": "Staging server was already stopped",
                "status": asdict(self.status)
            }
        
        self.logger.info(f"🛑 Stopping staging server (PID: {self.status.pid})")
        
        self.status.status = "stopping"
        
        try:
            if self.process:
                if force:
                    self.process.kill()
                else:
                    self.process.terminate()
                
                # Wait for process to stop
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process_stop()),
                        timeout=10
                    )
                except asyncio.TimeoutError:
                    self.logger.warning("Process didn't stop gracefully, force killing")
                    self.process.kill()
                    await self._wait_for_process_stop()
            
            # Clean up process references
            self.process = None
            self.status.pid = None
            self.status.status = "stopped"
            self.status.startup_time = None
            self.status.last_health_check = None
            self.status.error_message = None
            
            self.logger.info("✅ Staging server stopped successfully")
            
            return {
                "success": True,
                "message": "Staging server stopped successfully",
                "status": asdict(self.status)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping server: {e}")
            
            self.status.status = "error"
            self.status.error_message = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "status": asdict(self.status)
            }
    
    async def get_server_status(self, run_health_check: bool = True) -> Dict[str, Any]:
        """
        Get current server status with optional health check
        
        Args:
            run_health_check: Whether to run fresh health check
            
        Returns:
            Dict with current server status
        """
        
        # Check if process is still running
        if self.status.pid and not self._is_process_running(self.status.pid):
            self.status.status = "stopped"
            self.status.pid = None
            self.status.error_message = "Process died unexpectedly"
        
        # Run health check if requested and server is supposed to be running
        if run_health_check and self.status.status == "running":
            health_result = await self._run_health_check()
            
            if not health_result.get("success"):
                self.status.status = "error"
                self.status.error_message = health_result.get("error", "Health check failed")
        
        return {
            "status": asdict(self.status),
            "uptime_seconds": time.time() - self.status.startup_time if self.status.startup_time else 0,
            "is_accessible": self.status.status == "running"
        }
    
    async def run_interactive_validation(self, validation_timeout: int = 300) -> Dict[str, Any]:
        """
        Run interactive validation session with user feedback
        
        Args:
            validation_timeout: Timeout for user validation in seconds
            
        Returns:
            Dict with validation results and user feedback
        """
        
        self.logger.info("🔍 Starting interactive validation session")
        
        if self.status.status != "running":
            return {
                "success": False,
                "error": "Staging server is not running",
                "status": asdict(self.status)
            }
        
        validation_results = {
            "server_url": self.status.url,
            "validation_pages": [],
            "user_feedback_pending": True,
            "validation_timeout": validation_timeout,
            "instructions": [
                f"🌐 Navigate to {self.status.url}",
                "🔍 Test all critical pages and functionality",
                "🌙 Test both light and dark theme modes",
                "📱 Test responsive design on mobile/tablet",
                "✅ Report any issues found"
            ]
        }
        
        # Test critical pages
        for endpoint in self.health_endpoints:
            page_url = f"{self.status.url}{endpoint['path']}"
            page_result = await self._test_page_accessibility(page_url)
            
            validation_results["validation_pages"].append({
                "url": page_url,
                "path": endpoint["path"],
                "accessible": page_result.get("success", False),
                "response_time": page_result.get("response_time", 0),
                "status_code": page_result.get("status_code", 0)
            })
        
        return validation_results
    
    async def _checkout_branch(self, branch: str) -> Dict[str, Any]:
        """Checkout specified git branch"""
        
        self.logger.info(f"🌿 Checking out branch: {branch}")
        
        try:
            # Check if branch exists locally
            check_cmd = ["git", "branch", "--list", branch]
            check_process = await asyncio.create_subprocess_exec(
                *check_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            check_stdout, _ = await check_process.communicate()
            branch_exists_locally = bool(check_stdout.decode().strip())
            
            # Checkout command
            if branch_exists_locally:
                checkout_cmd = ["git", "checkout", branch]
            else:
                checkout_cmd = ["git", "checkout", "-b", branch, f"origin/{branch}"]
            
            process = await asyncio.create_subprocess_exec(
                *checkout_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "branch": branch,
                    "message": f"Successfully checked out {branch}",
                    "output": stdout.decode()
                }
            else:
                return {
                    "success": False,
                    "branch": branch,
                    "error": stderr.decode(),
                    "output": stdout.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "branch": branch,
                "error": str(e)
            }
    
    async def _build_project(self) -> Dict[str, Any]:
        """Build the project before starting server"""
        
        self.logger.info("🔨 Building project...")
        
        try:
            build_cmd = ["npm", "run", "build"]
            
            process = await asyncio.create_subprocess_exec(
                *build_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": "Build completed successfully",
                    "output": stdout.decode()[-1000:]  # Last 1000 chars
                }
            else:
                return {
                    "success": False,
                    "error": "Build failed",
                    "output": stderr.decode()[-1000:]  # Last 1000 chars
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _start_development_server(self) -> Dict[str, Any]:
        """Start the Next.js development server"""
        
        self.logger.info(f"🚀 Starting development server on port {self.port}")
        
        try:
            # Kill any existing process on the port
            await self._kill_process_on_port(self.port)
            
            # Start new server process
            server_cmd = ["npm", "run", "dev"]
            env = os.environ.copy()
            env["PORT"] = str(self.port)
            
            self.process = subprocess.Popen(
                server_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root),
                env=env,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            self.status.pid = self.process.pid
            self.status.status = "starting"
            self.status.startup_time = time.time()
            
            return {
                "success": True,
                "pid": self.status.pid,
                "port": self.port,
                "message": f"Server process started (PID: {self.status.pid})"
            }
            
        except Exception as e:
            self.status.status = "error"
            self.status.error_message = str(e)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_server_ready(self) -> Dict[str, Any]:
        """Wait for server to be ready and respond to health checks"""
        
        self.logger.info("⏳ Waiting for server to be ready...")
        
        start_time = time.time()
        retry_count = 0
        
        while (time.time() - start_time) < self.startup_timeout:
            retry_count += 1
            
            # Check if process is still running
            if not self._is_process_running(self.status.pid):
                return {
                    "success": False,
                    "error": "Server process died during startup",
                    "retry_count": retry_count
                }
            
            # Try health check
            health_result = await self._run_health_check()
            
            if health_result.get("success"):
                self.status.status = "running"
                self.status.last_health_check = time.time()
                
                return {
                    "success": True,
                    "startup_time": time.time() - start_time,
                    "retry_count": retry_count,
                    "health_result": health_result
                }
            
            # Wait before retry
            await asyncio.sleep(self.health_check_interval)
        
        # Timeout reached
        return {
            "success": False,
            "error": f"Server startup timeout ({self.startup_timeout}s)",
            "retry_count": retry_count
        }
    
    async def _run_health_check(self) -> Dict[str, Any]:
        """Run health check against server endpoints"""
        
        health_results = {
            "success": False,
            "endpoints_checked": 0,
            "endpoints_healthy": 0,
            "response_times": [],
            "errors": []
        }
        
        try:
            for endpoint in self.health_endpoints:
                url = f"{self.status.url}{endpoint['path']}"
                expected_status = endpoint["expected_status"]
                
                health_results["endpoints_checked"] += 1
                
                try:
                    start_time = time.time()
                    
                    response = requests.get(
                        url,
                        timeout=self.health_check_timeout,
                        allow_redirects=True
                    )
                    
                    response_time = time.time() - start_time
                    health_results["response_times"].append(response_time)
                    
                    if response.status_code == expected_status:
                        health_results["endpoints_healthy"] += 1
                    else:
                        health_results["errors"].append(
                            f"{url}: Expected {expected_status}, got {response.status_code}"
                        )
                        
                except Exception as e:
                    health_results["errors"].append(f"{url}: {str(e)}")
            
            # Determine overall success
            health_results["success"] = (
                health_results["endpoints_healthy"] == health_results["endpoints_checked"]
            )
            
            if health_results["response_times"]:
                health_results["avg_response_time"] = sum(health_results["response_times"]) / len(health_results["response_times"])
            
            return health_results
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                **health_results
            }
    
    async def _test_page_accessibility(self, url: str) -> Dict[str, Any]:
        """Test if a specific page is accessible"""
        
        try:
            start_time = time.time()
            
            response = requests.get(url, timeout=self.health_check_timeout)
            response_time = time.time() - start_time
            
            return {
                "success": response.status_code == 200,
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "content_length": len(response.content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    def _is_process_running(self, pid: Optional[int]) -> bool:
        """Check if process with given PID is running"""
        
        if not pid:
            return False
        
        try:
            return psutil.pid_exists(pid)
        except:
            return False
    
    async def _wait_for_process_stop(self):
        """Wait for process to stop"""
        
        if not self.process:
            return
        
        while self.process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def _kill_process_on_port(self, port: int):
        """Kill any process running on the specified port"""
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            self.logger.info(f"Killing process {proc.info['pid']} on port {port}")
                            proc.kill()
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            self.logger.warning(f"Error killing process on port {port}: {e}")
    
    async def _cleanup_failed_server(self):
        """Clean up after failed server startup"""
        
        self.status.status = "error"
        
        if self.process:
            try:
                self.process.kill()
            except:
                pass
            self.process = None
        
        self.status.pid = None


# ==================== STAGING UTILITIES ====================

async def start_interactive_staging(project_root: str, port: int = 3001, branch: Optional[str] = None) -> Dict[str, Any]:
    """Start interactive staging server for user validation"""
    
    manager = StagingServerManager(Path(project_root), port)
    
    # Start server
    start_result = await manager.start_staging_server(branch=branch, build_first=True)
    
    if not start_result.get("success"):
        return start_result
    
    # Begin interactive validation
    validation_result = await manager.run_interactive_validation()
    
    return {
        **start_result,
        "validation": validation_result,
        "next_steps": [
            f"🌐 Visit {manager.status.url} to test the application",
            "🔍 Verify all functionality works as expected",
            "🌙 Test both light and dark modes",
            "📱 Check responsive design",
            "✅ Report any issues for dev environment fixes"
        ]
    }


async def stop_staging_server(project_root: str, port: int = 3001) -> Dict[str, Any]:
    """Stop staging server"""
    
    manager = StagingServerManager(Path(project_root), port)
    
    # Get current status to find PID
    status = await manager.get_server_status(run_health_check=False)
    
    if status["status"]["status"] == "stopped":
        return status
    
    return await manager.stop_staging_server()


async def get_staging_status(project_root: str, port: int = 3001) -> Dict[str, Any]:
    """Get staging server status"""
    
    manager = StagingServerManager(Path(project_root), port)
    return await manager.get_server_status()


# ==================== DIRECT EXECUTION SUPPORT ====================

def main():
    """Direct execution interface for staging server manager"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="PM33 Staging Server Manager")
    parser.add_argument("command", choices=["start", "stop", "status", "interactive"], 
                       help="Server management command")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--port", type=int, default=3001, help="Server port")
    parser.add_argument("--branch", help="Git branch to checkout")
    parser.add_argument("--no-build", action="store_true", help="Skip build step")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def run_command():
        if args.command == "start":
            manager = StagingServerManager(Path(args.project_root), args.port)
            return await manager.start_staging_server(
                branch=args.branch,
                build_first=not args.no_build
            )
            
        elif args.command == "stop":
            return await stop_staging_server(args.project_root, args.port)
            
        elif args.command == "status":
            return await get_staging_status(args.project_root, args.port)
            
        elif args.command == "interactive":
            return await start_interactive_staging(
                args.project_root, 
                args.port, 
                args.branch
            )
    
    # Execute command
    result = asyncio.run(run_command())
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print(f"✅ {result.get('message', 'Command completed successfully')}")
            
            if result.get('status', {}).get('url'):
                print(f"🌐 URL: {result['status']['url']}")
                
            if result.get('next_steps'):
                print("\n📋 Next Steps:")
                for step in result['next_steps']:
                    print(f"  {step}")
        else:
            print(f"❌ Error: {result.get('error', 'Command failed')}")
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())