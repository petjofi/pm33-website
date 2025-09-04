#!/usr/bin/env python3
"""
PM33 Validation Orchestrator
Orchestrates existing UX/UI validators for deployment pipeline integration
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging


class ValidationOrchestrator:
    """Orchestrates PM33's existing UX/UI validation systems for deployment pipeline"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.design_validator_path = self.project_root / "mcp_design_validator.py"
        self.ux_validator_path = self.project_root / "mcp_ux_workflow_validator.py"
        
        # Validation results storage
        self.results = {
            "design": {},
            "ux": {},
            "combined": {},
            "timestamp": None
        }
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
    async def validate_development_environment(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run comprehensive validation on development environment
        
        Args:
            paths: Specific paths to validate, or None for full project
            
        Returns:
            Dict with validation results and recommendations
        """
        self.logger.info("🔍 Starting development environment validation")
        
        # Default paths for comprehensive validation
        if paths is None:
            paths = [
                "app/(marketing)/about/page.tsx",
                "components/shared/",
                "app/globals.css",
                "components/ui/",
                "app/(marketing)/",
            ]
        
        validation_results = {
            "design_validation": {},
            "ux_validation": {},
            "overall_score": 0,
            "deployment_ready": False,
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Run design validation
        design_results = await self._run_design_validation(paths)
        validation_results["design_validation"] = design_results
        
        # Run UX workflow validation
        ux_results = await self._run_ux_validation(paths)
        validation_results["ux_validation"] = ux_results
        
        # Calculate overall score and deployment readiness
        validation_results.update(
            self._calculate_overall_results(design_results, ux_results)
        )
        
        # Store results
        self.results["design"] = design_results
        self.results["ux"] = ux_results
        self.results["combined"] = validation_results
        self.results["timestamp"] = time.time()
        
        return validation_results
    
    async def _run_design_validation(self, paths: List[str]) -> Dict[str, Any]:
        """Run design validation using existing mcp_design_validator.py"""
        
        design_results = {
            "files_validated": 0,
            "violations": [],
            "score": 0,
            "inline_coding_violations": [],
            "theme_issues": [],
            "success": False
        }
        
        try:
            for path in paths:
                file_path = self.project_root / path
                
                if file_path.is_file():
                    # Validate individual file
                    result = await self._validate_design_file(str(file_path))
                    design_results["files_validated"] += 1
                    
                elif file_path.is_dir():
                    # Validate directory recursively
                    for tsx_file in file_path.rglob("*.tsx"):
                        result = await self._validate_design_file(str(tsx_file))
                        design_results["files_validated"] += 1
            
            # Run comprehensive design validation
            comprehensive_result = await self._run_comprehensive_design_validation()
            design_results.update(comprehensive_result)
            
            design_results["success"] = True
            
        except Exception as e:
            self.logger.error(f"❌ Design validation failed: {e}")
            design_results["error"] = str(e)
            
        return design_results
    
    async def _validate_design_file(self, file_path: str) -> Dict[str, Any]:
        """Validate individual file with design validator"""
        
        cmd = [
            sys.executable,
            str(self.design_validator_path),
            file_path,
            "--strict",
            "--json"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse JSON response
                return json.loads(stdout.decode())
            else:
                return {
                    "file": file_path,
                    "error": stderr.decode() if stderr else "Validation failed",
                    "success": False
                }
                
        except Exception as e:
            return {
                "file": file_path,
                "error": str(e),
                "success": False
            }
    
    async def _run_comprehensive_design_validation(self) -> Dict[str, Any]:
        """Run comprehensive design validation with inline coding enforcement"""
        
        # Design contract validation
        design_cmd = [
            sys.executable,
            str(self.design_validator_path),
            "app/frontend/components",
            "--recursive",
            "--strict",
            "--json"
        ]
        
        # Inline coding enforcement
        inline_cmd = [
            sys.executable,
            str(self.design_validator_path),
            "app/frontend/components",
            "--recursive",
            "--inline-coding-enforcement",
            "--json"
        ]
        
        results = {
            "design_contract_compliance": {},
            "inline_coding_compliance": {},
            "overall_compliance": 0
        }
        
        try:
            # Run design contract validation
            design_process = await asyncio.create_subprocess_exec(
                *design_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            design_stdout, design_stderr = await design_process.communicate()
            
            if design_process.returncode == 0:
                results["design_contract_compliance"] = json.loads(design_stdout.decode())
            
            # Run inline coding validation
            inline_process = await asyncio.create_subprocess_exec(
                *inline_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            inline_stdout, inline_stderr = await inline_process.communicate()
            
            if inline_process.returncode == 0:
                results["inline_coding_compliance"] = json.loads(inline_stdout.decode())
            
        except Exception as e:
            results["error"] = str(e)
            
        return results
    
    async def _run_ux_validation(self, paths: List[str]) -> Dict[str, Any]:
        """Run UX workflow validation using existing mcp_ux_workflow_validator.py"""
        
        ux_results = {
            "files_validated": 0,
            "workflow_violations": [],
            "accessibility_issues": [],
            "user_experience_score": 0,
            "success": False
        }
        
        try:
            for path in paths:
                file_path = self.project_root / path
                
                if file_path.is_file() and file_path.suffix in ['.tsx', '.ts']:
                    result = await self._validate_ux_file(str(file_path))
                    ux_results["files_validated"] += 1
                    
                elif file_path.is_dir():
                    for tsx_file in file_path.rglob("*.tsx"):
                        result = await self._validate_ux_file(str(tsx_file))
                        ux_results["files_validated"] += 1
            
            # Run comprehensive UX validation
            comprehensive_result = await self._run_comprehensive_ux_validation()
            ux_results.update(comprehensive_result)
            
            ux_results["success"] = True
            
        except Exception as e:
            self.logger.error(f"❌ UX validation failed: {e}")
            ux_results["error"] = str(e)
            
        return ux_results
    
    async def _validate_ux_file(self, file_path: str) -> Dict[str, Any]:
        """Validate individual file with UX validator"""
        
        cmd = [
            sys.executable,
            str(self.ux_validator_path),
            file_path,
            "--strict",
            "--json"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                return {
                    "file": file_path,
                    "error": stderr.decode() if stderr else "UX validation failed",
                    "success": False
                }
                
        except Exception as e:
            return {
                "file": file_path,
                "error": str(e),
                "success": False
            }
    
    async def _run_comprehensive_ux_validation(self) -> Dict[str, Any]:
        """Run comprehensive UX workflow validation"""
        
        cmd = [
            sys.executable,
            str(self.ux_validator_path),
            "app/frontend/components",
            "--recursive",
            "--strict",
            "--json"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                return {
                    "error": stderr.decode() if stderr else "Comprehensive UX validation failed",
                    "success": False
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def _calculate_overall_results(self, design_results: Dict[str, Any], ux_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall validation score and deployment readiness"""
        
        # Calculate weighted scores
        design_score = design_results.get("score", 0)
        ux_score = ux_results.get("user_experience_score", 0)
        
        # Weighted average (design: 60%, UX: 40%)
        overall_score = (design_score * 0.6) + (ux_score * 0.4)
        
        # Determine deployment readiness
        deployment_ready = (
            overall_score >= 85 and
            design_results.get("success", False) and
            ux_results.get("success", False) and
            len(design_results.get("violations", [])) == 0 and
            len(ux_results.get("workflow_violations", [])) == 0
        )
        
        # Compile critical issues
        critical_issues = []
        critical_issues.extend(design_results.get("violations", []))
        critical_issues.extend(ux_results.get("workflow_violations", []))
        critical_issues.extend(design_results.get("inline_coding_violations", []))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(design_results, ux_results, overall_score)
        
        return {
            "overall_score": round(overall_score, 1),
            "deployment_ready": deployment_ready,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "design_score": design_score,
            "ux_score": ux_score
        }
    
    def _generate_recommendations(self, design_results: Dict[str, Any], ux_results: Dict[str, Any], overall_score: float) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Design recommendations
        if design_results.get("violations"):
            recommendations.append("🎨 Fix design contract violations before deployment")
            
        if design_results.get("inline_coding_violations"):
            recommendations.append("🚫 Remove inline coding violations - use CSS design tokens")
            
        if design_results.get("theme_issues"):
            recommendations.append("🌙 Fix theme switching issues for consistent light/dark mode")
        
        # UX recommendations
        if ux_results.get("workflow_violations"):
            recommendations.append("👤 Address UX workflow violations for better user experience")
            
        if ux_results.get("accessibility_issues"):
            recommendations.append("♿ Fix accessibility issues for WCAG 2.1 AA compliance")
        
        # Overall score recommendations
        if overall_score < 70:
            recommendations.append("⚠️ Score too low for deployment - address critical issues first")
        elif overall_score < 85:
            recommendations.append("📈 Good progress - resolve remaining issues for deployment readiness")
        elif overall_score >= 85:
            recommendations.append("✅ Excellent score - ready for staging deployment")
            
        return recommendations
    
    async def get_validation_status(self) -> Dict[str, Any]:
        """Get current validation status and results"""
        
        if not self.results["timestamp"]:
            return {
                "status": "no_validation_run",
                "message": "No validation has been run yet"
            }
        
        age_minutes = (time.time() - self.results["timestamp"]) / 60
        
        return {
            "status": "valid" if age_minutes < 30 else "stale",
            "age_minutes": round(age_minutes, 1),
            "last_results": self.results["combined"],
            "design_results": self.results["design"],
            "ux_results": self.results["ux"]
        }
    
    async def pre_deployment_validation(self, environment: str = "staging") -> Tuple[bool, Dict[str, Any]]:
        """
        Run pre-deployment validation specific to environment
        
        Returns:
            Tuple of (deployment_approved, detailed_results)
        """
        
        self.logger.info(f"🚀 Running pre-deployment validation for {environment}")
        
        # Run comprehensive validation
        results = await self.validate_development_environment()
        
        # Environment-specific thresholds
        thresholds = {
            "staging": {"min_score": 75, "allow_warnings": True},
            "production": {"min_score": 90, "allow_warnings": False}
        }
        
        threshold = thresholds.get(environment, thresholds["staging"])
        
        # Determine approval
        deployment_approved = (
            results["overall_score"] >= threshold["min_score"] and
            len(results["critical_issues"]) == 0 and
            (threshold["allow_warnings"] or len(results["warnings"]) == 0)
        )
        
        # Add environment-specific recommendations
        if not deployment_approved:
            results["recommendations"].append(
                f"❌ Not approved for {environment} deployment - address issues above"
            )
        else:
            results["recommendations"].append(
                f"✅ Approved for {environment} deployment"
            )
        
        return deployment_approved, results


# ==================== VALIDATION UTILITIES ====================

async def quick_validation_check(project_root: str) -> Dict[str, Any]:
    """Quick validation check for development workflow"""
    
    orchestrator = ValidationOrchestrator(Path(project_root))
    
    # Focus on critical files that commonly have issues
    critical_paths = [
        "app/(marketing)/about/page.tsx",  # Known theme issues
        "app/globals.css",                 # CSS variables
        "components/shared/ThemeProvider.tsx"  # Theme system
    ]
    
    return await orchestrator.validate_development_environment(critical_paths)


async def staging_readiness_check(project_root: str) -> Tuple[bool, Dict[str, Any]]:
    """Check if codebase is ready for staging deployment"""
    
    orchestrator = ValidationOrchestrator(Path(project_root))
    return await orchestrator.pre_deployment_validation("staging")


async def production_readiness_check(project_root: str) -> Tuple[bool, Dict[str, Any]]:
    """Check if codebase is ready for production deployment"""
    
    orchestrator = ValidationOrchestrator(Path(project_root))
    return await orchestrator.pre_deployment_validation("production")


# ==================== DIRECT EXECUTION SUPPORT ====================

def main():
    """Direct execution interface for validation orchestrator"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="PM33 Validation Orchestrator")
    parser.add_argument("command", choices=["validate", "quick", "staging", "production"], 
                       help="Validation command to run")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def run_command():
        if args.command == "validate":
            orchestrator = ValidationOrchestrator(Path(args.project_root))
            return await orchestrator.validate_development_environment()
            
        elif args.command == "quick":
            return await quick_validation_check(args.project_root)
            
        elif args.command == "staging":
            approved, results = await staging_readiness_check(args.project_root)
            results["deployment_approved"] = approved
            return results
            
        elif args.command == "production":
            approved, results = await production_readiness_check(args.project_root)
            results["deployment_approved"] = approved
            return results
    
    # Execute command
    result = asyncio.run(run_command())
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"✅ Validation Score: {result.get('overall_score', 0)}/100")
        print(f"🚀 Deployment Ready: {result.get('deployment_ready', False)}")
        
        if result.get('critical_issues'):
            print(f"\n❌ Critical Issues ({len(result['critical_issues'])}):")
            for issue in result['critical_issues'][:5]:  # Show first 5
                print(f"  • {issue}")
                
        if result.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in result['recommendations'][:3]:  # Show first 3
                print(f"  • {rec}")
    
    # Exit code based on deployment readiness
    return 0 if result.get('deployment_ready', False) else 1


if __name__ == "__main__":
    sys.exit(main())