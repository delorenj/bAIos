#!/usr/bin/env python3
"""
bAIos inventory data models.

This module defines data structures for inventory items, sections,
and status tracking for the bAIos system requirements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from pathlib import Path
import json


class InventoryStatus(Enum):
    """Status enumeration for inventory items."""
    
    COMPLETE = "complete"
    FAILED_CRITICAL = "failed_critical"
    FAILED_NON_CRITICAL = "failed_non_critical"
    NOT_STARTED_REQUIRED = "not_started_required"
    NOTE = "note"
    
    def __str__(self) -> str:
        """Return human-readable status."""
        status_map = {
            self.COMPLETE: "✅ Complete",
            self.FAILED_CRITICAL: "❌ Failed (Critical)",
            self.FAILED_NON_CRITICAL: "⚠️ Failed (Non-Critical)",
            self.NOT_STARTED_REQUIRED: "🔴 Not Started (Required)",
            self.NOTE: "📝 Note"
        }
        return status_map.get(self, str(self.value))
    
    @property
    def emoji(self) -> str:
        """Return emoji representation."""
        emoji_map = {
            self.COMPLETE: "✅",
            self.FAILED_CRITICAL: "❌",
            self.FAILED_NON_CRITICAL: "⚠️",
            self.NOT_STARTED_REQUIRED: "🔴",
            self.NOTE: "📝"
        }
        return emoji_map.get(self, "❓")
    
    @property
    def color(self) -> str:
        """Return Rich color for display."""
        color_map = {
            self.COMPLETE: "green",
            self.FAILED_CRITICAL: "red",
            self.FAILED_NON_CRITICAL: "yellow",
            self.NOT_STARTED_REQUIRED: "bright_red",
            self.NOTE: "blue"
        }
        return color_map.get(self, "white")


@dataclass
class InventoryItem:
    """
    Represents a single inventory item with its requirements and status.
    """
    
    id: str
    description: str
    section: str
    category: str = ""
    status: InventoryStatus = InventoryStatus.NOT_STARTED_REQUIRED
    details: str = ""
    check_command: Optional[str] = None
    install_command: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            # Create ID from description
            self.id = self.description.lower().replace(" ", "_").replace("-", "_")[:50]
    
    @property
    def is_critical(self) -> bool:
        """Check if this item is critical (failure blocks system functionality)."""
        # Items that are typically critical
        critical_keywords = [
            "zsh", "shell", "git", "github", "ssh", "neovim", "python", 
            "nodejs", "docker", "claude-code", "authentication"
        ]
        return any(keyword in self.description.lower() for keyword in critical_keywords)
    
    @property
    def is_complete(self) -> bool:
        """Check if item is complete."""
        return self.status == InventoryStatus.COMPLETE
    
    @property
    def needs_attention(self) -> bool:
        """Check if item needs attention (failed or not started)."""
        return self.status in [
            InventoryStatus.FAILED_CRITICAL,
            InventoryStatus.FAILED_NON_CRITICAL,
            InventoryStatus.NOT_STARTED_REQUIRED
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "section": self.section,
            "category": self.category,
            "status": self.status.value,
            "details": self.details,
            "check_command": self.check_command,
            "install_command": self.install_command,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "is_critical": self.is_critical,
            "is_complete": self.is_complete,
            "needs_attention": self.needs_attention
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventoryItem":
        """Create instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            section=data.get("section", ""),
            category=data.get("category", ""),
            status=InventoryStatus(data.get("status", InventoryStatus.NOT_STARTED_REQUIRED.value)),
            details=data.get("details", ""),
            check_command=data.get("check_command"),
            install_command=data.get("install_command"),
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class InventorySection:
    """
    Represents a section of inventory items (e.g., WSL/Ubuntu, Windows).
    """
    
    name: str
    description: str = ""
    items: List[InventoryItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_item(self, item: InventoryItem):
        """Add an inventory item to this section."""
        item.section = self.name
        self.items.append(item)
    
    def get_item_by_id(self, item_id: str) -> Optional[InventoryItem]:
        """Get an item by its ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def get_items_by_status(self, status: InventoryStatus) -> List[InventoryItem]:
        """Get all items with a specific status."""
        return [item for item in self.items if item.status == status]
    
    def get_critical_items(self) -> List[InventoryItem]:
        """Get all critical items in this section."""
        return [item for item in self.items if item.is_critical]
    
    def get_incomplete_items(self) -> List[InventoryItem]:
        """Get all incomplete items."""
        return [item for item in self.items if item.needs_attention]
    
    @property
    def total_items(self) -> int:
        """Total number of items in section."""
        return len(self.items)
    
    @property
    def completed_items(self) -> int:
        """Number of completed items."""
        return len(self.get_items_by_status(InventoryStatus.COMPLETE))
    
    @property
    def failed_critical_items(self) -> int:
        """Number of critically failed items."""
        return len(self.get_items_by_status(InventoryStatus.FAILED_CRITICAL))
    
    @property
    def completion_percentage(self) -> float:
        """Completion percentage of this section."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def status_summary(self) -> Dict[str, int]:
        """Get summary of all statuses in this section."""
        summary = {}
        for status in InventoryStatus:
            summary[status.value] = len(self.get_items_by_status(status))
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "items": [item.to_dict() for item in self.items],
            "metadata": self.metadata,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_critical_items": self.failed_critical_items,
            "completion_percentage": self.completion_percentage,
            "status_summary": self.status_summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventorySection":
        """Create instance from dictionary."""
        section = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {})
        )
        
        for item_data in data.get("items", []):
            item = InventoryItem.from_dict(item_data)
            section.add_item(item)
        
        return section


@dataclass  
class InventoryReport:
    """
    Complete inventory report containing all sections and overall statistics.
    """
    
    sections: List[InventorySection] = field(default_factory=list)
    env_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: Optional[str] = None
    
    def add_section(self, section: InventorySection):
        """Add a section to the report."""
        self.sections.append(section)
    
    def get_section_by_name(self, name: str) -> Optional[InventorySection]:
        """Get a section by name."""
        for section in self.sections:
            if section.name.lower() == name.lower():
                return section
        return None
    
    def get_all_items(self) -> List[InventoryItem]:
        """Get all items across all sections."""
        items = []
        for section in self.sections:
            items.extend(section.items)
        return items
    
    def get_items_by_status(self, status: InventoryStatus) -> List[InventoryItem]:
        """Get all items with a specific status across all sections."""
        items = []
        for section in self.sections:
            items.extend(section.get_items_by_status(status))
        return items
    
    @property
    def total_items(self) -> int:
        """Total number of items across all sections."""
        return sum(section.total_items for section in self.sections)
    
    @property
    def completed_items(self) -> int:
        """Number of completed items across all sections."""
        return sum(section.completed_items for section in self.sections)
    
    @property
    def failed_critical_items(self) -> int:
        """Number of critically failed items across all sections."""
        return sum(section.failed_critical_items for section in self.sections)
    
    @property
    def overall_completion_percentage(self) -> float:
        """Overall completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @property
    def overall_status_summary(self) -> Dict[str, int]:
        """Get overall status summary across all sections."""
        summary = {}
        for status in InventoryStatus:
            summary[status.value] = len(self.get_items_by_status(status))
        return summary
    
    @property
    def critical_items_status(self) -> Dict[str, int]:
        """Status summary for only critical items."""
        critical_items = [item for item in self.get_all_items() if item.is_critical]
        summary = {}
        for status in InventoryStatus:
            summary[status.value] = len([item for item in critical_items if item.status == status])
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "sections": [section.to_dict() for section in self.sections],
            "env_keys": self.env_keys,
            "metadata": self.metadata,
            "generated_at": self.generated_at,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_critical_items": self.failed_critical_items,
            "overall_completion_percentage": self.overall_completion_percentage,
            "overall_status_summary": self.overall_status_summary,
            "critical_items_status": self.critical_items_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventoryReport":
        """Create instance from dictionary."""
        report = cls(
            env_keys=data.get("env_keys", []),
            metadata=data.get("metadata", {}),
            generated_at=data.get("generated_at")
        )
        
        for section_data in data.get("sections", []):
            section = InventorySection.from_dict(section_data)
            report.add_section(section)
        
        return report
    
    def save_to_file(self, file_path: Path):
        """Save report to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "InventoryReport":
        """Load report from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)