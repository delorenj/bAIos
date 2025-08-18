# Enhanced Comprehensive Inventory

## Required .env Keys

- GITHUB_PERSONAL_ACCESS_TOKEN
- OPENROUTER_API_KEY
- REPO_PATH (defaults to `$HOME/repos`)
- NERD_FONT (defaults to `Hack Nerd Font Mono`)

## Official Documentation Links

This inventory includes official installation documentation links for all tools, researched and verified by the bAIos Hive Mind Documentation Research Lead.

## Agent Group Categories

### 1. Shell & Terminal Setup Agent
**Priority: CRITICAL** - Must be done first after OS setup

- **zsh** - Install and set as default shell
  - 📖 **Official Docs**: [Zsh Manual](https://zsh.sourceforge.io/Doc/Release/index.html)
  - 🔧 **Installation**: [Installing ZSH Guide](https://github.com/ohmyzsh/ohmyzsh/wiki/Installing-ZSH)
- **oh-my-zsh** - Install via curl with basic plugins (git, docker, python)
  - 📖 **Official Docs**: [Oh My Zsh Website](https://ohmyz.sh/)
  - 🔧 **Installation**: `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
  - 📚 **Repository**: [GitHub - ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh)
- **Terminal** - Configure terminal settings
- **Z shell (Zsh)** - Advanced shell configuration
- **Bash** - Fallback shell setup
- **PowerShell** - Windows shell (if applicable)

### 2. Package Managers Agent  
**Priority: HIGH** - Required for most other installations

- **apt** - Ubuntu package manager (update, upgrade, install packages)
- **snap** - Ubuntu snap package manager
- **mise** - Development environment manager (install and activate in zshrc)
  - 📖 **Official Docs**: [Mise Documentation](https://mise.jdx.dev/getting-started.html)
  - 🔧 **Installation**: [Installing Mise](https://mise.jdx.dev/installing-mise.html)
  - ⚡ **Quick Install**: `curl https://mise.run | sh`
- **npm** - Node.js package manager
- **pip** - Python package manager
- **pipx** - Python application installer
  - 📖 **Official Docs**: [pipx Documentation](https://pipx.pypa.io/stable/)
  - 🔧 **Installation**: [pipx Installation Guide](https://pipx.pypa.io/stable/installation/)
  - 📚 **Repository**: [GitHub - pypa/pipx](https://github.com/pypa/pipx)
- **Chocolatey** - Windows package manager
- **Homebrew** - macOS package manager (if applicable)
- **nvm** - Node version manager

### 3. Version Control Agent
**Priority: HIGH** - Essential for development workflow

- **Git** - Version control system configuration
- **GitHub** - Platform integration and setup
- **GitHub CLI (gh)** - Install and auth login (non-enterprise, SSH key, PAT)
  - 📖 **Official Docs**: [GitHub CLI Manual](https://cli.github.com/manual/)
  - 🔧 **Installation**: [GitHub CLI Installation](https://github.com/cli/cli#installation)
  - 📚 **Repository**: [GitHub - cli/cli](https://github.com/cli/cli)
  - ⚡ **Quickstart**: [GitHub CLI Quickstart](https://docs.github.com/en/github-cli/github-cli/quickstart)
- **SSH** - Generate ed25519 key with no passphrase
  - 📖 **Official Docs**: [GitHub SSH Key Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
  - 🔧 **Command**: `ssh-keygen -t ed25519 -C "your_email@example.com"`
- **SSH Keys** - Configure GitHub SSH authentication

### 4. Development Tools Agent
**Priority: HIGH** - Core development environment

- **Neovim** - Install latest from packaged distributable (>v0.11, not apt)
  - 📖 **Official Docs**: [Neovim Documentation](https://neovim.io/)
  - 🔧 **Installation**: [Neovim INSTALL.md](https://github.com/neovim/neovim/blob/master/INSTALL.md)
  - 📚 **Repository**: [GitHub - neovim/neovim](https://github.com/neovim/neovim)
- **Vim** - Fallback editor
- **VS Code** - Microsoft editor
  - 📖 **Official Docs**: [VS Code Documentation](https://code.visualstudio.com/docs)
  - 🔧 **Installation**: [VS Code Setup Overview](https://code.visualstudio.com/docs/setup/setup-overview)
  - 💾 **Download**: [VS Code Download](https://code.visualstudio.com/download)
- **Cursor** - AI-powered editor
  - 📖 **Official Docs**: [Cursor Documentation](https://docs.cursor.com/en/welcome)
  - 💾 **Download**: [Cursor Website](https://cursor.com/en)
  - 🔧 **Installation Guide**: Available for Windows, macOS, and Linux
- **LazyVim** - Install and configure in `~/.config/nvim`
  - 📖 **Official Docs**: [LazyVim Website](https://www.lazyvim.org/)
  - 🔧 **Installation**: [LazyVim Installation Guide](https://www.lazyvim.org/installation)
  - 📚 **Repository**: [GitHub - LazyVim/LazyVim](https://github.com/LazyVim/LazyVim)

### 5. Fonts & UI Agent
**Priority: MEDIUM** - Visual and usability improvements

- **Hack Nerd Font Mono** - Download and install in Windows
  - 📖 **Official Source**: [Nerd Fonts](https://www.nerdfonts.com/)
  - 💾 **Download**: [Hack Nerd Font Releases](https://github.com/ryanoasis/nerd-fonts/releases)
- **JetBrains Mono** - Alternative font
  - 📖 **Official Docs**: [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
  - 💾 **Download**: [JetBrains Mono Downloads](https://github.com/JetBrains/JetBrainsMono)
- **Alacritty** - Terminal emulator (download/install in Windows, configure for WSL)
  - 📖 **Official Docs**: [Alacritty Website](https://alacritty.org/)
  - 🔧 **Installation**: [Alacritty INSTALL.md](https://github.com/alacritty/alacritty/blob/master/INSTALL.md)
  - 📚 **Repository**: [GitHub - alacritty/alacritty](https://github.com/alacritty/alacritty)

### 6. Programming Languages Agent
**Priority: HIGH** - Core development languages

- **Go** - Programming language (209 mentions - heavily used)
  - 📖 **Official Docs**: [Go Documentation](https://go.dev/doc/)
  - 🔧 **Installation**: [Download and Install Go](https://go.dev/doc/install)
  - 💾 **Download**: [Go Downloads](https://go.dev/dl/)
- **Python** - Install 3.12.9 via mise
- **Python 3.12.9** - Specific version requirement
  - 📖 **Official Docs**: [Python 3.12 Documentation](https://docs.python.org/3.12/)
  - 🔧 **Installation**: [Python Setup and Usage](https://docs.python.org/3.12/using/index.html)
  - 💾 **Download**: [Python 3.12.9 Release](https://www.python.org/downloads/release/python-3129/)
- **Rust** - Systems programming language
  - 📖 **Official Docs**: [The Rust Programming Language](https://doc.rust-lang.org/book/)
  - 🔧 **Installation**: [Install Rust](https://www.rust-lang.org/tools/install)
  - ⚡ **Quick Install**: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Node.js** - Install latest via mise
  - 📖 **Official Docs**: [Node.js Documentation](https://nodejs.org/en/learn/)
  - 🔧 **Installation**: [How to Install Node.js](https://nodejs.org/en/learn/getting-started/how-to-install-nodejs)
  - 💾 **Download**: [Node.js Downloads](https://nodejs.org/en/download)
- **JavaScript** - Runtime environment
- **TypeScript** - Type-safe JavaScript

### 7. Container & DevOps Agent
**Priority: MEDIUM** - Containerization and deployment

- **Docker** - Container platform (test with hello-world)
  - 📖 **Official Docs**: [Docker Documentation](https://docs.docker.com/)
  - 🔧 **Installation**: [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
  - 🐧 **Linux Guide**: [Docker on Linux](https://docs.docker.com/engine/install/)
  - ✅ **Verification**: `sudo docker run hello-world`
- **Docker Compose** - Multi-container orchestration (v2)
  - 📖 **Official Docs**: [Docker Compose Documentation](https://docs.docker.com/compose/)
- **Docker Desktop** - Windows/macOS Docker interface
  - 📖 **Official Docs**: [Docker Desktop Documentation](https://docs.docker.com/desktop/)
  - 💾 **Download**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 8. AI & Development Tools Agent
**Priority: MEDIUM** - AI-assisted development

- **Claude** - AI assistant integration
- **claude-code** - Install via npm (`npm i -g @anthropic-ai/claude-code`)
  - 📖 **Official Docs**: [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
  - 🔧 **Installation**: [Claude Code Setup](https://docs.anthropic.com/en/docs/claude-code/setup)
  - 📦 **NPM Package**: [@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code)
  - ⚡ **Requirements**: Node.js 18+, authentication required
- **claude-flow** - Install via npm (`npm i -g claude-flow@latest`)
- **gptme** - Install via pipx (`pipx install 'gptme[all]'`)
  - 📖 **Official Docs**: [gptme Documentation](https://gptme.org/docs/)
  - 🔧 **Installation**: [Getting Started Guide](https://gptme.org/docs/getting-started.html)
  - 📚 **Repository**: [GitHub - gptme/gptme](https://github.com/gptme/gptme)
  - 📦 **PyPI**: [gptme on PyPI](https://pypi.org/project/gptme/)
  - ⚡ **Requirements**: Python 3.10+, LLM API key needed
- **gptme-rag** - Install via pipx (`pipx install gptme-rag`)
- **ChatGPT** - AI assistant
- **Copilot** - GitHub AI assistant
- **Ollama** - Local AI models

### 9. Windows-Specific Agent
**Priority: HIGH** (for Windows users) - Windows/WSL integration

- **Windows** - Host OS configuration
- **WSL** - Windows Subsystem for Linux setup
  - 📖 **Official Docs**: [WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
  - 🔧 **Installation**: [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
  - ⚡ **Quick Install**: `wsl --install` (PowerShell as Administrator)
  - 📋 **Requirements**: Windows 10 version 2004+ or Windows 11
  - 🔄 **Setup**: Restart required after installation
- **Ubuntu** - WSL distribution
- **Linux** - Target development environment

### 10. Configuration & Dotfiles Agent
**Priority: MEDIUM** - Environment customization

- **zshyzsh** - Clone `git@github.com:YIC-Triumph/zshyzsh` into `~/.config/`
- **zshrc** - Include `export ZSH_CUSTOM=$HOME/.config/zshyzsh`
- **mise config** - Set to `experimental`
- **Symlinks** - Create symlinks for `cursor` and `vscode` in `~/.local/bin`
- **PATH** - Environment variable configuration
- **Environment Variables** - System configuration

### 11. Additional Development Tools
**Priority: LOW-MEDIUM** - Nice-to-have tools

- **grep** - Text search utility
- **fzf** - Fuzzy finder
- **find** - File search utility
- **Glow** - Markdown viewer
- **wget** - File downloader
- **unzip** - Archive extraction
- **tar** - Archive management
- **make** - Build automation
- **top** - Process monitor
- **ping** - Network utility

### 12. Web Development Tools
**Priority: LOW** - Web-specific tools

- **Angular** - Web framework
- **Bootstrap** - CSS framework
- **Tailwind CSS** - Utility-first CSS
- **ESLint** - JavaScript linter
- **Prettier** - Code formatter
- **Black** - Python formatter

### 13. File Formats & Data
**Priority: LOW** - Data handling

- **JSON** - Data format
- **TOML** - Configuration format
- **YAML** - Configuration format
- **Markdown** - Documentation format
- **PDF** - Document format
- **SQL** - Database query language

### 14. Cloud & Services
**Priority: LOW** - External services

- **AWS** - Cloud platform
- **API** - Service integration

### 15. Communication & Productivity
**Priority: LOW** - Team collaboration

- **Microsoft Teams** - Communication platform
- **Chrome** - Web browser
- **Obsidian** - Note-taking application
  - 📖 **Official Docs**: [Obsidian Help](https://help.obsidian.md/)
  - 🔧 **Installation**: [Download and Install Obsidian](https://help.obsidian.md/install)
  - 💾 **Download**: [Obsidian Downloads](https://obsidian.md/download)
  - 🌐 **Platforms**: Available for iOS, Android, macOS, Windows, and Linux
- **Roam Research** - Knowledge management

### 16. Project-Specific Tools
**Priority: VARIABLE** - Project dependencies

- **Trinote** - Project-specific tool
- **sst/opencode** - Install and configure

## Acceptance Criteria by Platform

### WSL/Ubuntu Requirements

#### Core System (Agent Group 1-3)
- [x] zsh installed and set as default shell
- [x] oh-my-zsh installed with basic plugins (git, docker, python)
- [x] mise installed and activation added to zshrc
- [ ] gh installed and authenticated (non-enterprise, SSH key, PAT)
- [ ] SSH ed25519 key generated with no passphrase

#### Development Environment (Agent Group 4-6)
- [x] neovim >= 0.11.0 installed from official package (not apt)
- [ ] LazyVim installed in `~/.config/nvim`
- [ ] Python 3.12.9 installed via mise
- [ ] Node.js latest installed via mise
- [ ] uv@latest installed via mise
- [ ] pipx@latest installed via mise

#### Configuration (Agent Group 10)
- [ ] `git@github.com:YIC-Triumph/zshyzsh` cloned to `~/.config/`
- [ ] zshrc includes `export ZSH_CUSTOM=$HOME/.config/zshyzsh`
- [ ] mise config set to `experimental`
- [ ] Symlinks for `cursor` and `vscode` in `~/.local/bin`

#### AI Tools (Agent Group 8)
- [ ] gptme installed via `pipx install 'gptme[all]'`
- [ ] gptme-rag installed via `pipx install gptme-rag`
- [ ] sst/opencode installed
- [ ] claude-code installed via `npm i -g @anthropic-ai/claude-code`
- [ ] claude-code authenticated with long-running token
- [ ] claude-flow installed via `npm i -g claude-flow@latest`

#### Container Platform (Agent Group 7)
- [ ] Docker can run hello-world container
- [ ] Docker Compose v2 installed and working

### Windows Requirements

#### Core Applications (Agent Group 5 & 9)
- [ ] Hack Nerd Font Mono downloaded and installed
- [ ] Alacritty terminal downloaded and installed
- [ ] Alacritty configured to start WSL as Windows user (not admin)
- [ ] Docker Desktop downloaded and installed

## Installation Dependencies (Execution Order)

### Phase 1: Foundation
1. Windows setup (if applicable)
2. WSL/Ubuntu installation
3. Package managers (apt, snap)

### Phase 2: Core Shell
1. zsh installation
2. oh-my-zsh setup
3. Basic shell configuration

### Phase 3: Development Foundation
1. mise installation
2. Git setup
3. SSH key generation
4. GitHub authentication

### Phase 4: Development Tools
1. Neovim installation
2. LazyVim setup
3. Language installations (Python, Node.js, Go, Rust)

### Phase 5: Configuration
1. Clone zshyzsh configuration
2. Configure dotfiles
3. Create symlinks

### Phase 6: AI & Advanced Tools
1. Install AI development tools
2. Configure claude-code authentication
3. Set up additional development utilities

### Phase 7: Containerization
1. Docker Desktop (Windows)
2. Docker CLI (WSL)
3. Docker Compose

### Phase 8: Optional Tools
1. Web development frameworks
2. Additional utilities
3. Communication tools

## Agent Communication Protocol

Each agent will:
1. **Report status** to BaiosCoordinator
2. **Check dependencies** before execution
3. **Verify completion** against acceptance criteria
4. **Handle rollback** if verification fails
5. **Request human input** when needed (passwords, confirmations)

## Quality Assurance

QA Verification Agent will validate:
- ✅ **Installation Success** - Tool is installed and accessible
- ✅ **Version Requirements** - Meets minimum version requirements
- ✅ **Functionality Test** - Basic functionality works (e.g., Docker hello-world)
- ✅ **Configuration Correct** - Settings are properly configured
- ✅ **Integration Working** - Tool integrates with other components

---

**Total Items: 78+ tools and configurations**  
**Agent Groups: 16 specialized domains**  
**Estimated Installation Time: 2-4 hours (depending on internet speed)**