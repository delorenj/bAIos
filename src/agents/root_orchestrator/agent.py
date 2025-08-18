"""Root Orchestrator Agent for WSL Environment Provisioning."""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
import markdown
import re
from pathlib import Path

from atomic_agents.lib.base.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from pydantic import Field

from .config import RootOrchestratorConfig
from .schema import (
    ProvisioningSpec,
    ChecklistItem,
    ChecklistStatus,
    AgentResponse,
    QAResult,
    SystemState,
    HumanEscalation,
)


class RootOrchestratorInputSchema(BaseIOSchema):
    """Input schema for Root Orchestrator Agent."""
    
    spec_file_path: str = Field(
        ..., 
        description="Path to the WSL environment specification markdown file"
    )
    
    action: str = Field(
        default="provision",
        description="Action to perform: 'provision', 'status', 'retry'"
    )


class RootOrchestratorOutputSchema(BaseIOSchema):
    """Output schema for Root Orchestrator Agent."""
    
    status: str = Field(..., description="Overall orchestration status")
    checklist_status: ChecklistStatus = Field(..., description="Current checklist status")
    active_agents: List[str] = Field(default=[], description="Currently active agents")
    completed_items: List[str] = Field(default=[], description="Completed checklist items")
    failed_items: List[str] = Field(default=[], description="Failed checklist items")
    human_escalations: List[HumanEscalation] = Field(default=[], description="Items requiring human intervention")
    message: str = Field(..., description="Status message for the user")


class RootOrchestratorAgent(BaseAgent):
    """Root orchestrator agent for WSL environment provisioning.
    
    This agent processes provisioning specifications, creates checklists,
    spawns specialized agents, coordinates their work, and handles QA verification.
    """

    def __init__(self, config: RootOrchestratorConfig):
        super().__init__(config)
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Internal state
        self.current_spec: Optional[ProvisioningSpec] = None
        self.checklist: List[ChecklistItem] = []
        self.system_state: SystemState = SystemState()
        self.active_agents: Dict[str, str] = {}  # agent_id -> item_id
        self.qa_history: Dict[str, List[QAResult]] = {}  # item_id -> qa_results
        self.human_escalations: List[HumanEscalation] = []
        
        self.logger.info("Root Orchestrator Agent initialized")

    def _parse_spec_file(self, file_path: str) -> ProvisioningSpec:
        """Parse WSL environment specification from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first heading
            title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "WSL Environment Spec"
            
            # Extract overview from content between title and first checklist
            overview_match = re.search(r'^#\s+(.+?)(?=^##|\n-\s+\[)', content, re.DOTALL | re.MULTILINE)
            overview = overview_match.group(1).strip() if overview_match else ""
            
            # Extract checklist items
            checklist_items = self._extract_checklist_items(content)
            
            # Extract environment variables
            env_vars = self._extract_environment_variables(content)
            
            return ProvisioningSpec(
                title=title,
                overview=overview,
                checklist_items=checklist_items,
                environment_variables=env_vars
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse spec file {file_path}: {e}")
            raise

    def _extract_checklist_items(self, content: str) -> List[ChecklistItem]:
        """Extract checklist items from markdown content."""
        items = []
        
        # Find all checkbox items with pattern: - [ ] description
        checkbox_pattern = r'^-\s+\[\s*\]\s+(.+?)(?:\n|$)'
        matches = re.findall(checkbox_pattern, content, re.MULTILINE)
        
        for i, match in enumerate(matches):
            item_text = match.strip()
            
            # Extract commands from description (look for backticks)
            commands = []
            cmd_pattern = r'`([^`]+)`'
            cmd_matches = re.findall(cmd_pattern, item_text)
            commands.extend(cmd_matches)
            
            # Determine agent type based on content
            agent_type = self._determine_agent_type(item_text)
            
            item = ChecklistItem(
                id=f"item_{i+1:03d}",
                title=item_text.split(':')[0].strip() if ':' in item_text else item_text,
                description=item_text,
                commands=commands,
                assigned_agent=agent_type
            )
            items.append(item)
        
        return items

    def _determine_agent_type(self, description: str) -> str:
        """Determine which agent should handle this checklist item."""
        desc_lower = description.lower()
        
        if any(keyword in desc_lower for keyword in ['install', 'apt', 'npm', 'pip', 'curl']):
            return "installer"
        elif any(keyword in desc_lower for keyword in ['shell', 'zsh', 'bash', 'path', 'alias']):
            return "shell_master"
        elif any(keyword in desc_lower for keyword in ['mise', 'python', 'node', 'version']):
            return "mise_master"
        elif any(keyword in desc_lower for keyword in ['auth', 'key', 'token', 'login', 'ssh']):
            return "authorizer"
        elif any(keyword in desc_lower for keyword in ['verify', 'test', 'check']):
            return "qa_expert"
        else:
            return "researcher"

    def _extract_environment_variables(self, content: str) -> Dict[str, str]:
        """Extract required environment variables from spec."""
        env_vars = {}
        
        # Look for environment variables section
        env_section_match = re.search(r'## Environment Variables\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if env_section_match:
            env_content = env_section_match.group(1)
            
            # Extract variables mentioned in the content
            var_pattern = r'([A-Z_]+)\s+configured'
            matches = re.findall(var_pattern, env_content)
            
            for var in matches:
                env_vars[var] = ""  # Will be filled by system state check
        
        return env_vars

    async def _spawn_agent(self, agent_type: str, item: ChecklistItem) -> str:
        """Spawn a specialized agent to handle a checklist item."""
        agent_id = f"{agent_type}_{item.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Spawning {agent_type} agent {agent_id} for item {item.id}")
        
        # In a real implementation, this would spawn actual agent processes
        # For now, we simulate the spawning
        self.active_agents[agent_id] = item.id
        
        # Update item status
        item.status = "in_progress"
        item.updated_at = datetime.now()
        
        return agent_id

    async def _check_system_state(self) -> SystemState:
        """Check current system state to sync with checklist."""
        # This would implement actual system state checking
        # For now, return a mock state
        return SystemState(
            installed_packages=["curl", "wget", "git"],
            configured_tools=["git"],
            environment_vars={
                "OPENROUTER_API_KEY": "configured",
                "PATH": "/usr/local/bin:/usr/bin:/bin"
            },
            shell_config={"zsh": "not_configured"}
        )

    async def _run_qa_verification(self, item: ChecklistItem, agent_response: AgentResponse) -> QAResult:
        """Run QA verification for a completed item."""
        # This would implement actual QA verification
        # For now, simulate QA with some logic
        
        # Simple heuristic: fail randomly to test the workflow
        import random
        if random.random() < 0.3:  # 30% failure rate for testing
            return QAResult(
                item_id=item.id,
                result="FAIL",
                reason="Simulated failure for testing workflow",
                verification_steps=["Checked installation", "Verified configuration"]
            )
        else:
            return QAResult(
                item_id=item.id,
                result="SUCCESS",
                reason="All verification steps passed",
                verification_steps=["Checked installation", "Verified configuration", "Tested functionality"]
            )

    async def _handle_qa_failure(self, item: ChecklistItem, qa_result: QAResult):
        """Handle QA failure for an item."""
        item.failure_count += 1
        item.failure_reasons.append(qa_result.reason)
        
        if item.id not in self.qa_history:
            self.qa_history[item.id] = []
        self.qa_history[item.id].append(qa_result)
        
        if item.failure_count >= self.config.max_failure_retries:
            # Escalate to human
            escalation = HumanEscalation(
                item_id=item.id,
                failure_count=item.failure_count,
                failure_history=self.qa_history[item.id],
                suggested_actions=[
                    "Manually verify the installation steps",
                    "Check for system-specific issues",
                    "Review error logs for detailed information"
                ]
            )
            self.human_escalations.append(escalation)
            item.status = "failed"
            
            self.logger.warning(f"Item {item.id} escalated to human after {item.failure_count} failures")
        else:
            # Retry the item
            item.status = "pending"
            self.logger.info(f"Item {item.id} will be retried (attempt {item.failure_count + 1})")

    def _calculate_checklist_status(self) -> ChecklistStatus:
        """Calculate current checklist status."""
        total = len(self.checklist)
        completed = sum(1 for item in self.checklist if item.status == "completed")
        pending = sum(1 for item in self.checklist if item.status == "pending")
        in_progress = sum(1 for item in self.checklist if item.status == "in_progress")
        failed = sum(1 for item in self.checklist if item.status == "failed")
        
        progress = (completed / total * 100) if total > 0 else 0
        
        return ChecklistStatus(
            total_items=total,
            completed=completed,
            pending=pending,
            in_progress=in_progress,
            failed=failed,
            progress_percentage=progress
        )

    async def run(self, input_data: RootOrchestratorInputSchema) -> RootOrchestratorOutputSchema:
        """Main orchestration workflow."""
        
        if input_data.action == "provision":
            # Parse specification and create checklist
            self.current_spec = self._parse_spec_file(input_data.spec_file_path)
            self.checklist = self.current_spec.checklist_items
            
            self.logger.info(f"Loaded specification with {len(self.checklist)} items")
            
            # Check current system state
            self.system_state = await self._check_system_state()
            
            # Sync checklist with system state
            await self._sync_checklist_with_system_state()
            
            # Start processing items
            await self._process_checklist()
        
        elif input_data.action == "status":
            # Return current status without processing
            pass
        
        elif input_data.action == "retry":
            # Retry failed items
            await self._retry_failed_items()
        
        # Calculate final status
        checklist_status = self._calculate_checklist_status()
        
        return RootOrchestratorOutputSchema(
            status="completed" if checklist_status.completed == checklist_status.total_items else "in_progress",
            checklist_status=checklist_status,
            active_agents=list(self.active_agents.keys()),
            completed_items=[item.id for item in self.checklist if item.status == "completed"],
            failed_items=[item.id for item in self.checklist if item.status == "failed"],
            human_escalations=self.human_escalations,
            message=f"Processed {checklist_status.completed}/{checklist_status.total_items} items successfully"
        )

    async def _sync_checklist_with_system_state(self):
        """Sync checklist items with current system state."""
        # This would check which items are already completed
        # For now, just log that we're syncing
        self.logger.info("Syncing checklist with current system state")
        
        # Mark some items as completed based on system state
        for item in self.checklist:
            if "git" in item.description.lower() and "git" in self.system_state.configured_tools:
                item.status = "completed"
                item.updated_at = datetime.now()

    async def _process_checklist(self):
        """Process all pending checklist items."""
        pending_items = [item for item in self.checklist if item.status == "pending"]
        
        # Process items in parallel (up to max_parallel_agents)
        semaphore = asyncio.Semaphore(self.config.max_parallel_agents)
        
        async def process_item(item: ChecklistItem):
            async with semaphore:
                await self._process_single_item(item)
        
        tasks = [process_item(item) for item in pending_items]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_single_item(self, item: ChecklistItem):
        """Process a single checklist item."""
        try:
            # Spawn appropriate agent
            agent_id = await self._spawn_agent(item.assigned_agent, item)
            
            # Simulate agent work (in real implementation, this would coordinate with actual agents)
            await asyncio.sleep(2)  # Simulate work
            
            # Simulate agent response
            agent_response = AgentResponse(
                agent_type=item.assigned_agent,
                agent_id=agent_id,
                item_id=item.id,
                status="completed",
                output=f"Successfully processed {item.title}",
                commands_executed=item.commands
            )
            
            # Run QA verification if enabled
            if self.config.qa_verification_required:
                qa_result = await self._run_qa_verification(item, agent_response)
                
                if qa_result.result == "SUCCESS":
                    item.status = "completed"
                    item.updated_at = datetime.now()
                    self.logger.info(f"Item {item.id} completed successfully")
                else:
                    await self._handle_qa_failure(item, qa_result)
            else:
                item.status = "completed"
                item.updated_at = datetime.now()
            
            # Clean up agent
            if agent_id in self.active_agents:
                del self.active_agents[agent_id]
                
        except Exception as e:
            self.logger.error(f"Failed to process item {item.id}: {e}")
            item.status = "failed"
            item.failure_count += 1
            item.failure_reasons.append(str(e))

    async def _retry_failed_items(self):
        """Retry items that have failed but haven't reached max retries."""
        failed_items = [
            item for item in self.checklist 
            if item.status == "pending" and item.failure_count > 0 and item.failure_count < self.config.max_failure_retries
        ]
        
        if failed_items:
            self.logger.info(f"Retrying {len(failed_items)} failed items")
            await self._process_checklist()