# WSL Environment Dependency Analysis

## Overview

This document provides a comprehensive dependency map for the WSL development environment specification, identifying critical path dependencies, potential circular dependencies, and components suitable for parallel installation.

## System-Level Dependencies

### Host OS Foundation
```
Windows 11/10
├── WSL 2 Installation
├── Docker Desktop (WSL 2 backend)
├── Alacritty Terminal
└── Hack Nerd Font Mono
```

**Dependencies:**
- Windows 11/10 → WSL 2 → Ubuntu 22.04+
- Docker Desktop → WSL 2 Backend → Ubuntu distribution
- Alacritty → Hack Nerd Font Mono → Windows font installation

**Critical Path:** Windows → WSL 2 → Ubuntu (blocking all other components)

## Shell Environment Dependencies

### Core Shell Chain
```
Ubuntu 22.04+
├── apt update/upgrade → curl → zsh
├── zsh → oh-my-zsh → zshyzsh configuration
├── oh-my-zsh → Git (for plugins: git, docker, python)
└── zshyzsh → SSH key → GitHub authentication
```

**Critical Dependencies:**
1. `apt update` (blocks all package installations)
2. `curl` (required for oh-my-zsh, mise, GitHub CLI installations)
3. `zsh` → `oh-my-zsh` → `zshyzsh` (sequential dependency chain)
4. `ZSH_CUSTOM=$HOME/.config/zshyzsh` (blocks shell configuration)

**Circular Dependency Alert:**
- `zshyzsh` repository requires GitHub access
- GitHub access requires SSH key and GitHub CLI
- But `zshyzsh` contains configuration needed for proper environment

**Resolution Strategy:**
1. Install zsh → oh-my-zsh → basic GitHub CLI
2. Generate SSH key and authenticate with GitHub
3. Clone zshyzsh repository  
4. Configure ZSH_CUSTOM and reload shell

## Authentication Chain Dependencies

### GitHub Access Pipeline
```
SSH Key Generation
├── ssh-keygen -t ed25519 (requires Git)
├── GitHub CLI installation
├── GitHub CLI authentication (PAT token)
├── SSH key addition to GitHub account
└── Repository access enabled
```

**Critical Dependencies:**
- Git → SSH key generation
- SSH key → GitHub CLI authentication  
- GitHub CLI → SSH key upload to GitHub
- GitHub authentication → zshyzsh repository access
- zshyzsh → environment secrets (GITHUB_PERSONAL_ACCESS_TOKEN)

**Potential Circular Issue:**
- zshyzsh contains `secrets.zsh` with `GITHUB_PERSONAL_ACCESS_TOKEN`
- But GitHub access is needed to clone zshyzsh
- Resolution: Use initial PAT for GitHub CLI auth, then source secrets from zshyzsh

## Version Management Dependencies

### Mise Ecosystem
```
curl (foundation)
├── mise installation
├── mise zsh integration (requires zsh + oh-my-zsh)
├── mise tools installation
│   ├── python@3.12.9
│   ├── nodejs@latest  
│   ├── pnpm@latest
│   ├── uv@latest
│   └── pipx@latest
└── AI tool installations (depend on mise tools)
```

**Critical Dependencies:**
- `curl` → `mise` installation
- `zsh` + `oh-my-zsh` → `mise activate zsh` integration
- `mise` → all language runtime installations
- Language runtimes → language-specific tools (npm packages, pipx packages)

**Parallel Installation Opportunities:**
- After mise is installed and activated, all `mise install` commands can run in parallel
- Node.js packages can install in parallel after Node.js runtime is ready
- Python packages can install in parallel after Python runtime is ready

## Configuration Dependencies

### Configuration File Linkage
```
zshyzsh Repository (central configuration hub)
├── ~/.zshrc ← ZSH_CUSTOM export
├── gptme/config.toml ← symlinked to ~/.config/gptme/config.toml
├── zellij/ ← symlinked to ~/.config/zellij  
├── alacritty/alacritty.yml ← copied to Windows
├── secrets.zsh ← environment variables
└── mcp/triumph-tools.json ← Claude Code MCP config
```

**Dependencies:**
- All configurations → zshyzsh repository availability
- zshyzsh → GitHub authentication
- Symlink operations → target applications installed
- Environment secrets → shell reload for availability

**Configuration Order:**
1. Clone zshyzsh repository
2. Set ZSH_CUSTOM environment variable
3. Install target applications (gptme, zellij, etc.)
4. Create symlinks
5. Copy Windows configurations
6. Source environment variables

## Cross-Component Relationships

### Tool Integration Matrix

| Component | Depends On | Enables | Parallel With |
|-----------|------------|---------|---------------|
| WSL 2 | Windows | All other components | Docker Desktop |
| curl | apt update | mise, oh-my-zsh, GitHub CLI | git, zsh |
| zsh | curl, apt | oh-my-zsh | git |
| oh-my-zsh | zsh, curl | zshyzsh integration | git |
| mise | curl, zsh | all language runtimes | git, GitHub CLI |
| Git | apt | SSH key generation | zsh, curl |
| GitHub CLI | curl, git | repository access | zsh |
| SSH key | git | GitHub authentication | - |
| zshyzsh | GitHub access | environment config | - |
| Python | mise | pipx, gptme, uv | Node.js |
| Node.js | mise | npm packages | Python |
| pipx | Python | gptme, gptme-rag | npm packages |
| Docker | Host Docker Desktop | container operations | all other tools |

### Critical Path Blockers

**Highest Priority (Sequential Only):**
1. Windows → WSL 2 → Ubuntu
2. apt update → curl 
3. curl → oh-my-zsh, mise, GitHub CLI
4. zsh → oh-my-zsh → zshyzsh integration
5. GitHub CLI + SSH → zshyzsh repository access

**Medium Priority (Some Parallelization):**
1. mise → language runtimes (can be parallel)
2. Language runtimes → language-specific tools (can be parallel within language)
3. zshyzsh → configuration linking (some can be parallel)

**Low Priority (Highly Parallel):**
1. System utilities (grep, fzf, jq, etc.)
2. Additional development tools
3. Documentation and validation

## Parallel Installation Strategies

### Phase 1: Foundation (Sequential)
```bash
# Must be sequential
1. Install WSL 2 + Ubuntu
2. apt update && apt upgrade -y
3. Install: curl, git, zsh
4. Install oh-my-zsh
5. Set zsh as default shell
```

### Phase 2: Core Tools (Limited Parallel)
```bash
# Can run in parallel after Phase 1
parallel_group_1: {
  install_mise,
  install_github_cli,
  generate_ssh_key
}

# Sequential dependency
authenticate_github_cli
clone_zshyzsh_repo
configure_zsh_custom
```

### Phase 3: Language Runtimes (Highly Parallel)
```bash
# All can run in parallel after mise is configured
parallel_group_2: {
  mise install python@3.12.9,
  mise install nodejs@latest,
  mise install pnpm@latest,
  mise install uv@latest,
  mise install pipx@latest
}
```

### Phase 4: Language-Specific Tools (Parallel by Language)
```bash
# Node.js packages (parallel)
npm_parallel: {
  npm install -g @anthropic-ai/claude-code,
  npm install -g claude-flow@latest,  
  npm install -g @google/gemini-cli@latest
}

# Python packages (parallel)  
pipx_parallel: {
  pipx install 'gptme[all]',
  pipx install gptme-rag
}
```

### Phase 5: Configuration & Validation (Mixed)
```bash
# Configuration linking (some parallel)
config_parallel: {
  symlink_gptme_config,
  symlink_zellij_config,
  copy_alacritty_config_to_windows
}

# Validation (all parallel)
validation_parallel: {
  test_all_commands,
  verify_github_auth,
  validate_docker_access,
  check_environment_variables
}
```

## Potential Conflicts & Resolutions

### 1. Node.js Version Conflict
**Issue:** System Node.js vs mise-managed Node.js
**Resolution:** Ensure mise activates in shell before system PATH

### 2. Python Virtual Environment Conflicts  
**Issue:** System Python vs mise Python vs virtual environments
**Resolution:** Use mise for global Python, virtual environments for projects

### 3. ZSH Configuration Loading Order
**Issue:** oh-my-zsh vs zshyzsh vs mise activation order
**Resolution:** Load order: oh-my-zsh → zshyzsh (ZSH_CUSTOM) → mise activation

### 4. SSH Agent Configuration
**Issue:** SSH key not automatically loaded
**Resolution:** Configure SSH agent in zshyzsh configuration

### 5. Docker Permission Issues
**Issue:** WSL user not in docker group
**Resolution:** Add user to docker group, restart WSL

## Installation Recommendations

### Critical Path Focus
1. **Prioritize blocking dependencies:** Get WSL, curl, zsh, oh-my-zsh working first
2. **GitHub authentication early:** Needed for zshyzsh repository access
3. **mise configuration before tools:** All language runtimes depend on mise

### Parallelization Opportunities
1. **System utilities:** Can install anytime after apt update
2. **Language tools:** Can install in parallel after respective runtimes
3. **Configuration linking:** Can happen in parallel for unrelated configs

### Error Recovery Strategies
1. **GitHub access failures:** Have backup PAT ready, verify SSH key format
2. **mise installation issues:** Verify curl works, check shell integration
3. **Configuration conflicts:** Keep backup of original configs before linking

## Validation Dependencies

Each validation step has its own dependency chain:

```
Command Validations:
├── zsh --version (depends on: zsh installation)
├── mise --version (depends on: mise installation + shell integration)  
├── gh auth status (depends on: GitHub CLI + authentication)
├── ssh -T git@github.com (depends on: SSH key + GitHub setup)
├── nvim --version (depends on: Neovim installation)
├── python --version (depends on: mise + Python installation)
├── docker run hello-world (depends on: Docker Desktop + WSL integration)
└── claude --version (depends on: Node.js + claude-code installation)
```

This dependency analysis provides a roadmap for systematic WSL environment provisioning with optimal parallelization and conflict avoidance.