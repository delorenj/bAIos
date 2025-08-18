# 🔧 Git Authentication Troubleshooting Guide

## 🚨 Emergency Authentication Recovery Procedures

### Problem 1: "Permission denied (publickey)" Error

**Symptoms:**
```bash
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Solution Sequence:**
```bash
# 1. Check if SSH key exists
ls -la ~/.ssh/id_ed25519*

# 2. If no key, generate one
ssh-keygen -t ed25519 -C "your.email@domain.com"

# 3. Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 4. Copy public key
cat ~/.ssh/id_ed25519.pub

# 5. Add to GitHub (Settings → SSH and GPG keys)

# 6. Test connection
ssh -T git@github.com
```

### Problem 2: GitHub CLI Not Authenticated

**Symptoms:**
```bash
gh auth status
# Returns: Not logged in
```

**Solution:**
```bash
# Re-authenticate with CLI
gh auth login --protocol ssh --web

# Verify authentication
gh auth status
```

### Problem 3: ZSH_CUSTOM Points to Non-existent Directory

**Symptoms:**
```bash
echo $ZSH_CUSTOM
# Shows path that doesn't exist
```

**Solution:**
```bash
# 1. Check if directory should exist
ls -la ~/.config/zshyzsh

# 2. If missing, clone repository
git clone git@github.com:delorenj/zshyzsh.git ~/.config/zshyzsh

# 3. Verify ZSH_CUSTOM in ~/.zshrc
grep ZSH_CUSTOM ~/.zshrc
```

### Problem 4: Repository Clone Fails

**Symptoms:**
```bash
git clone git@github.com:delorenj/zshyzsh.git ~/.config/zshyzsh
# Fails with authentication error
```

**Solution Ladder:**
```bash
# Option 1: Check SSH authentication
ssh -T git@github.com

# Option 2: Try HTTPS as fallback
git clone https://github.com/delorenj/zshyzsh.git ~/.config/zshyzsh

# Option 3: Switch back to SSH after clone
cd ~/.config/zshyzsh
git remote set-url origin git@github.com:delorenj/zshyzsh.git
```

### Problem 5: Symlinks Broken or Missing

**Symptoms:**
```bash
ls -la ~/.config/ | grep zshyzsh
# Shows broken links or missing links
```

**Solution:**
```bash
# Remove broken links
find ~/.config/ -type l -not -path "*/zshyzsh/*" -exec readlink {} + | grep zshyzsh | xargs rm -f

# Recreate symlinks
cd ~/.config
ln -sf zshyzsh/alacritty alacritty
ln -sf zshyzsh/gptme gptme
ln -sf zshyzsh/opencode opencode
ln -sf zshyzsh/zellij zellij
```

## 🔄 Complete Reset Procedure

If everything is broken, follow this nuclear option:

```bash
# 1. Back up existing config
mv ~/.config/zshyzsh ~/.config/zshyzsh-backup-$(date +%Y%m%d-%H%M%S)

# 2. Remove broken symlinks
find ~/.config/ -type l -not -path "*/zshyzsh/*" -exec readlink {} + | grep zshyzsh | xargs rm -f

# 3. Re-clone repository
git clone git@github.com:delorenj/zshyzsh.git ~/.config/zshyzsh

# 4. Switch to correct branch
cd ~/.config/zshyzsh
git checkout ubuntu-dev

# 5. Recreate symlinks
cd ~/.config
ln -sf zshyzsh/alacritty alacritty
ln -sf zshyzsh/gptme gptme
ln -sf zshyzsh/opencode opencode
ln -sf zshyzsh/zellij zellij

# 6. Verify ZSH_CUSTOM
echo $ZSH_CUSTOM
```

## 🔍 Diagnostic Commands

### Authentication Status Check
```bash
# SSH key status
ls -la ~/.ssh/id_ed25519*

# GitHub CLI status
gh auth status

# SSH connection test
ssh -T git@github.com

# Git configuration
git config --global user.name
git config --global user.email
```

### Repository Health Check
```bash
# Repository status
cd ~/.config/zshyzsh && git status

# Remote configuration
cd ~/.config/zshyzsh && git remote -v

# Branch information
cd ~/.config/zshyzsh && git branch -a
```

### Configuration Integrity Check
```bash
# ZSH_CUSTOM variable
echo $ZSH_CUSTOM

# Directory exists
test -d "$ZSH_CUSTOM" && echo "Directory exists" || echo "Directory missing"

# Symlink status
ls -la ~/.config/ | grep -E "(alacritty|gptme|opencode|zellij)"
```

## 🚨 Emergency Contact Points

If all else fails:
1. Check GitHub status page
2. Verify network connectivity
3. Check SSH agent status: `ssh-add -l`
4. Restart SSH agent: `eval "$(ssh-agent -s)"`
5. Re-add keys: `ssh-add ~/.ssh/id_ed25519`

---

*Your Git Authentication Expert - Turning authentication chaos into ordered harmony!*