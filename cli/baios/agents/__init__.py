#!/usr/bin/env python3
"""
bAIos CLI agents module.

This module provides the base Agent class and specialized agent implementations
for different domains of expertise.
"""

from .base import Agent
from .bill_coordinator import BillTheCoordinator
from .mise_master import MiseMaster
from .tzvi_windows import TzviTheWindowsWizard
from .shelldon import Shelldon

__all__ = [
    "Agent",
    "BillTheCoordinator", 
    "MiseMaster",
    "TzviTheWindowsWizard",
    "Shelldon"
]