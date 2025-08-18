"""
bAIos Provisioning Agent

A simplified, monolithic agent for provisioning WSL environments.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProvisioningTask:
    """Represents a single provisioning task"""
    id: str
    description: str
    check_command: Optional[str] = None
    install_command: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ProvisioningAgent:
    """
    A simplified, monolithic agent for provisioning WSL environments.
    """

    def __init__(self, config_path: Optional[str] = None, dry_run: bool = False):
        """
        Initialize the Provisioning Agent.

        Args:
            config_path: Path to configuration file
            dry_run: If True, simulate operations without execution
        """
        self.config_path = config_path or Path(__file__).parent / "config.yaml"
        self.dry_run = dry_run
        self.tasks: Dict[str, ProvisioningTask] = {}
        self._initialize_tasks()

    def _initialize_tasks(self):
        """Initialize task definitions from a configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                for task_data in config.get('tasks', []):
                    # Filter out None values from task_data
                    filtered_task_data = {k: v for k, v in task_data.items() if v is not None}
                    task = ProvisioningTask(**filtered_task_data)
                    self.tasks[task.id] = task
        except FileNotFoundError:
            logger.error(f"Configuration file not found at: {self.config_path}")
            self.tasks = {}
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            self.tasks = {}

    def get_ready_tasks(self) -> List[str]:
        """
        Get list of tasks that are ready to execute (all dependencies completed).
        
        Returns:
            List of task IDs that can be executed
        """
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status != "pending":
                continue
                
            # Check if all dependencies are completed
            dependencies_met = all(
                self.tasks[dep].status == "completed"
                for dep in task.dependencies
                if dep in self.tasks
            )
            
            if dependencies_met:
                ready_tasks.append(task_id)
                
        return ready_tasks

    async def execute_task(self, task_id: str) -> bool:
        """
        Execute a specific task.
        
        Args:
            task_id: ID of the task to execute
            
        Returns:
            True if task completed successfully
        """
        task = self.tasks[task_id]
        
        logger.info(f"🚀 Starting task: {task.description}")
        
        task.status = "running"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Simulating execution of task: {task.description}")
            await asyncio.sleep(1)
            task.status = "completed"
            return True

        if task.check_command:
            process = await asyncio.create_subprocess_shell(
                task.check_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info(f"✅ Task '{task.description}' already completed.")
                task.status = "completed"
                return True

        if task.install_command:
            process = await asyncio.create_subprocess_shell(
                task.install_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info(f"✅ Task '{task.description}' completed successfully.")
                task.status = "completed"
                return True
            else:
                logger.error(f"❌ Task '{task.description}' failed.")
                task.status = "failed"
                task.error_message = stderr.decode()
                return False
        
        # If there is no check_command and no install_command, we assume the task is a meta-task that is completed by its dependencies.
        task.status = "completed"
        return True

    async def run(self, task_id: Optional[str] = None) -> bool:
        """
        Execute the complete provisioning workflow or a single task.

        Args:
            task_id: Optional ID of a single task to execute.

        Returns:
            True if all tasks completed successfully
        """
        logger.info("=" * 60)
        logger.info("bAIos Provisioning Agent - Starting")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info("=" * 60)

        if task_id:
            if task_id not in self.tasks:
                logger.error(f"Task '{task_id}' not found.")
                return False
            
            # Find dependencies
            tasks_to_run = [task_id]
            deps = self.tasks[task_id].dependencies
            while deps:
                dep_id = deps.pop(0)
                if dep_id not in tasks_to_run:
                    tasks_to_run.insert(0, dep_id)
                    new_deps = self.tasks[dep_id].dependencies
                    deps.extend(new_deps)

            for task_to_run in tasks_to_run:
                success = await self.execute_task(task_to_run)
                if not success:
                    return False
            return True

        completed_count = 0
        total_tasks = len(self.tasks)

        while completed_count < total_tasks:
            ready_tasks = self.get_ready_tasks()

            if not ready_tasks:
                pending_tasks = [t for t in self.tasks.values() if t.status == "pending"]
                if not pending_tasks:
                    break  # All tasks completed
                else:
                    logger.error("Dependency deadlock detected!")
                    return False
            
            results = await asyncio.gather(*[self.execute_task(task_id) for task_id in ready_tasks])

            if not all(results):
                logger.error("Workflow execution failed.")
                return False
            
            completed_count = len([t for t in self.tasks.values() if t.status == "completed"])

        logger.info("=" * 60)
        logger.info("bAIos Provisioning Agent - Finished")
        logger.info("=" * 60)

        return True

async def main():
    """
    Main entry point for the Provisioning Agent.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="bAIos Provisioning Agent - A simplified, monolithic agent for provisioning WSL environments."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without executing"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="ID of a single task to execute"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run agent
    agent = ProvisioningAgent(
        config_path=args.config,
        dry_run=args.dry_run
    )

    success = await agent.run(task_id=args.task)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

root_agent = ProvisioningAgent
