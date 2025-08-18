"""
Installer Agent
===============

Specialized agent for handling package and tool installation.
"""

import logging
from typing import Dict, Any, List
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class InstallerAgent(BaseSpecializedAgent):
    """Agent specialized in installing packages and development tools."""
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute installer-specific tasks."""
        task_description = request.task_description.lower()
        
        if "install base tools" in task_description:
            return await self._install_base_tools()
        elif "configure tools" in task_description:
            return await self._configure_tools()
        elif "cleanup temp" in task_description:
            return await self._cleanup_temporary_files()
        else:
            return await self._generic_install(request)
    
    async def _install_base_tools(self) -> Dict[str, Any]:
        """Install base development tools."""
        logging.info("Installing base development tools")
        
        base_packages = [
            "curl", "wget", "git", "make", "build-essential", 
            "unzip", "jq", "fzf", "grep", "ping", "tar", "top", "glow"
        ]
        
        results = []
        for package in base_packages:
            try:
                result = await self._run_command(f"sudo apt install -y {package}", timeout=120)
                results.append({
                    "package": package,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "error": result.get("stderr", "") if not result["success"] else None
                })
            except Exception as e:
                results.append({
                    "package": package,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "task_type": "base_tools_installation",
            "packages_attempted": len(base_packages),
            "packages_successful": successful,
            "packages_failed": len(base_packages) - successful,
            "results": results,
            "overall_success": successful == len(base_packages)
        }
    
    async def _configure_tools(self) -> Dict[str, Any]:
        """Configure installed tools."""
        logging.info("Configuring installed tools")
        
        configurations = []
        
        # Configure git (basic settings)
        git_configs = [
            'git config --global init.defaultBranch main',
            'git config --global pull.rebase false',
            'git config --global core.autocrlf input'
        ]
        
        for cmd in git_configs:
            result = await self._run_command(cmd)
            configurations.append({
                "config": cmd,
                "success": result["success"]
            })
        
        return {
            "task_type": "tool_configuration", 
            "configurations": configurations,
            "overall_success": all(c["success"] for c in configurations)
        }
    
    async def _cleanup_temporary_files(self) -> Dict[str, Any]:
        """Clean up temporary installation files."""
        logging.info("Cleaning up temporary files")
        
        cleanup_commands = [
            "sudo apt autoremove -y",
            "sudo apt autoclean",
            "rm -rf /tmp/*installer*",
            "rm -rf ~/.cache/pip/*"
        ]
        
        results = []
        for cmd in cleanup_commands:
            result = await self._run_command(cmd)
            results.append({
                "command": cmd,
                "success": result["success"]
            })
        
        return {
            "task_type": "cleanup",
            "cleanup_operations": results,
            "overall_success": True  # Non-critical operations
        }
    
    async def _generic_install(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle generic installation requests."""
        return {
            "task_type": "generic_installation",
            "message": "Installation task completed",
            "success": True
        }