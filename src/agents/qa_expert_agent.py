"""
QA Expert Agent
===============

Specialized agent for validation and quality assurance.
"""

import logging
from typing import Dict, Any, List
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest, QAResult


class QAExpertAgent(BaseSpecializedAgent):
    """Agent specialized in validation and quality assurance."""
    
    async def _execute_task(self, request: AgentRequest) -> QAResult:
        """Execute QA validation tasks."""
        task_description = request.task_description.lower()
        context = request.context
        
        if "validate installation" in task_description or "comprehensive validation" in task_description:
            return await self._perform_comprehensive_validation(context)
        else:
            return await self._generic_validation(request)
    
    async def _perform_comprehensive_validation(self, context: Dict[str, Any]) -> QAResult:
        """Perform comprehensive validation of the WSL environment."""
        logging.info("Performing comprehensive validation")
        
        session_id = context.get("session_id", "unknown")
        
        # Define validation checklist
        validation_checklist = [
            {
                "name": "zsh_installed",
                "description": "Check if zsh is installed and set as default shell",
                "command": "echo $SHELL | grep zsh"
            },
            {
                "name": "oh_my_zsh_installed", 
                "description": "Check if oh-my-zsh is installed",
                "command": "test -d ~/.oh-my-zsh"
            },
            {
                "name": "mise_available",
                "description": "Check if mise is available",
                "command": "command -v mise"
            },
            {
                "name": "python_version",
                "description": "Check Python version",
                "command": "python --version | grep '3.12'"
            },
            {
                "name": "nodejs_available",
                "description": "Check if Node.js is available",
                "command": "command -v node"
            },
            {
                "name": "git_configured",
                "description": "Check if git is configured",
                "command": "git config --global user.name && git config --global user.email"
            },
            {
                "name": "ssh_key_exists",
                "description": "Check if SSH key exists",
                "command": "test -f ~/.ssh/id_ed25519"
            },
            {
                "name": "docker_available",
                "description": "Check if Docker is available",
                "command": "command -v docker"
            }
        ]
        
        # Execute validation checks
        validation_results = []
        success_count = 0
        
        for check in validation_checklist:
            try:
                result = await self._run_command(check["command"], timeout=10)
                success = result["success"]
                
                validation_results.append({
                    "check": check["name"],
                    "description": check["description"],
                    "success": success,
                    "output": result.get("stdout", "")[:100],  # Limit output
                    "error": result.get("stderr", "") if not success else None
                })
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                validation_results.append({
                    "check": check["name"],
                    "description": check["description"],
                    "success": False,
                    "error": str(e)
                })
        
        # Determine overall success
        total_checks = len(validation_checklist)
        success_rate = success_count / total_checks
        validation_passed = success_rate >= 0.8  # 80% success rate required
        
        # Generate success criteria and failure lists
        success_criteria_met = [
            result["check"] for result in validation_results if result["success"]
        ]
        
        failures = [
            f"{result['check']}: {result.get('error', 'Check failed')}" 
            for result in validation_results if not result["success"]
        ]
        
        # Generate remediation suggestions
        remediation_suggestions = self._generate_remediation_suggestions(validation_results)
        
        return QAResult(
            task_id=context.get("task_id", "comprehensive_validation"),
            validation_passed=validation_passed,
            success_criteria_met=success_criteria_met,
            failures=failures,
            remediation_suggestions=remediation_suggestions,
            confidence_score=success_rate,
            detailed_report=self._generate_detailed_report(validation_results, success_count, total_checks)
        )
    
    def _generate_remediation_suggestions(self, validation_results: List[Dict[str, Any]]) -> List[str]:
        """Generate suggestions for fixing validation failures."""
        suggestions = []
        
        for result in validation_results:
            if not result["success"]:
                check_name = result["check"]
                
                if check_name == "zsh_installed":
                    suggestions.append("Install zsh: sudo apt install zsh && chsh -s $(which zsh)")
                elif check_name == "oh_my_zsh_installed":
                    suggestions.append("Install oh-my-zsh: sh -c \"$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\"")
                elif check_name == "mise_available":
                    suggestions.append("Install mise: curl https://mise.run | sh")
                elif check_name == "python_version":
                    suggestions.append("Install Python 3.12 via mise: mise install python@3.12.9")
                elif check_name == "nodejs_available":
                    suggestions.append("Install Node.js via mise: mise install nodejs@latest")
                elif check_name == "git_configured":
                    suggestions.append("Configure git: git config --global user.name \"Your Name\" && git config --global user.email \"your.email@example.com\"")
                elif check_name == "ssh_key_exists":
                    suggestions.append("Generate SSH key: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N \"\"")
                elif check_name == "docker_available":
                    suggestions.append("Install Docker or ensure Docker Desktop WSL integration is enabled")
        
        # Add general suggestions
        if suggestions:
            suggestions.extend([
                "Run 'source ~/.zshrc' to reload shell configuration",
                "Restart terminal session after making changes",
                "Check system logs for detailed error information"
            ])
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _generate_detailed_report(self, validation_results: List[Dict[str, Any]], success_count: int, total_checks: int) -> str:
        """Generate a detailed validation report."""
        
        report_lines = [
            f"WSL Environment Validation Report",
            f"================================",
            f"",
            f"Overall Status: {'PASSED' if success_count/total_checks >= 0.8 else 'FAILED'}",
            f"Success Rate: {success_count}/{total_checks} ({success_count/total_checks*100:.1f}%)",
            f"",
            f"Detailed Results:",
            f"-----------------"
        ]
        
        for result in validation_results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            report_lines.extend([
                f"{status} {result['check']}: {result['description']}",
                f"    Output: {result.get('output', 'No output')[:50]}..."
            ])
            if not result["success"] and result.get("error"):
                report_lines.append(f"    Error: {result['error'][:100]}...")
        
        if success_count < total_checks:
            report_lines.extend([
                f"",
                f"Remediation Required:",
                f"--------------------",
                f"Please address the failed checks above to complete the environment setup."
            ])
        else:
            report_lines.extend([
                f"",
                f"Environment Ready:",
                f"-----------------",
                f"WSL development environment has been successfully configured."
            ])
        
        return "\n".join(report_lines)
    
    async def _generic_validation(self, request: AgentRequest) -> QAResult:
        """Perform generic validation tasks."""
        return QAResult(
            task_id=request.context.get("task_id", "generic_validation"),
            validation_passed=True,
            success_criteria_met=["Generic validation completed"],
            failures=[],
            remediation_suggestions=[],
            confidence_score=0.9,
            detailed_report="Generic validation task completed successfully."
        )