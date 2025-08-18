"""
bAIos Root Agent

An intelligent root agent that delegates tasks to specialized sub-agents.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RootAgent:
    """
    The Root Agent for the bAIos provisioning system.
    """

    def __init__(self, dry_run: bool = False):
        """
        Initialize the Root Agent.

        Args:
            dry_run: If True, simulate operations without execution
        """
        self.dry_run = dry_run
        self.sub_agents: Dict[str, Any] = {
            "system_setup": None,
            "shell": None,
            "dev_tools": None,
            "ai": None,
        }
        self._initialize_sub_agents()

    def _initialize_sub_agents(self):
        """Initialize sub-agent definitions"""
        from agents.system_setup_agent.agent import ProvisioningAgent as SystemSetupAgent
        from agents.shell_agent.agent import ProvisioningAgent as ShellAgent
        from agents.dev_tools_agent.agent import ProvisioningAgent as DevToolsAgent
        from agents.ai_agent.agent import ProvisioningAgent as AIAgent

        self.sub_agents["system_setup"] = SystemSetupAgent(dry_run=self.dry_run)
        self.sub_agents["shell"] = ShellAgent(dry_run=self.dry_run)
        self.sub_agents["dev_tools"] = DevToolsAgent(dry_run=self.dry_run)
        self.sub_agents["ai"] = AIAgent(dry_run=self.dry_run)

    def _get_agent_for_task(self, task_id: str) -> Optional[Any]:
        """Get the appropriate agent for a given task"""
        for agent in self.sub_agents.values():
            if task_id in agent.tasks:
                return agent
        return None

    async def run(self, query: str) -> bool:
        """
        Execute a task based on a natural language query.

        Args:
            query: The natural language query describing the task to execute.

        Returns:
            True if the task completed successfully
        """
        logger.info(f"Received query: {query}")

        # Simple keyword-based routing
        task_id = None
        if "python" in query:
            task_id = "python_install"
        elif "node" in query:
            task_id = "nodejs_install"
        elif "git" in query:
            task_id = "git_install"
        elif "zsh" in query:
            task_id = "zsh_install"
        elif "wsl" in query:
            task_id = "wsl_setup"
        elif "ubuntu" in query:
            task_id = "ubuntu_setup"
        elif "claude" in query:
            task_id = "claude_code_install"
        elif "gptme" in query:
            task_id = "gptme_install"
        else:
            logger.error(f"Could not determine task from query: {query}")
            return False

        agent = self._get_agent_for_task(task_id)
        if not agent:
            logger.error(f"Could not find agent for task: {task_id}")
            return False

        return await agent.run(task_id=task_id)

async def main():
    """
    Main entry point for the Root Agent.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="bAIos Root Agent - An intelligent root agent that delegates tasks to specialized sub-agents."
    )
    parser.add_argument(
        "query",
        type=str,
        help="The natural language query describing the task to execute."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without executing"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run agent
    agent = RootAgent(
        dry_run=args.dry_run
    )

    success = await agent.run(query=args.query)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

root_agent = RootAgent
