# Windows Package Installer Agent - Full Automation Plan

## 🎯 Zero-Intervention Installation Strategy

### **Core Automation Principle**
WindowsPackageInstaller will achieve 100% unattended installation using:
- **Package Managers**: winget, chocolatey, scoop for silent installs
- **Environment Variables**: All credentials/tokens from .env
- **MCP Command Execution**: Remote execution through secure MCP tools
- **Verification**: Automated success/failure detection

## 🔧 **Package Manager Strategy**

### **1. Winget (Primary - Microsoft Official)**
```bash
# Silent installation with accept-all
winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.VisualStudioCode --silent
winget install --id Docker.DockerDesktop --silent
```

**Advantages:**
- ✅ Built into Windows 10/11
- ✅ Official Microsoft packages
- ✅ Silent install support
- ✅ JSON output for automation

### **2. Chocolatey (Secondary - Community)**
```powershell
# Install chocolatey itself
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Silent package installs
choco install git -y
choco install vscode -y
choco install docker-desktop -y
```

### **3. Scoop (Tertiary - Developer Tools)**
```powershell
# Install scoop
iwr -useb get.scoop.sh | iex

# Developer tools
scoop install git
scoop install neovim
scoop bucket add extras
scoop install vscode
```

## 🔐 **Credential Management (.env)**

### **Required Environment Variables**
```bash
# .env file in project root
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_USERNAME=your-username
GITHUB_EMAIL=your-email@domain.com

# Optional: Auto-configure Git
GIT_USER_NAME="Your Full Name"
GIT_USER_EMAIL="your-email@domain.com"

# Windows-specific
WINDOWS_USER=your-windows-username
CHOCOLATEY_LICENSE_KEY=optional-commercial-key

# Claude/AI Tools
CLAUDE_API_KEY=sk-ant-xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx
```

### **Secure Token Handling**
```python
import os
from pathlib import Path

def load_credentials():
    """Load all credentials from .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    return {
        'github_token': os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN'),
        'github_username': os.getenv('GITHUB_USERNAME'),
        'github_email': os.getenv('GITHUB_EMAIL'),
        'git_name': os.getenv('GIT_USER_NAME'),
        'git_email': os.getenv('GIT_USER_EMAIL'),
    }
```

## 🖥️ **Windows Agent Architecture**

### **Agent Structure**
```python
class WindowsPackageInstallerAgent(GoogleADKAgent):
    """Fully automated Windows package installer"""
    
    def __init__(self):
        super().__init__()
        self.credentials = self.load_credentials()
        self.package_managers = {
            'winget': WingetManager(),
            'chocolatey': ChocolateyManager(), 
            'scoop': ScoopManager()
        }
    
    async def install_development_environment(self):
        """Main automation workflow"""
        # 1. Install package managers
        await self.setup_package_managers()
        
        # 2. Install core tools
        await self.install_core_packages()
        
        # 3. Configure Git with tokens
        await self.configure_git()
        
        # 4. Setup development tools
        await self.setup_development_tools()
        
        # 5. Verify everything works
        await self.verify_installation()
```

### **MCP Tool Integration**
```python
# Use MCP for all command execution
async def execute_windows_command(self, command: str, admin: bool = False):
    """Execute commands through MCP with optional admin rights"""
    
    if admin:
        # PowerShell as Administrator
        ps_command = f'Start-Process PowerShell -Verb RunAs -ArgumentList "-Command", "{command}"'
        return await self.mcp_client.call_tool("execute_command", {
            "command": ps_command,
            "shell": "powershell",
            "timeout": 300
        })
    else:
        return await self.mcp_client.call_tool("execute_command", {
            "command": command,
            "shell": "powershell"
        })
```

## 📦 **Package Installation Matrix**

### **Core Development Tools**
| Package | Winget ID | Chocolatey | Verification |
|---------|-----------|------------|--------------|
| Git | `Git.Git` | `git` | `git --version` |
| VS Code | `Microsoft.VisualStudioCode` | `vscode` | `code --version` |
| Node.js | `OpenJS.NodeJS` | `nodejs` | `node --version` |
| Python | `Python.Python.3.12` | `python` | `python --version` |
| Docker | `Docker.DockerDesktop` | `docker-desktop` | `docker --version` |
| WSL | `Microsoft.WSL` | `wsl` | `wsl --status` |

### **Development Tools**
| Package | Winget ID | Verification |
|---------|-----------|--------------|
| Windows Terminal | `Microsoft.WindowsTerminal` | `wt --version` |
| PowerShell 7 | `Microsoft.PowerShell` | `pwsh --version` |
| GitHub CLI | `GitHub.cli` | `gh --version` |
| Neovim | `Neovim.Neovim` | `nvim --version` |

## 🔄 **Automation Workflow**

### **Phase 1: Environment Setup**
1. Check Windows version and capabilities
2. Load credentials from .env file  
3. Verify internet connectivity
4. Check for existing installations

### **Phase 2: Package Manager Installation**
```python
async def setup_package_managers(self):
    """Install all package managers if missing"""
    
    # Winget (usually pre-installed)
    if not await self.check_winget():
        await self.install_winget()
    
    # Chocolatey
    if not await self.check_chocolatey():
        await self.install_chocolatey()
    
    # Scoop (optional)
    if self.config.use_scoop:
        await self.install_scoop()
```

### **Phase 3: Silent Package Installation**
```python
async def install_package(self, package_name: str):
    """Try multiple package managers for installation"""
    
    for pm_name, pm in self.package_managers.items():
        try:
            result = await pm.install(package_name, silent=True)
            if result.success:
                self.log_success(f"{package_name} installed via {pm_name}")
                return result
        except Exception as e:
            self.log_warning(f"{pm_name} failed for {package_name}: {e}")
            continue
    
    raise InstallationError(f"All package managers failed for {package_name}")
```

### **Phase 4: Automated Configuration**
```python
async def configure_git(self):
    """Configure Git with credentials from .env"""
    
    commands = [
        f'git config --global user.name "{self.credentials["git_name"]}"',
        f'git config --global user.email "{self.credentials["git_email"]}"',
        f'git config --global credential.helper manager-core',
        # Setup GitHub CLI with token
        f'echo {self.credentials["github_token"]} | gh auth login --with-token'
    ]
    
    for cmd in commands:
        await self.execute_windows_command(cmd)
```

## ✅ **Verification Strategy**

### **Automated Testing**
```python
async def verify_installation(self):
    """Comprehensive verification of all installations"""
    
    verifications = [
        ("Git", "git --version"),
        ("Node.js", "node --version"),
        ("Docker", "docker --version"),
        ("VS Code", "code --version"),
        ("GitHub CLI", "gh --version"),
        ("WSL", "wsl --status"),
    ]
    
    results = []
    for name, command in verifications:
        try:
            result = await self.execute_windows_command(command)
            if result.returncode == 0:
                results.append(f"✅ {name}: {result.stdout.strip()}")
            else:
                results.append(f"❌ {name}: Failed")
        except Exception as e:
            results.append(f"❌ {name}: Error - {e}")
    
    return results
```

## 🚀 **Key Automation Features**

### **1. Zero Prompts**
- All package installations use `--silent` flags
- Credentials loaded from environment
- Accept all license agreements automatically
- Use default installation paths

### **2. Error Recovery**
- Multiple package manager fallbacks
- Retry logic for network failures
- Detailed logging for troubleshooting
- Rollback capabilities for failed installs

### **3. Progress Tracking**
- Real-time installation status
- Estimated time remaining
- Detailed logs for each operation
- Success/failure reporting

### **4. Security**
- Credentials never logged or displayed
- Secure token handling
- MCP command execution sandboxing
- Administrative privilege management

## 📋 **Implementation Checklist**

✅ **Design Complete**
- [x] Package manager strategy defined
- [x] Credential management planned
- [x] MCP integration designed
- [x] Verification framework outlined

⭕ **Next Steps**
- [ ] Implement WindowsPackageInstallerAgent class
- [ ] Create package manager wrapper classes
- [ ] Add Windows-specific MCP tools
- [ ] Build comprehensive test suite
- [ ] Create example .env template

This approach eliminates all human intervention while maintaining security and reliability through proper credential management and comprehensive verification.