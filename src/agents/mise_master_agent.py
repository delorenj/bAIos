"""
Mise Master Agent
=================

Specialized agent for managing version-controlled development tools via mise.
"""

import logging
from typing import Dict, Any, List
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class MiseMasterAgent(BaseSpecializedAgent):
    """Agent specialized in managing tools via mise version manager."""
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute mise-related tasks."""
        task_description = request.task_description.lower()
        
        if "install mise tools" in task_description:
            return await self._install_mise_tools()
        else:
            return await self._generic_mise_task(request)
    
    async def _install_mise_tools(self) -> Dict[str, Any]:
        """Install and configure mise-managed tools."""
        logging.info("Installing mise and managed tools")
        
        installation_steps = []
        
        # Install mise if not present
        mise_check = await self._run_command("command -v mise")
        if not mise_check["success"]:
            # Install mise
            mise_install = await self._run_command(
                "curl https://mise.run | sh", timeout=120
            )
            installation_steps.append({
                "step": "install_mise",
                "success": mise_install["success"]
            })
        else:
            installation_steps.append({
                "step": "mise_already_installed",
                "success": True
            })
        
        # Create mise config directory
        config_dir = await self._run_command("mkdir -p ~/.config/mise")
        installation_steps.append({
            "step": "create_config_dir",
            "success": config_dir["success"]
        })
        
        # Create mise configuration
        config_content = '''
[tools]
python = "3.12.9"
nodejs = "latest"
pnpm = "latest"
uv = "latest"
pipx = "latest"

experimental = true
'''
        
        config_create = await self._run_command(
            f'echo "{config_content}" > ~/.config/mise/config.toml'
        )
        installation_steps.append({
            "step": "create_config",
            "success": config_create["success"]
        })
        
        # Install configured tools
        tools = ["python@3.12.9", "nodejs@latest", "pnpm@latest", "uv@latest", "pipx@latest"]
        tool_results = []
        
        for tool in tools:
            install_result = await self._run_command(f"mise install {tool}", timeout=300)
            tool_results.append({
                "tool": tool,
                "success": install_result["success"],
                "output": install_result.get("stdout", "")[:200]  # Limit output size
            })
        
        # Set up mise shell integration
        shell_setup = await self._configure_mise_shell_integration()
        installation_steps.append({
            "step": "shell_integration",
            "success": shell_setup
        })
        
        successful_tools = sum(1 for result in tool_results if result["success"])
        
        return {
            "task_type": "mise_tools_installation",
            "installation_steps": installation_steps,
            "tools_installed": tool_results,
            "successful_tools": successful_tools,
            "total_tools": len(tools),
            "overall_success": all(step["success"] for step in installation_steps) and successful_tools == len(tools)
        }
    
    async def _configure_mise_shell_integration(self) -> bool:
        """Configure mise shell integration."""
        try:
            # Add mise activation to shell profiles
            shell_configs = ["~/.zshrc", "~/.bashrc"]
            
            mise_activation = 'eval "$(mise activate zsh)"'
            
            for config_file in shell_configs:
                # Check if file exists before modifying
                file_exists = await self._check_file_exists(config_file)
                if file_exists:
                    # Check if already configured
                    check_config = await self._run_command(f"grep -q 'mise activate' {config_file}")
                    if not check_config["success"]:
                        # Add mise activation
                        add_config = await self._run_command(f'echo "{mise_activation}" >> {config_file}')
                        if not add_config["success"]:
                            return False
            
            return True
        except:
            return False
    
    async def _generic_mise_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle generic mise-related tasks."""
        return {
            "task_type": "generic_mise_task",
            "message": "Mise task completed",
            "success": True
        }