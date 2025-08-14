"""
bAIos data models package.

This package contains data models for the bAIos CLI tool,
including inventory items and system checks.
"""

from .inventory import InventoryItem, InventorySection, InventoryStatus

__all__ = ["InventoryItem", "InventorySection", "InventoryStatus"]