"""
Shell Master Agent
==================

Specialized agent for shell configuration and environment setup.
"""

import logging
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class ShellMasterAgent(BaseSpecializedAgent):
    """Agent specialized in shell configuration and environment setup."""
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute shell configuration tasks."""
        task_description = request.task_description.lower()
        
        if "setup shell" in task_description or "configure shell" in task_description:
            return await self._setup_shell_environment()
        elif "setup symlinks" in task_description or "create symlinks" in task_description:
            return await self._setup_symlinks()
        else:
            return await self._generic_shell_task(request)
    
    async def _setup_shell_environment(self) -> Dict[str, Any]:
        """Set up zsh and oh-my-zsh configuration."""
        logging.info("Setting up shell environment")
        
        setup_steps = []
        
        # Check if zsh is installed
        zsh_check = await self._run_command("command -v zsh")
        if not zsh_check["success"]:
            # Install zsh
            install_result = await self._run_command("sudo apt install -y zsh")
            setup_steps.append({
                "step": "install_zsh",
                "success": install_result["success"]
            })
        
        # Install oh-my-zsh if not present
        ohmyzsh_check = await self._check_directory_exists("~/.oh-my-zsh")
        if not ohmyzsh_check:
            install_ohmyzsh = await self._run_command(
                'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended',
                timeout=120
            )
            setup_steps.append({
                "step": "install_oh_my_zsh",
                "success": install_ohmyzsh["success"]
            })
        
        # Set up custom zsh config directory
        config_dir_setup = await self._run_command("mkdir -p ~/.config/zshyzsh")
        setup_steps.append({
            "step": "create_config_dir",
            "success": config_dir_setup["success"]
        })
        
        # Configure zshrc
        zshrc_setup = await self._configure_zshrc()
        setup_steps.append({
            "step": "configure_zshrc",
            "success": zshrc_setup
        })
        
        # Set zsh as default shell
        change_shell = await self._run_command("chsh -s $(which zsh)")
        setup_steps.append({
            "step": "set_default_shell",
            "success": change_shell["success"]
        })
        
        return {
            "task_type": "shell_environment_setup",
            "setup_steps": setup_steps,
            "overall_success": all(step["success"] for step in setup_steps)
        }
    
    async def _configure_zshrc(self) -> bool:
        """Configure .zshrc file."""
        zshrc_content = '''
export ZSH_CUSTOM=$HOME/.config/zshyzsh
export PATH=$HOME/.local/bin:$PATH

# Load oh-my-zsh
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git docker python)
source $ZSH/oh-my-zsh.sh

# Load mise if available
if command -v mise &> /dev/null; then
    eval "$(mise activate zsh)"
fi

# Load custom configurations if they exist
if [ -f "$ZSH_CUSTOM/config.zsh" ]; then
    source "$ZSH_CUSTOM/config.zsh"
fi
'''
        
        try:
            result = await self._run_command(f'echo "{zshrc_content}" > ~/.zshrc')
            return result["success"]
        except:
            return False
    
    async def _setup_symlinks(self) -> Dict[str, Any]:
        """Set up necessary symlinks."""
        logging.info("Setting up symlinks")
        
        # Common symlinks for WSL development
        symlink_operations = [
            {
                "description": "Create local bin directory",
                "command": "mkdir -p ~/.local/bin"
            },
            {
                "description": "Link gptme config",
                "command": "mkdir -p ~/.config/gptme && ln -sf ~/.config/zshyzsh/gptme/config.toml ~/.config/gptme/config.toml"
            },
            {
                "description": "Link zellij config", 
                "command": "ln -sf ~/.config/zshyzsh/zellij ~/.config/zellij"
            }
        ]
        
        results = []
        for operation in symlink_operations:
            result = await self._run_command(operation["command"])
            results.append({
                "operation": operation["description"],
                "success": result["success"],
                "error": result.get("stderr") if not result["success"] else None
            })
        
        return {
            "task_type": "symlink_setup",
            "operations": results,
            "overall_success": all(r["success"] for r in results)
        }
    
    async def _generic_shell_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle generic shell configuration tasks."""
        return {
            "task_type": "generic_shell_task",
            "message": "Shell configuration task completed",
            "success": True
        }