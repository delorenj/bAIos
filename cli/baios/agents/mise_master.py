#!/usr/bin/env python3
"""
Mise Master - Expert in mise tool management and configuration.

Mise Master specializes in managing development environments using mise,
including runtime version management, global tool configuration, and
environment-specific setups.
"""

from .base import Agent
from typing import Dict, Any
import os
from pathlib import Path


class MiseMaster(Agent):
    """
    Mise Master specializes in:
    - mise installation and configuration
    - Runtime version management (Node.js, Python, Ruby, etc.)
    - Global and project-specific tool management
    - Environment configuration and optimization
    - Development environment troubleshooting
    """
    
    def __init__(self):
        super().__init__(
            name="Mise Master",
            expertise="mise tool management, runtime versions, and development environment configuration",
            personality="Precise, methodical, and environment-focused. Knows exactly how to set up the perfect development environment."
        )
    
    def ask(self, question: str) -> str:
        """
        Answer mise-related questions and provide guidance.
        
        Mise Master can help with:
        - mise installation and setup
        - Managing runtime versions
        - Configuration file management
        - Environment troubleshooting
        - Tool installation and updates
        """
        question_lower = question.lower()
        
        # Installation questions
        if any(word in question_lower for word in ["install", "setup", "configure"]):
            return self._handle_installation_question(question)
        
        # Version management questions
        elif any(word in question_lower for word in ["version", "runtime", "node", "python", "ruby", "go"]):
            return self._handle_version_question(question)
        
        # Configuration questions
        elif any(word in question_lower for word in ["config", "toml", ".mise", "settings"]):
            return self._handle_config_question(question)
        
        # Troubleshooting questions
        elif any(word in question_lower for word in ["error", "problem", "issue", "not working", "broken"]):
            return self._handle_troubleshooting_question(question)
        
        # General mise questions
        else:
            return self._handle_general_mise_question(question)
    
    def _handle_installation_question(self, question: str) -> str:
        """Handle mise installation and setup questions."""
        system_info = self.get_system_info()
        mise_installed = self.check_command_available("mise")
        
        return f"""🔧 **Mise Master** here to help with installation!

**Current Status:**
- System: {system_info['platform']} ({system_info['architecture']})
- mise installed: {'✅ Yes' if mise_installed else '❌ No'}

**📦 Installation Options:**

**Option 1: Quick Install Script (Recommended)**
```bash
curl https://mise.run | sh
```

**Option 2: Via Package Managers**
```bash
# Ubuntu/Debian
sudo snap install mise --classic

# macOS
brew install mise

# Windows (via Scoop)
scoop install mise
```

**🔧 Post-Installation Setup:**

1. **Add to shell profile:**
```bash
# For bash (~/.bashrc)
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# For zsh (~/.zshrc)  
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc

# For fish (~/.config/fish/config.fish)
echo 'mise activate fish | source' >> ~/.config/fish/config.fish
```

2. **Reload shell:**
```bash
source ~/.bashrc  # or ~/.zshrc
```

3. **Verify installation:**
```bash
mise --version
```

**💡 Your specific question:** "{question}"

{self._get_mise_status()}

Would you like me to guide you through any specific part of the setup?"""

    def _handle_version_question(self, question: str) -> str:
        """Handle runtime version management questions."""
        mise_installed = self.check_command_available("mise")
        
        return f"""🎯 **Mise Master** on version management!

**🔄 Runtime Version Management:**

**Install Runtimes:**
```bash
# Latest versions
mise install node@latest python@latest ruby@latest

# Specific versions  
mise install node@18.17.0 python@3.11.5

# Multiple versions
mise install node@16 node@18 node@20
```

**🌐 Global Defaults:**
```bash
# Set global defaults
mise global node@18.17.0 python@3.11.5

# View current versions
mise current

# List installed versions
mise list node
```

**📁 Project-Specific Versions:**
```bash
# In project directory
mise local node@16.20.0 python@3.10.12

# Creates .mise.toml file:
```
```toml
[tools]
node = "16.20.0"
python = "3.10.12"
```

**🔍 Available Runtimes:**
- **Languages:** node, python, ruby, go, rust, java, dotnet
- **Databases:** postgres, redis, mongodb  
- **Tools:** terraform, kubectl, helm, docker-compose

**📊 Status Check:**
- mise installed: {'✅ Yes' if mise_installed else '❌ No'}

**💡 For your question:** "{question}"

{self._get_current_versions() if mise_installed else "Install mise first to see current versions."}

Need help with a specific runtime or version?"""

    def _handle_config_question(self, question: str) -> str:
        """Handle configuration questions."""
        system_info = self.get_system_info()
        home_dir = Path(system_info['home_dir'])
        global_config = home_dir / ".config" / "mise" / "config.toml"
        project_config = Path.cwd() / ".mise.toml"
        
        return f"""⚙️ **Mise Master** on configuration!

**📁 Configuration Files:**

**Global Config:** `{global_config}`
```toml
[tools]
node = "18.17.0" 
python = "3.11.5"

[env]
PATH = ["$HOME/.local/bin", "$PATH"]

[settings]
experimental = true
```

**Project Config:** `.mise.toml` (in project root)
```toml
[tools]
node = "16.20.0"
python = "3.10.12"

[env]
DATABASE_URL = "postgres://localhost/myapp"
API_KEY = "development-key"

[tasks]
dev = "npm run dev"
test = "npm test"
```

**🔧 Configuration Commands:**
```bash
# Edit global config
mise config edit

# Show current config
mise config show  

# List all configs
mise config list

# Validate config
mise config validate
```

**📊 Current Status:**
- Working Directory: {system_info['current_dir']}
- Global Config Exists: {'✅ Yes' if global_config.exists() else '❌ No'}
- Project Config Exists: {'✅ Yes' if project_config.exists() else '❌ No'}

**💡 Your question:** "{question}"

Would you like me to help you create or modify a specific configuration?"""

    def _handle_troubleshooting_question(self, question: str) -> str:
        """Handle troubleshooting questions."""
        system_info = self.get_system_info()
        mise_installed = self.check_command_available("mise")
        
        return f"""🔍 **Mise Master** troubleshooting mode!

**🚨 Common Issues & Solutions:**

**1. Command not found: mise**
```bash
# Check if mise is in PATH
which mise

# Reinstall if needed
curl https://mise.run | sh

# Add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
```

**2. Runtime not activating**
```bash
# Check if mise is activated in shell
echo $MISE_SHELL

# Re-activate mise
eval "$(mise activate bash)"  # or zsh/fish

# Check shell profile
grep -n "mise activate" ~/.bashrc ~/.zshrc
```

**3. Version conflicts**
```bash
# Check current versions
mise current

# Reset to global
mise local --remove node python

# Clear cache
mise cache clear
```

**4. Installation failures**
```bash
# Update mise first
mise self-update

# Install with verbose output
mise install -v node@18.17.0

# Check available versions
mise list-remote node
```

**📊 Current System Status:**
- Platform: {system_info['platform']}
- mise installed: {'✅ Yes' if mise_installed else '❌ No'}
- Shell: {os.environ.get('SHELL', 'Unknown')}

**💡 Your specific issue:** "{question}"

{self._get_diagnostic_info() if mise_installed else "Please install mise first."}

Need me to run specific diagnostics for your issue?"""

    def _handle_general_mise_question(self, question: str) -> str:
        """Handle general mise questions."""
        mise_installed = self.check_command_available("mise")
        
        return f"""🎪 **Mise Master** at your service!

**🚀 About mise:**
mise is a polyglot runtime manager (like nvm, rbenv, pyenv, etc. but for any language) that:
- Manages tool versions per-project
- Handles environment variables
- Provides task running capabilities
- Supports 100+ tools and runtimes

**⚡ Key Features:**
- **Fast** - Written in Rust for performance
- **Compatible** - Works with existing `.nvmrc`, `.python-version` files  
- **Flexible** - Global and project-specific configurations
- **Comprehensive** - Supports languages, databases, and CLI tools

**🎯 Common Use Cases:**
1. **Development Environment** - Consistent tool versions across team
2. **CI/CD** - Reproducible builds with exact versions
3. **Multiple Projects** - Different Node/Python versions per project
4. **Environment Variables** - Project-specific settings

**📊 Quick Status:**
- mise installed: {'✅ Yes' if mise_installed else '❌ No'}
- Your question: "{question}"

**🔧 Getting Started:**
```bash
# Install a runtime
mise install node@18

# Set as default
mise global node@18

# Check status  
mise current
```

{self._get_mise_status() if mise_installed else "Ready to help you install and configure mise!"}

What specific aspect of mise would you like to explore?"""

    def _get_mise_status(self) -> str:
        """Get current mise status information."""
        if not self.check_command_available("mise"):
            return "**Status:** mise not installed"
        
        version = self.run_command("mise --version")
        current = self.run_command("mise current")
        
        status = "\n**📊 Current Status:**"
        if version:
            status += f"\n- Version: {version}"
        if current:
            status += f"\n- Current Tools:\n```\n{current}\n```"
        else:
            status += "\n- No tools configured yet"
            
        return status

    def _get_current_versions(self) -> str:
        """Get currently active versions."""
        current = self.run_command("mise current")
        if current:
            return f"\n**📊 Currently Active:**\n```\n{current}\n```"
        return "\n**📊 No tools currently active**"

    def _get_diagnostic_info(self) -> str:
        """Get diagnostic information for troubleshooting."""
        diagnostics = []
        
        # Check mise doctor
        doctor = self.run_command("mise doctor")
        if doctor:
            diagnostics.append(f"**🏥 mise doctor:**\n```\n{doctor}\n```")
        
        # Check env
        env_info = self.run_command("mise env")
        if env_info:
            diagnostics.append(f"**🌍 Environment:**\n```\n{env_info}\n```")
        
        return "\n" + "\n\n".join(diagnostics) if diagnostics else "\n**No diagnostic info available**"