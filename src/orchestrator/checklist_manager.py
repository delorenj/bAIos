"""
Checklist Management System
===========================

Manages execution checklists and validation criteria for WSL provisioning.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path


class ChecklistStatus(str, Enum):
    """Status values for checklist items."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class ChecklistPriority(str, Enum):
    """Priority levels for checklist items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class ChecklistItem:
    """Individual checklist item."""
    id: str
    name: str
    description: str
    category: str
    priority: ChecklistPriority
    status: ChecklistStatus = ChecklistStatus.PENDING
    agent_type: Optional[str] = None
    dependencies: List[str] = None
    validation_command: Optional[str] = None
    success_criteria: List[str] = None
    failure_reasons: List[str] = None
    execution_time: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.success_criteria is None:
            self.success_criteria = []
        if self.failure_reasons is None:
            self.failure_reasons = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChecklistItem':
        """Create from dictionary."""
        return cls(**data)
    
    def is_ready_to_execute(self, completed_items: List[str]) -> bool:
        """Check if item is ready to execute based on dependencies."""
        if self.status != ChecklistStatus.PENDING:
            return False
        
        # Check if all dependencies are completed
        for dep_id in self.dependencies:
            if dep_id not in completed_items:
                return False
        
        return True
    
    def can_retry(self) -> bool:
        """Check if item can be retried."""
        return self.retry_count < self.max_retries


@dataclass
class ChecklistCategory:
    """Category grouping for checklist items."""
    id: str
    name: str
    description: str
    items: List[ChecklistItem] = None
    required: bool = True
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


class ChecklistManager:
    """Manages execution checklists for WSL provisioning."""
    
    def __init__(self, session_id: str):
        """
        Initialize checklist manager.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.categories: Dict[str, ChecklistCategory] = {}
        self.items: Dict[str, ChecklistItem] = {}
        self.execution_order: List[str] = []
        
        logging.info(f"Initialized ChecklistManager for session {session_id}")
        
        # Load default WSL provisioning checklist
        self._load_default_checklist()
    
    def _load_default_checklist(self):
        """Load the default WSL provisioning checklist."""
        
        # System Setup Category
        system_category = ChecklistCategory(
            id="system_setup",
            name="System Setup",
            description="Basic system configuration and package management",
            required=True
        )
        
        system_items = [
            ChecklistItem(
                id="update_system",
                name="Update System Packages",
                description="Update apt package lists and upgrade system packages",
                category="system_setup",
                priority=ChecklistPriority.CRITICAL,
                agent_type="installer",
                validation_command="apt list --upgradable | wc -l",
                success_criteria=["System packages updated", "No critical vulnerabilities"]
            ),
            ChecklistItem(
                id="install_base_tools",
                name="Install Base Development Tools",
                description="Install essential development tools (curl, git, build-essential, etc.)",
                category="system_setup",
                priority=ChecklistPriority.CRITICAL,
                agent_type="installer",
                dependencies=["update_system"],
                validation_command="command -v curl && command -v git && command -v gcc",
                success_criteria=["curl available", "git available", "build tools available"]
            ),
            ChecklistItem(
                id="configure_timezone",
                name="Configure Timezone",
                description="Set system timezone and locale settings",
                category="system_setup",
                priority=ChecklistPriority.MEDIUM,
                agent_type="installer",
                validation_command="timedatectl show --property=Timezone",
                success_criteria=["Timezone configured correctly"]
            )
        ]
        
        system_category.items = system_items
        self.categories["system_setup"] = system_category
        
        # Shell Configuration Category
        shell_category = ChecklistCategory(
            id="shell_config",
            name="Shell Configuration",
            description="Configure zsh, oh-my-zsh, and shell environment",
            required=True
        )
        
        shell_items = [
            ChecklistItem(
                id="install_zsh",
                name="Install Zsh Shell",
                description="Install zsh and set as default shell",
                category="shell_config",
                priority=ChecklistPriority.HIGH,
                agent_type="shell_master",
                dependencies=["install_base_tools"],
                validation_command="echo $SHELL | grep zsh",
                success_criteria=["zsh installed", "zsh set as default shell"]
            ),
            ChecklistItem(
                id="install_oh_my_zsh",
                name="Install Oh-My-Zsh",
                description="Install oh-my-zsh framework with themes and plugins",
                category="shell_config",
                priority=ChecklistPriority.HIGH,
                agent_type="shell_master",
                dependencies=["install_zsh"],
                validation_command="test -d ~/.oh-my-zsh",
                success_criteria=["oh-my-zsh installed", "powerlevel10k theme configured"]
            ),
            ChecklistItem(
                id="configure_shell_plugins",
                name="Configure Shell Plugins",
                description="Install and configure useful zsh plugins",
                category="shell_config",
                priority=ChecklistPriority.MEDIUM,
                agent_type="shell_master",
                dependencies=["install_oh_my_zsh"],
                validation_command="grep 'zsh-autosuggestions\\|zsh-syntax-highlighting' ~/.zshrc",
                success_criteria=["autosuggestions plugin active", "syntax highlighting active"]
            )
        ]
        
        shell_category.items = shell_items
        self.categories["shell_config"] = shell_category
        
        # Language Management Category
        lang_category = ChecklistCategory(
            id="language_management",
            name="Language Management",
            description="Setup mise and install programming languages",
            required=True
        )
        
        lang_items = [
            ChecklistItem(
                id="install_mise",
                name="Install Mise Tool Manager",
                description="Install mise for managing programming language versions",
                category="language_management",
                priority=ChecklistPriority.HIGH,
                agent_type="mise_master",
                dependencies=["configure_shell_plugins"],
                validation_command="command -v mise",
                success_criteria=["mise installed", "mise available in PATH"]
            ),
            ChecklistItem(
                id="install_python",
                name="Install Python 3.12.9",
                description="Install Python 3.12.9 via mise",
                category="language_management",
                priority=ChecklistPriority.HIGH,
                agent_type="mise_master",
                dependencies=["install_mise"],
                validation_command="python --version | grep '3.12.9'",
                success_criteria=["Python 3.12.9 installed", "Python available globally"]
            ),
            ChecklistItem(
                id="install_nodejs",
                name="Install Node.js Latest",
                description="Install latest Node.js via mise",
                category="language_management",
                priority=ChecklistPriority.HIGH,
                agent_type="mise_master",
                dependencies=["install_mise"],
                validation_command="node --version && npm --version",
                success_criteria=["Node.js installed", "npm available"]
            )
        ]
        
        lang_category.items = lang_items
        self.categories["language_management"] = lang_category
        
        # Authentication Setup Category
        auth_category = ChecklistCategory(
            id="authentication",
            name="Authentication Setup",
            description="Configure git, SSH keys, and authentication",
            required=True
        )
        
        auth_items = [
            ChecklistItem(
                id="configure_git",
                name="Configure Git",
                description="Set up git user name, email, and default settings",
                category="authentication",
                priority=ChecklistPriority.HIGH,
                agent_type="authorizer",
                dependencies=["install_base_tools"],
                validation_command="git config --global user.name && git config --global user.email",
                success_criteria=["Git user name set", "Git email set", "Git configured"]
            ),
            ChecklistItem(
                id="generate_ssh_key",
                name="Generate SSH Key",
                description="Generate ed25519 SSH key for authentication",
                category="authentication",
                priority=ChecklistPriority.HIGH,
                agent_type="authorizer",
                dependencies=["configure_git"],
                validation_command="test -f ~/.ssh/id_ed25519",
                success_criteria=["SSH key generated", "SSH key added to agent"]
            ),
            ChecklistItem(
                id="configure_ssh_config",
                name="Configure SSH Config",
                description="Set up SSH client configuration",
                category="authentication",
                priority=ChecklistPriority.MEDIUM,
                agent_type="authorizer",
                dependencies=["generate_ssh_key"],
                validation_command="test -f ~/.ssh/config",
                success_criteria=["SSH config file created", "SSH settings configured"]
            )
        ]
        
        auth_category.items = auth_items
        self.categories["authentication"] = auth_category
        
        # Development Environment Category
        dev_category = ChecklistCategory(
            id="development_environment",
            name="Development Environment",
            description="Setup development tools and editors",
            required=False
        )
        
        dev_items = [
            ChecklistItem(
                id="install_docker_integration",
                name="Configure Docker Integration",
                description="Ensure Docker Desktop WSL integration works",
                category="development_environment",
                priority=ChecklistPriority.MEDIUM,
                agent_type="installer",
                dependencies=["install_base_tools"],
                validation_command="command -v docker && docker ps",
                success_criteria=["Docker command available", "Docker daemon accessible"]
            ),
            ChecklistItem(
                id="install_neovim",
                name="Install Neovim",
                description="Install and configure Neovim editor",
                category="development_environment",
                priority=ChecklistPriority.OPTIONAL,
                agent_type="installer",
                dependencies=["install_python"],
                validation_command="command -v nvim",
                success_criteria=["Neovim installed", "Neovim configuration available"]
            )
        ]
        
        dev_category.items = dev_items
        self.categories["development_environment"] = dev_category
        
        # Build items dictionary and execution order
        self._build_items_index()
        self._calculate_execution_order()
    
    def _build_items_index(self):
        """Build index of all items by ID."""
        self.items = {}
        for category in self.categories.values():
            for item in category.items:
                self.items[item.id] = item
    
    def _calculate_execution_order(self):
        """Calculate optimal execution order based on dependencies."""
        visited = set()
        temp_visited = set()
        order = []
        
        def dfs_visit(item_id: str):
            if item_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {item_id}")
            if item_id in visited:
                return
            
            temp_visited.add(item_id)
            
            item = self.items[item_id]
            for dep_id in item.dependencies:
                if dep_id in self.items:
                    dfs_visit(dep_id)
            
            temp_visited.remove(item_id)
            visited.add(item_id)
            order.append(item_id)
        
        # Process all items
        for item_id in self.items:
            if item_id not in visited:
                dfs_visit(item_id)
        
        self.execution_order = order
        logging.info(f"Calculated execution order with {len(order)} items")
    
    def get_ready_items(self) -> List[ChecklistItem]:
        """Get items that are ready to execute."""
        completed_items = [
            item_id for item_id, item in self.items.items() 
            if item.status == ChecklistStatus.COMPLETED
        ]
        
        ready_items = []
        for item_id in self.execution_order:
            item = self.items[item_id]
            if item.is_ready_to_execute(completed_items):
                ready_items.append(item)
        
        return ready_items
    
    def update_item_status(self, item_id: str, status: ChecklistStatus, 
                          notes: Optional[str] = None, execution_time: Optional[float] = None):
        """Update the status of a checklist item."""
        if item_id not in self.items:
            raise ValueError(f"Unknown checklist item: {item_id}")
        
        item = self.items[item_id]
        old_status = item.status
        item.status = status
        
        if notes:
            item.notes = notes
        if execution_time:
            item.execution_time = execution_time
        
        logging.info(f"Updated item {item_id}: {old_status} -> {status}")
    
    def mark_item_failed(self, item_id: str, failure_reason: str, can_retry: bool = True):
        """Mark an item as failed with reason."""
        if item_id not in self.items:
            raise ValueError(f"Unknown checklist item: {item_id}")
        
        item = self.items[item_id]
        item.failure_reasons.append(failure_reason)
        item.retry_count += 1
        
        if can_retry and item.can_retry():
            item.status = ChecklistStatus.PENDING
            logging.info(f"Item {item_id} failed but can retry ({item.retry_count}/{item.max_retries})")
        else:
            item.status = ChecklistStatus.FAILED
            logging.error(f"Item {item_id} failed permanently: {failure_reason}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary."""
        total_items = len(self.items)
        status_counts = {}
        
        for status in ChecklistStatus:
            status_counts[status.value] = sum(
                1 for item in self.items.values() if item.status == status
            )
        
        progress_percentage = (
            status_counts.get(ChecklistStatus.COMPLETED.value, 0) / total_items * 100
            if total_items > 0 else 0
        )
        
        return {
            "total_items": total_items,
            "status_counts": status_counts,
            "progress_percentage": progress_percentage,
            "categories": len(self.categories),
            "ready_items": len(self.get_ready_items())
        }
    
    def get_category_progress(self, category_id: str) -> Dict[str, Any]:
        """Get progress summary for a specific category."""
        if category_id not in self.categories:
            raise ValueError(f"Unknown category: {category_id}")
        
        category = self.categories[category_id]
        total_items = len(category.items)
        
        if total_items == 0:
            return {"category": category_id, "progress_percentage": 100, "items": []}
        
        status_counts = {}
        for status in ChecklistStatus:
            status_counts[status.value] = sum(
                1 for item in category.items if item.status == status
            )
        
        progress_percentage = (
            status_counts.get(ChecklistStatus.COMPLETED.value, 0) / total_items * 100
        )
        
        return {
            "category": category_id,
            "name": category.name,
            "total_items": total_items,
            "status_counts": status_counts,
            "progress_percentage": progress_percentage,
            "required": category.required
        }
    
    def export_checklist(self) -> Dict[str, Any]:
        """Export complete checklist state."""
        return {
            "session_id": self.session_id,
            "categories": {
                cat_id: {
                    "id": cat.id,
                    "name": cat.name,
                    "description": cat.description,
                    "required": cat.required,
                    "items": [item.to_dict() for item in cat.items]
                }
                for cat_id, cat in self.categories.items()
            },
            "execution_order": self.execution_order,
            "progress_summary": self.get_progress_summary()
        }
    
    def save_checklist(self, filepath: str):
        """Save checklist to file."""
        export_data = self.export_checklist()
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logging.info(f"Saved checklist to {filepath}")
    
    def load_checklist(self, filepath: str):
        """Load checklist from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.session_id = data["session_id"]
        self.execution_order = data["execution_order"]
        
        # Reconstruct categories and items
        self.categories = {}
        self.items = {}
        
        for cat_id, cat_data in data["categories"].items():
            category = ChecklistCategory(
                id=cat_data["id"],
                name=cat_data["name"],
                description=cat_data["description"],
                required=cat_data["required"]
            )
            
            category.items = []
            for item_data in cat_data["items"]:
                # Convert string enums back to enum types
                item_data["status"] = ChecklistStatus(item_data["status"])
                item_data["priority"] = ChecklistPriority(item_data["priority"])
                
                item = ChecklistItem.from_dict(item_data)
                category.items.append(item)
                self.items[item.id] = item
            
            self.categories[cat_id] = category
        
        logging.info(f"Loaded checklist from {filepath}")
    
    def validate_checklist_integrity(self) -> List[str]:
        """Validate checklist for issues like missing dependencies."""
        issues = []
        
        # Check for missing dependencies
        all_item_ids = set(self.items.keys())
        for item_id, item in self.items.items():
            for dep_id in item.dependencies:
                if dep_id not in all_item_ids:
                    issues.append(f"Item '{item_id}' has missing dependency: '{dep_id}'")
        
        # Check for circular dependencies
        try:
            self._calculate_execution_order()
        except ValueError as e:
            issues.append(f"Dependency error: {str(e)}")
        
        return issues