#!/usr/bin/env python3
"""
Shelldon - Shell scripting and command-line expert.

Shelldon specializes in shell scripting, command-line tools, system administration,
and terminal workflows. He knows all the ins and outs of bash, zsh, and other shells.
"""

from .base import Agent
from typing import Dict, Any
import os
import subprocess
from pathlib import Path


class Shelldon(Agent):
    """
    Shelldon specializes in:
    - Shell scripting (bash, zsh, fish, etc.)
    - Command-line tools and utilities  
    - System administration tasks
    - Terminal configuration and customization
    - Process management and system monitoring
    """
    
    def __init__(self):
        super().__init__(
            name="Shelldon",
            expertise="Shell scripting, command-line tools, and terminal workflows",
            personality="Command-line wizard with deep system knowledge. Speaks in precise, efficient commands and loves elegant one-liners."
        )
    
    def ask(self, question: str) -> str:
        """
        Answer shell and command-line questions.
        
        Shelldon can help with:
        - Shell configuration and customization
        - Command-line tools and utilities
        - Scripting and automation
        - Process management
        - System monitoring and administration
        """
        question_lower = question.lower()
        
        # Shell configuration questions
        if any(word in question_lower for word in ["shell", "bash", "zsh", "fish", "default shell"]):
            return self._handle_shell_question(question)
        
        # Scripting questions  
        elif any(word in question_lower for word in ["script", "automation", "automate", "batch"]):
            return self._handle_scripting_question(question)
        
        # Command-line tools questions
        elif any(word in question_lower for word in ["command", "tool", "utility", "cli"]):
            return self._handle_tools_question(question)
        
        # Process and system questions
        elif any(word in question_lower for word in ["process", "system", "monitor", "performance"]):
            return self._handle_system_question(question)
        
        # File operations questions
        elif any(word in question_lower for word in ["file", "directory", "find", "search", "permission"]):
            return self._handle_file_question(question)
        
        # General shell questions
        else:
            return self._handle_general_shell_question(question)
    
    def _handle_shell_question(self, question: str) -> str:
        """Handle shell configuration and setup questions."""
        current_shell = os.environ.get('SHELL', 'Unknown')
        system_info = self.get_system_info()
        
        # Check if asking about default shell specifically
        if "default shell" in question.lower() or "is zsh my default" in question.lower():
            return self._check_default_shell()
        
        return f"""🐚 **Shelldon** here for shell mastery!

**Current Shell Environment:**
- Active Shell: `{current_shell}`
- Platform: {system_info['platform']}
- User: {system_info['user']}

**🔧 Shell Configuration:**

**Check Default Shell:**
```bash
echo $SHELL
# or
getent passwd $USER | cut -d: -f7
```

**Change Default Shell:**
```bash
# List available shells
cat /etc/shells

# Change to zsh
chsh -s $(which zsh)

# Change to bash
chsh -s $(which bash)
```

**⚡ Popular Shell Setups:**

**Zsh + Oh My Zsh:**
```bash
# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Popular plugins in ~/.zshrc
plugins=(git npm node python docker)

# Popular themes
ZSH_THEME="agnoster"  # or "powerlevel10k/powerlevel10k"
```

**Bash Configuration (~/.bashrc):**
```bash
# Custom prompt
export PS1="\\u@\\h:\\w\\$ "

# Aliases
alias ll='ls -la'
alias la='ls -A'
alias grep='grep --color=auto'

# History settings
export HISTSIZE=10000
export HISTCONTROL=ignoredups
```

**💡 Your question:** "{question}"

{self._get_shell_status()}

Want help configuring a specific shell or feature?"""

    def _handle_scripting_question(self, question: str) -> str:
        """Handle shell scripting questions."""
        return f"""📜 **Shelldon** on scripting mastery!

**🚀 Shell Scripting Essentials:**

**Script Template:**
```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Variables
readonly SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
readonly LOG_FILE="/tmp/script.log"

# Functions
log() {{
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}}

main() {{
    log "Script started"
    # Your code here
    log "Script completed"
}}

# Error handling
trap 'log "Script failed on line $LINENO"' ERR

main "$@"
```

**⚡ Common Patterns:**

**File Processing:**
```bash
# Process files in directory
for file in *.txt; do
    [ -f "$file" ] || continue
    echo "Processing $file"
done

# Find and process
find . -name "*.log" -type f -exec grep -l "ERROR" {{}} \\;
```

**Command Line Arguments:**
```bash
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=1
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done
```

**Error Handling:**
```bash
# Check command success
if command -v git >/dev/null 2>&1; then
    echo "Git is available"
else
    echo "Git not found" >&2
    exit 1
fi

# Function with error checking
safe_mkdir() {{
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || {{
            echo "Failed to create $dir" >&2
            return 1
        }}
    fi
}}
```

**💡 Your question:** "{question}"

Need help with a specific scripting challenge or pattern?"""

    def _handle_tools_question(self, question: str) -> str:
        """Handle command-line tools questions."""
        return f"""🔨 **Shelldon** on command-line tools!

**⚡ Essential CLI Tools:**

**File Operations:**
```bash
# Advanced find
fd "pattern"          # Modern find alternative
rg "text"             # Modern grep (ripgrep)  
tree                  # Directory visualization
exa                   # Modern ls alternative
bat                   # Better cat with syntax highlighting

# File manipulation
jq '.key'             # JSON processing
yq '.key'             # YAML processing
sed 's/old/new/g'     # Stream editing
awk '{{print $1}}'    # Text processing
```

**System Monitoring:**
```bash
# Process monitoring
htop                  # Interactive process viewer
btop                  # Beautiful system monitor
ps aux | grep nginx   # Process listing

# System resources
df -h                 # Disk usage
du -sh *              # Directory sizes
free -h               # Memory usage
iotop                 # I/O monitoring
```

**Network Tools:**
```bash
# Network diagnostics
curl -I example.com   # HTTP headers
wget -O file.zip url  # Download files
ping google.com       # Network connectivity
netstat -tulpn        # Open ports
ss -tulpn             # Modern netstat

# HTTP testing
httpie GET api.com/users
curl -X POST -H "Content-Type: application/json" -d '{{"key":"value"}}' api.com
```

**Development Tools:**
```bash
# Version control
git status --porcelain
git log --oneline --graph

# Package managers  
npm list --depth=0
pip list --outdated
cargo tree

# Development servers
python -m http.server 8000
php -S localhost:8000
```

**🎯 Modern Replacements:**
- `ls` → `exa` or `eza`
- `cat` → `bat`
- `find` → `fd`
- `grep` → `rg` (ripgrep)
- `du` → `dust`
- `ps` → `procs`

**💡 Your question:** "{question}"

What specific tools or tasks do you need help with?"""

    def _handle_system_question(self, question: str) -> str:
        """Handle system monitoring and administration questions."""
        system_info = self.get_system_info()
        
        return f"""⚙️ **Shelldon** on system administration!

**🔍 System Monitoring:**

**Performance Overview:**
```bash
# CPU and memory
top -n 1
htop
vmstat 1 5

# Disk I/O
iostat -x 1
iotop

# Network
iftop
nethogs
ss -tuln
```

**Process Management:**
```bash
# Find processes
ps aux | grep nginx
pgrep -f "python app.py"

# Kill processes
pkill -f "python app.py"
kill -9 $(pgrep nginx)

# Process tree
pstree -p
```

**Resource Usage:**
```bash
# Disk usage
df -h /
du -sh /var/log/*
ncdu /home  # Interactive disk usage

# Memory analysis  
free -h
cat /proc/meminfo
slabtop

# CPU info
lscpu
cat /proc/cpuinfo
```

**Log Analysis:**
```bash
# System logs
journalctl -f                    # Follow systemd logs
journalctl -u nginx.service      # Service-specific logs
tail -f /var/log/syslog          # Traditional logs

# Log analysis
grep -i error /var/log/messages
awk '/ERROR/ {{print $1, $2, $NF}}' app.log
```

**📊 Current System:**
- Platform: {system_info['platform']} {system_info['platform_release']}
- Architecture: {system_info['architecture']}
- Python: {system_info['python_version']}
- Load: {self._get_system_load()}

**💡 Your question:** "{question}"

{self._get_process_info()}

Need help with specific system monitoring or administration tasks?"""

    def _handle_file_question(self, question: str) -> str:
        """Handle file operations questions."""
        system_info = self.get_system_info()
        
        return f"""📁 **Shelldon** on file operations!

**🔍 File Finding & Searching:**

**Modern Tools:**
```bash
# Find files by name (fast)
fd "pattern"
fd "*.py" src/

# Search file contents (blazing fast)
rg "function.*user"
rg "TODO|FIXME" --type python

# Interactive searching
fzf  # Fuzzy finder
```

**Traditional Tools:**
```bash
# Find files
find . -name "*.txt" -type f
find /var -size +100M -exec ls -lh {{}} \\;
find . -mtime -7  # Modified in last 7 days

# Search contents
grep -r "pattern" .
grep -n "error" *.log
```

**📝 File Operations:**

**Basic Operations:**
```bash
# Copy with progress
rsync -av --progress source/ dest/
cp -r --preserve=all source dest

# Move/rename
mv old_name new_name
rename 's/old/new/g' *.txt

# Create/touch
mkdir -p path/to/deep/directory
touch file{{1..10}}.txt
```

**Permission Management:**
```bash
# View permissions
ls -la
stat filename

# Change permissions
chmod 755 script.sh      # rwxr-xr-x
chmod u+x script.sh      # Add execute for user
chmod -R 644 directory/  # Recursive

# Change ownership
chown user:group file
chown -R www-data:www-data /var/www/
```

**🔧 Advanced File Operations:**
```bash
# Compare files
diff file1 file2
comm -23 file1 file2     # Lines in file1 but not file2

# File compression
tar -czf archive.tar.gz directory/
tar -xzf archive.tar.gz

# Disk usage
du -sh * | sort -rh      # Sort by size
```

**📊 Current Directory:**
- Location: {system_info['current_dir']}
- User: {system_info['user']}

**💡 Your question:** "{question}"

What specific file operation do you need help with?"""

    def _handle_general_shell_question(self, question: str) -> str:
        """Handle general shell questions."""
        current_shell = os.environ.get('SHELL', 'Unknown')
        system_info = self.get_system_info()
        
        return f"""🎯 **Shelldon** - Your Command-Line Sensei!

I live and breathe the command line! Here's what I can help you with:

**🐚 My Specialties:**
- **Shell Mastery** - bash, zsh, fish configuration
- **Scripting Excellence** - automation and workflow scripts  
- **CLI Tools** - modern alternatives and power tools
- **System Administration** - monitoring, processes, logs
- **File Wizardry** - finding, processing, managing files

**⚡ Quick Wins:**

**Productivity Aliases:**
```bash
alias ll='ls -la'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias h='history'
alias c='clear'
```

**One-Liners:**
```bash
# Find large files
find . -type f -size +100M -exec ls -lh {{}} \\; | sort -k5 -rh

# Process monitoring
ps aux | awk '{{print $2, $4, $11}}' | column -t

# Network connections
netstat -tulpn | grep :80
```

**📊 Your Current Setup:**
- Shell: `{current_shell}`
- Platform: {system_info['platform']}
- Working Directory: `{system_info['current_dir']}`

**💡 Your question:** "{question}"

I'm here to make your terminal experience legendary! Whether you need:
- Shell configuration help
- Scripting assistance  
- Command-line tool recommendations
- System administration guidance
- File operation wizardry

**🤝 Team Synergy:** I work perfectly with:
- **MiseMaster** - For development environment commands
- **TzviTheWindowsWizard** - For cross-platform shell workflows
- **BillTheCoordinator** - For scripted automation workflows

What command-line challenge can I help you conquer?"""

    def _check_default_shell(self) -> str:
        """Check if zsh is the default shell."""
        current_shell = os.environ.get('SHELL', '')
        user = os.environ.get('USER', 'unknown')
        
        # Try to get the user's default shell from passwd
        try:
            passwd_output = subprocess.run(
                ['getent', 'passwd', user], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if passwd_output.returncode == 0:
                shell_from_passwd = passwd_output.stdout.strip().split(':')[-1]
            else:
                shell_from_passwd = "Unknown"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            shell_from_passwd = "Unknown"
        
        is_zsh = 'zsh' in current_shell.lower()
        
        return f"""🐚 **Shelldon** checking your shell status!

**🔍 Shell Analysis:**
- **Current Session Shell:** `{current_shell}`
- **Default Shell (from passwd):** `{shell_from_passwd}`
- **Is zsh your default?** {'✅ Yes!' if is_zsh else '❌ No'}

**📊 Shell Status:**
```
Current: {current_shell}
Default: {shell_from_passwd}
Match: {'✅ Yes' if current_shell == shell_from_passwd else '⚠️  Different'}
```

**🔧 To Make zsh Your Default:**
```bash
# Check available shells
cat /etc/shells

# Change default shell to zsh  
chsh -s $(which zsh)

# Verify change
echo $SHELL
```

**⚡ After Changing Shell:**
1. **Log out and back in** for changes to take effect
2. **Install Oh My Zsh** for an enhanced experience:
   ```bash
   sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
   ```

{'**🎉 You are already using zsh as your default shell!**' if is_zsh else '**💡 Switch to zsh for a more powerful shell experience!**'}"""

    def _get_shell_status(self) -> str:
        """Get current shell status and configuration."""
        current_shell = os.environ.get('SHELL', 'Unknown')
        shell_name = Path(current_shell).name if current_shell != 'Unknown' else 'Unknown'
        
        status_lines = [
            f"- Active Shell: `{current_shell}`",
            f"- Shell Name: `{shell_name}`"
        ]
        
        # Check for common shell config files
        home = Path.home()
        configs = {
            'bash': ['.bashrc', '.bash_profile', '.profile'],
            'zsh': ['.zshrc', '.zprofile'],
            'fish': ['.config/fish/config.fish']
        }
        
        for shell_type, config_files in configs.items():
            for config_file in config_files:
                config_path = home / config_file
                if config_path.exists():
                    status_lines.append(f"- {shell_type.title()} Config: `{config_path}` ✅")
        
        return "\n**🔍 Shell Status:**\n" + "\n".join(status_lines)

    def _get_system_load(self) -> str:
        """Get system load average if available."""
        try:
            with open('/proc/loadavg', 'r') as f:
                load = f.read().strip().split()[:3]
                return f"{load[0]} {load[1]} {load[2]}"
        except FileNotFoundError:
            return "N/A"

    def _get_process_info(self) -> str:
        """Get basic process information."""
        try:
            # Get process count
            ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if ps_output.returncode == 0:
                process_count = len(ps_output.stdout.strip().split('\n')) - 1
                return f"\n**🔢 Process Count:** {process_count} running processes"
        except FileNotFoundError:
            pass
        
        return "\n**🔢 Process Info:** Not available on this system"