#!/usr/bin/env python3
"""
bAIos inventory parser.

This module provides functionality to parse the INVENTORY.md file
and convert it into structured inventory data models.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..models.inventory import (
    InventoryItem, 
    InventorySection, 
    InventoryReport, 
    InventoryStatus
)


class InventoryParser:
    """
    Parser for INVENTORY.md file that extracts requirements and converts
    them into structured inventory data models.
    """
    
    def __init__(self, inventory_file: Optional[Path] = None):
        """
        Initialize the parser with the inventory file path.
        
        Args:
            inventory_file: Path to INVENTORY.md file. If None, uses default location.
        """
        if inventory_file is None:
            # Default to docs/INVENTORY.md relative to the CLI root
            self.inventory_file = Path(__file__).parent.parent.parent.parent / "docs" / "INVENTORY.md"
        else:
            self.inventory_file = Path(inventory_file)
        
        self.content = ""
        self.sections = []
        self.env_keys = []
    
    def parse(self) -> InventoryReport:
        """
        Parse the inventory file and return a structured report.
        
        Returns:
            InventoryReport: Structured inventory data
        
        Raises:
            FileNotFoundError: If inventory file doesn't exist
            ValueError: If file content cannot be parsed
        """
        if not self.inventory_file.exists():
            raise FileNotFoundError(f"Inventory file not found: {self.inventory_file}")
        
        # Read the file content
        with open(self.inventory_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        # Parse different sections
        self._parse_env_keys()
        self._parse_acceptance_criteria()
        
        # Create and return the report
        report = InventoryReport(
            sections=self.sections,
            env_keys=self.env_keys,
            generated_at=datetime.now().isoformat(),
            metadata={
                "source_file": str(self.inventory_file),
                "parser_version": "1.0.0"
            }
        )
        
        return report
    
    def _parse_env_keys(self):
        """Parse the Required .env Keys section."""
        env_section_pattern = r"## Required \.env Keys\s*\n(.*?)(?=##|\Z)"
        env_match = re.search(env_section_pattern, self.content, re.DOTALL)
        
        if not env_match:
            return
        
        env_content = env_match.group(1)
        
        # Extract environment keys
        env_key_pattern = r"^-\s+([A-Z_]+)(?:\s+\(.*?\))?"
        for line in env_content.strip().split('\n'):
            match = re.match(env_key_pattern, line.strip())
            if match:
                self.env_keys.append(match.group(1))
    
    def _parse_acceptance_criteria(self):
        """Parse the Acceptance Criteria section."""
        criteria_pattern = r"## Acceptance Criteria\s*\n(.*?)(?=##|\Z)"
        criteria_match = re.search(criteria_pattern, self.content, re.DOTALL)
        
        if not criteria_match:
            return
        
        criteria_content = criteria_match.group(1)
        
        # Split into platform-specific sections
        self._parse_platform_sections(criteria_content)
    
    def _parse_platform_sections(self, content: str):
        """Parse platform-specific sections (WSL/Ubuntu, Windows, etc.)."""
        # Pattern to match **SectionName** followed by list items
        section_pattern = r"\*\*(.*?)\*\*\s*\n((?:^-.*\n?)*)"
        sections = re.findall(section_pattern, content, re.MULTILINE)
        
        for section_name, section_content in sections:
            section_name = section_name.strip()
            inventory_section = InventorySection(
                name=section_name,
                description=f"Requirements for {section_name} platform"
            )
            
            # Parse individual requirements
            requirements = self._parse_requirements(section_content)
            
            for req_text in requirements:
                item = self._create_inventory_item(req_text, section_name)
                inventory_section.add_item(item)
            
            if inventory_section.items:  # Only add if it has items
                self.sections.append(inventory_section)
    
    def _parse_requirements(self, section_content: str) -> List[str]:
        """Parse individual requirements from section content."""
        requirements = []
        
        # Split by lines and find bullet points
        lines = section_content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- '):
                # Remove the bullet point and clean up
                req_text = line[2:].strip()
                if req_text:
                    requirements.append(req_text)
        
        return requirements
    
    def _create_inventory_item(self, requirement_text: str, section_name: str) -> InventoryItem:
        """
        Create an InventoryItem from a requirement text.
        
        Args:
            requirement_text: The requirement description
            section_name: The section this requirement belongs to
        
        Returns:
            InventoryItem: Structured inventory item
        """
        # Generate a unique ID based on the requirement text
        item_id = self._generate_item_id(requirement_text)
        
        # Determine category based on content
        category = self._determine_category(requirement_text)
        
        # Create basic inventory item
        item = InventoryItem(
            id=item_id,
            description=requirement_text,
            section=section_name,
            category=category,
            status=InventoryStatus.NOT_STARTED_REQUIRED,
            metadata=self._extract_metadata(requirement_text)
        )
        
        # Add check and install commands based on the requirement
        self._add_command_suggestions(item, requirement_text)
        
        return item
    
    def _generate_item_id(self, text: str) -> str:
        """Generate a unique ID from requirement text."""
        # Extract key words and create ID
        # Remove common words and keep important ones
        stopwords = {
            'is', 'are', 'and', 'the', 'to', 'with', 'from', 'for', 'of', 'in', 
            'at', 'by', 'on', 'as', 'be', 'or', 'an', 'a', 'all', 'any', 'can'
        }
        
        # Clean and tokenize
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [w for w in clean_text.split() if w and w not in stopwords]
        
        # Take first few significant words
        key_words = words[:4]
        item_id = '_'.join(key_words)
        
        # Ensure it's not too long
        return item_id[:50]
    
    def _determine_category(self, text: str) -> str:
        """Determine the category of the requirement based on content."""
        text_lower = text.lower()
        
        categories = {
            'shell': ['zsh', 'shell', 'ohmyzsh', 'bash'],
            'development_tools': ['neovim', 'lazyvim', 'nvim', 'editor'],
            'package_managers': ['mise', 'pipx', 'npm', 'pip'],
            'version_control': ['git', 'github', 'gh', 'ssh', 'key'],
            'runtime': ['python', 'nodejs', 'node', 'uv'],
            'containerization': ['docker', 'container', 'compose'],
            'ai_tools': ['gptme', 'claude-code', 'claude-flow', 'opencode'],
            'fonts': ['font', 'nerd font', 'hack'],
            'terminals': ['alacritty', 'terminal'],
            'symlinks': ['symlink', 'link', 'cursor', 'vscode'],
            'config': ['config', 'configuration', 'zshrc'],
            'authentication': ['auth', 'login', 'token', 'pat']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_metadata(self, text: str) -> Dict:
        """Extract metadata from requirement text."""
        metadata = {}
        
        # Extract version requirements
        version_match = re.search(r'>?v?(\d+\.?\d*\.?\d*)', text)
        if version_match:
            metadata['version_requirement'] = version_match.group(1)
        
        # Extract file paths
        path_matches = re.findall(r'[`"]([~/\.\w\/-]+)[`"]', text)
        if path_matches:
            metadata['paths'] = path_matches
        
        # Extract URLs
        url_matches = re.findall(r'(https?://[^\s]+)', text)
        if url_matches:
            metadata['urls'] = url_matches
        
        # Extract command mentions
        if 'using' in text or 'with' in text:
            command_match = re.search(r'using\s+[`"](.+?)[`"]|with\s+[`"](.+?)[`"]', text)
            if command_match:
                metadata['install_method'] = command_match.group(1) or command_match.group(2)
        
        return metadata
    
    def _add_command_suggestions(self, item: InventoryItem, text: str):
        """Add suggested check and install commands based on the requirement."""
        text_lower = text.lower()
        
        # Common tool mappings
        command_mappings = {
            'zsh': {
                'check': 'which zsh && echo $SHELL',
                'install': 'sudo apt install zsh && chsh -s $(which zsh)'
            },
            'ohmyzsh': {
                'check': 'test -d ~/.oh-my-zsh && echo "Oh My Zsh installed"',
                'install': 'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
            },
            'mise': {
                'check': 'mise --version',
                'install': 'curl https://mise.run | sh'
            },
            'gh': {
                'check': 'gh --version && gh auth status',
                'install': 'sudo apt install gh'
            },
            'neovim': {
                'check': 'nvim --version',
                'install': 'curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux64.tar.gz'
            },
            'docker': {
                'check': 'docker --version && docker run hello-world',
                'install': 'curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh'
            },
            'gptme': {
                'check': 'gptme --version',
                'install': 'pipx install \'gptme[all]\''
            },
            'claude-code': {
                'check': 'claude --version',
                'install': 'npm i -g @anthropic-ai/claude-code'
            },
            'claude-flow': {
                'check': 'claude-flow --version',
                'install': 'npm i -g claude-flow@latest'
            },
            'python': {
                'check': 'python3 --version',
                'install': 'mise install python@3.12.9'
            },
            'nodejs': {
                'check': 'node --version',
                'install': 'mise install nodejs@latest'
            }
        }
        
        # Find matching commands
        for tool, commands in command_mappings.items():
            if tool in text_lower:
                if 'check' in commands:
                    item.check_command = commands['check']
                if 'install' in commands:
                    item.install_command = commands['install']
                break
        
        # Special handling for complex requirements
        if 'ssh' in text_lower and 'key' in text_lower:
            item.check_command = 'test -f ~/.ssh/id_ed25519 && echo "SSH key exists"'
            item.install_command = 'ssh-keygen -t ed25519 -C "baios@setup" -N ""'
        
        if 'symlink' in text_lower:
            if 'cursor' in text_lower:
                item.check_command = 'test -L ~/.local/bin/cursor && echo "Cursor symlink exists"'
                item.install_command = 'ln -sf /mnt/c/Users/$(whoami)/AppData/Local/Programs/cursor/cursor.exe ~/.local/bin/cursor'
            elif 'vscode' in text_lower:
                item.check_command = 'test -L ~/.local/bin/code && echo "VSCode symlink exists"'
                item.install_command = 'ln -sf /mnt/c/Users/$(whoami)/AppData/Local/Programs/Microsoft\\ VS\\ Code/bin/code ~/.local/bin/code'
    
    def validate_report(self, report: InventoryReport) -> Tuple[bool, List[str]]:
        """
        Validate the parsed report for consistency and completeness.
        
        Args:
            report: The inventory report to validate
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if we have sections
        if not report.sections:
            issues.append("No inventory sections found")
        
        # Check if we have environment keys
        if not report.env_keys:
            issues.append("No environment keys found")
        
        # Validate each section
        for section in report.sections:
            if not section.items:
                issues.append(f"Section '{section.name}' has no items")
            
            # Check for duplicate IDs within section
            item_ids = [item.id for item in section.items]
            if len(item_ids) != len(set(item_ids)):
                issues.append(f"Section '{section.name}' has duplicate item IDs")
        
        # Check for critical items without check commands
        critical_items = [item for item in report.get_all_items() if item.is_critical]
        missing_checks = [item for item in critical_items if not item.check_command]
        
        if missing_checks:
            issues.append(f"{len(missing_checks)} critical items missing check commands")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def get_sample_report() -> InventoryReport:
        """
        Generate a sample report for testing purposes.
        
        Returns:
            InventoryReport: Sample report with test data
        """
        # Create sample sections
        wsl_section = InventorySection(
            name="WSL/Ubuntu",
            description="Requirements for WSL/Ubuntu platform"
        )
        
        # Add sample items
        wsl_items = [
            InventoryItem(
                id="zsh_installed_default",
                description="zsh is installed and set to the default shell",
                section="WSL/Ubuntu",
                category="shell",
                status=InventoryStatus.NOT_STARTED_REQUIRED,
                check_command="which zsh && echo $SHELL",
                install_command="sudo apt install zsh && chsh -s $(which zsh)"
            ),
            InventoryItem(
                id="docker_hello_world",
                description="docker can bring up the hello world container",
                section="WSL/Ubuntu", 
                category="containerization",
                status=InventoryStatus.NOT_STARTED_REQUIRED,
                check_command="docker run hello-world",
                install_command="curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
            )
        ]
        
        for item in wsl_items:
            wsl_section.add_item(item)
        
        # Create sample report
        report = InventoryReport(
            sections=[wsl_section],
            env_keys=["GITHUB_PERSONAL_ACCESS_TOKEN", "OPENROUTER_API_KEY"],
            generated_at=datetime.now().isoformat(),
            metadata={
                "source": "sample_data",
                "parser_version": "1.0.0"
            }
        )
        
        return report