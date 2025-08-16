#!/usr/bin/env python3
"""
Tzvi The Windows Wizard - Windows-specific expertise and guidance.

Tzvi specializes in Windows development environments, WSL configuration,
Windows Terminal setup, and Windows-specific tooling and workflows.
"""

from .base import Agent
from typing import Dict, Any
import os
from pathlib import Path


class TzviTheWindowsWizard(Agent):
    """
    Tzvi The Windows Wizard specializes in:
    - Windows Subsystem for Linux (WSL) setup and configuration
    - Windows Terminal and PowerShell customization
    - Windows development environment optimization
    - Cross-platform file system navigation
    - Windows-specific tooling and package management
    """
    
    def __init__(self):
        super().__init__(
            name="Tzvi The Windows Wizard",
            expertise="Windows development environments, WSL, and Windows-specific tooling",
            personality="Enthusiastic about Windows development, detail-oriented, and always knows the Windows way to do things."
        )
    
    def handle_question(self, question: str) -> str:
        """
        Answer Windows-specific questions and provide guidance.
        
        Tzvi can help with:
        - WSL installation and configuration
        - Windows Terminal setup
        - File system navigation between Windows and WSL
        - Windows development tools
        - PowerShell and command prompt usage
        """
        question_lower = question.lower()
        
        # WSL-related questions
        if any(word in question_lower for word in ["wsl", "windows subsystem", "linux", "ubuntu"]):
            return self._handle_wsl_question(question)
        
        # Windows Terminal questions
        elif any(word in question_lower for word in ["terminal", "powershell", "cmd", "console"]):
            return self._handle_terminal_question(question)
        
        # File system questions
        elif any(word in question_lower for word in ["path", "filesystem", "drive", "mount", "directory"]):
            return self._handle_filesystem_question(question)
        
        # Package management questions
        elif any(word in question_lower for word in ["chocolatey", "winget", "scoop", "package", "install"]):
            return self._handle_package_question(question)
        
        # Development environment questions
        elif any(word in question_lower for word in ["dev", "development", "environment", "setup", "configure"]):
            return self._handle_dev_environment_question(question)
        
        # General Windows questions
        else:
            return self._handle_general_windows_question(question)
    
    def _handle_wsl_question(self, question: str) -> str:
        """Handle WSL-related questions."""
        system_info = self.get_system_info()
        is_wsl = 'WSL' in os.environ.get('WSL_DISTRO_NAME', '') or 'microsoft' in system_info.get('platform_version', '').lower()
        
        return f"""🐧 **Tzvi The Windows Wizard** on WSL!

**Current Environment:**
- Running in WSL: {'✅ Yes' if is_wsl else '❌ No'}
- System: {system_info['platform']} 
- Distribution: {os.environ.get('WSL_DISTRO_NAME', 'Not in WSL')}

**🚀 WSL Setup Guide:**

**1. Install WSL2 (PowerShell as Administrator):**
```powershell
wsl --install
# Or for specific distro
wsl --install -d Ubuntu
```

**2. Verify WSL Installation:**
```powershell
wsl --list --verbose
wsl --status
```

**3. Update WSL:**
```powershell
wsl --update
wsl --shutdown
```

**🔧 Essential WSL Configuration:**

**Set WSL2 as default:**
```powershell
wsl --set-default-version 2
```

**Configure .wslconfig (in Windows %USERPROFILE%):**
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

**🌉 Windows ↔ WSL Integration:**
- **Windows from WSL:** `/mnt/c/Users/YourName/`
- **WSL from Windows:** `\\\\wsl.localhost\\Ubuntu\\home\\username\\`
- **Cross-execution:** `cmd.exe /c dir` from WSL, `wsl ls -la` from Windows

**💡 Your question:** "{question}"

{self._get_wsl_status()}

Need help with specific WSL configuration or troubleshooting?"""

    def _handle_terminal_question(self, question: str) -> str:
        """Handle Windows Terminal and shell questions."""
        system_info = self.get_system_info()
        
        return f"""💻 **Tzvi The Windows Wizard** on Windows Terminal!

**🎯 Windows Terminal Setup:**

**1. Install Windows Terminal:**
```powershell
# Via Microsoft Store (Recommended)
# Or via GitHub releases
winget install Microsoft.WindowsTerminal
```

**2. Configuration File Location:**
`%LOCALAPPDATA%\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json`

**3. Essential Settings:**
```json
{{
    "defaultProfile": "{{Ubuntu GUID}}",
    "copyOnSelect": true,
    "copyFormatting": false,
    "profiles": {{
        "list": [
            {{
                "name": "Ubuntu",
                "source": "Windows.Terminal.Wsl",
                "startingDirectory": "//wsl.localhost/Ubuntu/home/username",
                "colorScheme": "One Half Dark",
                "font": {{
                    "face": "CascadiaCode NF"
                }}
            }}
        ]
    }}
}}
```

**🎨 Recommended Fonts:**
- **Cascadia Code** (built-in)
- **JetBrains Mono**
- **Fira Code**
- **Hack Nerd Font** (for icons)

**⚡ PowerShell Enhancement:**
```powershell
# Install PowerShell 7
winget install Microsoft.PowerShell

# Install Oh My Posh
winget install JanDeDobbeleer.OhMyPosh

# Configure profile
notepad $PROFILE
```

**💡 Your question:** "{question}"

**📊 Current Environment:**
- System: {system_info['platform']}
- Shell: {os.environ.get('SHELL', 'Windows Shell')}

Want me to help you customize your terminal setup?"""

    def _handle_filesystem_question(self, question: str) -> str:
        """Handle file system navigation questions."""
        system_info = self.get_system_info()
        is_wsl = 'microsoft' in system_info.get('platform_version', '').lower()
        
        return f"""📁 **Tzvi The Windows Wizard** on file systems!

**🌉 Windows ↔ WSL Path Translation:**

**From Windows to WSL:**
- `C:\\Users\\YourName\\` → `/mnt/c/Users/YourName/`
- `D:\\Projects\\` → `/mnt/d/Projects/`

**From WSL to Windows:**
- `/home/username/` → `\\\\wsl.localhost\\Ubuntu\\home\\username\\`
- `/tmp/` → `\\\\wsl.localhost\\Ubuntu\\tmp\\`

**⚡ Quick Navigation:**

**Windows Commands:**
```cmd
# Open WSL home in Explorer
explorer.exe \\\\wsl.localhost\\Ubuntu\\home\\%username%

# Open current directory in Explorer (from WSL)
explorer.exe .
```

**WSL Commands:**
```bash
# Access Windows drives
cd /mnt/c/Users/YourName/Desktop

# Open Windows apps from WSL
cmd.exe /c start .
code . # VS Code integration
```

**🔧 Path Utilities:**
```bash
# Convert Windows path to WSL
wslpath "C:\\Users\\YourName\\Documents"
# Output: /mnt/c/Users/YourName/Documents

# Convert WSL path to Windows  
wslpath -w /home/username/projects
# Output: \\\\wsl.localhost\\Ubuntu\\home\\username\\projects
```

**📊 Current Status:**
- Current Directory: {system_info['current_dir']}
- Home Directory: {system_info['home_dir']}
- Running in WSL: {'✅ Yes' if is_wsl else '❌ No'}

**💡 Your question:** "{question}"

Need help with specific path translations or file system operations?"""

    def _handle_package_question(self, question: str) -> str:
        """Handle Windows package management questions."""
        return f"""📦 **Tzvi The Windows Wizard** on package management!

**🚀 Windows Package Managers:**

**1. winget (Recommended - Built-in):**
```powershell
# Search for packages
winget search "visual studio code"

# Install packages
winget install Microsoft.VisualStudioCode
winget install Git.Git
winget install Microsoft.PowerShell

# List installed packages
winget list

# Upgrade all packages
winget upgrade --all
```

**2. Chocolatey:**
```powershell
# Install Chocolatey (PowerShell as Admin)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Use Chocolatey
choco install git nodejs vscode googlechrome firefox
choco upgrade all
```

**3. Scoop (User-level):**
```powershell
# Install Scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Use Scoop
scoop install git nodejs python
scoop bucket add extras
scoop install vscode
```

**🎯 Recommended Developer Tools:**
```powershell
# Essential dev tools via winget
winget install Git.Git
winget install Microsoft.VisualStudioCode  
winget install Microsoft.WindowsTerminal
winget install Microsoft.PowerShell
winget install Docker.DockerDesktop
winget install JetBrains.Toolbox
winget install Postman.Postman
```

**💡 Your question:** "{question}"

**🔧 Package Manager Comparison:**
- **winget:** Built-in, official, growing catalog
- **Chocolatey:** Mature, largest catalog, requires admin
- **Scoop:** User-level, portable apps, command-line focused

Which package manager would work best for your needs?"""

    def _handle_dev_environment_question(self, question: str) -> str:
        """Handle development environment questions."""
        system_info = self.get_system_info()
        
        return f"""🛠️ **Tzvi The Windows Wizard** on dev environments!

**🏗️ Complete Windows Development Setup:**

**1. Essential Foundation:**
```powershell
# Core tools
winget install Git.Git
winget install Microsoft.VisualStudioCode
winget install Microsoft.WindowsTerminal
winget install Microsoft.PowerShell

# Enable WSL2
wsl --install
```

**2. Development Runtimes (in WSL):**
```bash
# Install mise for runtime management
curl https://mise.run | sh

# Install development runtimes
mise install node@latest python@latest
mise global node python
```

**3. Docker Setup:**
```powershell
# Install Docker Desktop
winget install Docker.DockerDesktop

# Configure for WSL2 backend
# Enable WSL2 integration in Docker Desktop settings
```

**🎯 IDE Configuration:**

**VS Code Extensions:**
- WSL extension (ms-vscode-remote.remote-wsl)
- GitLens
- Python
- JavaScript/TypeScript
- Docker

**⚙️ Environment Variables:**
```powershell
# Add to Windows PATH (PowerShell as Admin)
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\\YourPath", [EnvironmentVariableTarget]::Machine)
```

**🔧 Cross-Platform Considerations:**
- Use WSL for Unix-like development
- Keep Windows tools for Windows-specific development
- Use VS Code Remote-WSL for seamless integration
- Configure git with proper line endings

**📊 Current Setup:**
- Platform: {system_info['platform']}
- Architecture: {system_info['architecture']}
- Python: {system_info['python_version']}

**💡 Your question:** "{question}"

What type of development environment are you setting up?"""

    def _handle_general_windows_question(self, question: str) -> str:
        """Handle general Windows questions."""
        system_info = self.get_system_info()
        
        return f"""🪟 **Tzvi The Windows Wizard** at your service!

I'm your Windows development specialist, here to help with:

**🎯 My Expertise:**
- **WSL Configuration** - Perfect Linux dev environment on Windows
- **Windows Terminal** - Beautiful, customizable terminal experience  
- **Package Management** - winget, Chocolatey, Scoop mastery
- **Cross-Platform Workflows** - Seamless Windows ↔ Linux integration
- **Development Tools** - VS Code, Git, Docker, and more

**⚡ Quick Windows Tips:**
- Use `Ctrl + Shift + C/V` in Windows Terminal
- `Win + X` opens admin menu
- `Win + R` for quick run dialog
- `Win + .` for emoji picker
- `F2` to rename files in Explorer

**🔧 Common Windows Dev Tasks:**
```powershell
# Run as administrator
Start-Process powershell -Verb runAs

# Check Windows version
winver

# System information
systeminfo

# Network configuration
ipconfig /all
```

**📊 Your Environment:**
- OS: {system_info['platform']} {system_info['platform_release']}
- Architecture: {system_info['architecture']}  
- User: {system_info['user']}
- Current Directory: {system_info['current_dir']}

**💡 Your question:** "{question}"

I'm here to make Windows development a joy! What specific Windows challenge can I help you tackle?

**🤝 Team Up:** I work great with:
- **Shelldon** - For cross-platform scripting
- **MiseMaster** - For development environment setup
- **BillTheCoordinator** - For complex Windows workflows"""

    def _get_wsl_status(self) -> str:
        """Get current WSL status."""
        status_info = []
        
        # Check if in WSL
        wsl_distro = os.environ.get('WSL_DISTRO_NAME')
        if wsl_distro:
            status_info.append(f"- Current Distro: {wsl_distro}")
        
        # Check WSL version (if available)
        wsl_version = self.run_command("wsl.exe --version")
        if wsl_version:
            status_info.append(f"- WSL Version: {wsl_version.split()[0] if wsl_version else 'Unknown'}")
        
        # Check available distributions
        wsl_list = self.run_command("wsl.exe --list --verbose")
        if wsl_list:
            status_info.append(f"- Available Distributions:\n```\n{wsl_list}\n```")
        
        if status_info:
            return "\n**🔍 WSL Status:**\n" + "\n".join(status_info)
        else:
            return "\n**🔍 WSL Status:** Not detected or not accessible"