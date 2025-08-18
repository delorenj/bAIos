"""
End-to-End Integration Tests
============================

Comprehensive tests for the complete orchestrator system.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock
from ..orchestrator import RootOrchestrator, AgentFactory, TaskScheduler, FailureTracker
from ..orchestrator.checklist_manager import ChecklistManager, ChecklistStatus
from ..agents.stub_agent import StubAgentFactory
from ..schemas import ProvisioningRequest, ProvisioningResponse, TaskStatus


class TestEndToEndOrchestrator:
    """End-to-end tests for the complete orchestrator system."""
    
    @pytest.fixture
    def temp_spec_file(self):
        """Create a temporary environment specification file."""
        spec_content = """
# WSL Environment Specification

## System Requirements
- Ubuntu 22.04 with WSL 2
- Minimum 4GB RAM available
- At least 10GB free disk space

## Languages & Runtimes
- Python 3.12.9 (via mise)
- Node.js latest (via mise)

## Shell Configuration
- zsh as default shell
- oh-my-zsh with powerlevel10k theme
- Essential plugins: git, zsh-autosuggestions, zsh-syntax-highlighting

## Development Tools
- git with user configuration
- SSH key (ed25519) for authentication
- mise for version management
- Basic development tools (curl, wget, build-essential)

## Optional Components
- Docker Desktop WSL integration
- Neovim with basic configuration
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(spec_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def orchestrator_with_stubs(self):
        """Create orchestrator configured with stub agents for testing."""
        with patch('src.orchestrator.root_orchestrator.instructor'), \
             patch('src.orchestrator.root_orchestrator.OpenAI'), \
             patch('src.orchestrator.agent_factory.instructor'), \
             patch('src.orchestrator.agent_factory.OpenAI'):
            
            orchestrator = RootOrchestrator()
            
            # Replace real agent factory with stub factory for testing
            stub_factory = StubAgentFactory(default_success_rate=0.9)
            
            # Mock the agent factory to return stub agents
            orchestrator.agent_factory.create_agent = stub_factory.create_stub_agent
            
            return orchestrator, stub_factory
    
    @pytest.mark.asyncio
    async def test_full_provisioning_workflow_success(self, orchestrator_with_stubs, temp_spec_file):
        """Test complete successful provisioning workflow."""
        orchestrator, stub_factory = orchestrator_with_stubs
        
        # Create provisioning request
        request = ProvisioningRequest(
            environment_spec_path=temp_spec_file,
            user_preferences={"minimal_install": False, "parallel_execution": True},
            dry_run=True,
            force_reinstall=False
        )
        
        # Mock the execution methods to simulate successful execution
        with patch.object(orchestrator, '_create_execution_plan', new_callable=AsyncMock) as mock_plan, \
             patch.object(orchestrator, '_execute_phase', new_callable=AsyncMock) as mock_execute, \
             patch.object(orchestrator, '_perform_final_validation', new_callable=AsyncMock) as mock_qa:
            
            # Mock execution plan
            from ..schemas import ExecutionPlan, ProvisioningPhase
            mock_plan.return_value = ExecutionPlan(
                session_id=orchestrator.session_id,
                phases=[
                    ProvisioningPhase.INITIALIZATION,
                    ProvisioningPhase.SYSTEM_SETUP,
                    ProvisioningPhase.LANGUAGE_INSTALLATION,
                    ProvisioningPhase.SHELL_CONFIGURATION,
                    ProvisioningPhase.AUTHENTICATION_SETUP,
                    ProvisioningPhase.VALIDATION
                ],
                task_dependencies=[],
                estimated_duration=300.0,
                parallel_execution_groups=[],
                critical_path=[]
            )\n            \n            # Mock successful execution\n            mock_execute.return_value = True\n            \n            # Mock successful QA\n            from ..schemas import QAResult\n            mock_qa.return_value = QAResult(\n                task_id=\"final_validation\",\n                validation_passed=True,\n                success_criteria_met=[\"system_setup\", \"shell_config\", \"language_setup\"],\n                failures=[],\n                remediation_suggestions=[],\n                confidence_score=0.95\n            )\n            \n            # Execute provisioning\n            response = await orchestrator.provision_environment(request)\n            \n            # Verify response\n            assert isinstance(response, ProvisioningResponse)\n            assert response.status == TaskStatus.COMPLETED\n            assert response.session_id == orchestrator.session_id\n            assert response.progress_percentage == 100\n            assert len(response.completed_tasks) > 0\n            assert len(response.failed_tasks) == 0\n            assert response.human_interventions_required == 0\n    \n    @pytest.mark.asyncio\n    async def test_provisioning_with_failures_and_recovery(self, orchestrator_with_stubs, temp_spec_file):\n        \"\"\"Test provisioning workflow with failures and recovery.\"\"\"\n        orchestrator, stub_factory = orchestrator_with_stubs\n        \n        # Create some failure-prone agents\n        stub_factory.create_failure_prone_agent(\"installer\", failure_rate=0.6)\n        stub_factory.create_failure_prone_agent(\"shell_master\", failure_rate=0.4)\n        \n        request = ProvisioningRequest(\n            environment_spec_path=temp_spec_file,\n            user_preferences={\"minimal_install\": True},\n            dry_run=True\n        )\n        \n        with patch.object(orchestrator, '_create_execution_plan', new_callable=AsyncMock) as mock_plan, \\\n             patch.object(orchestrator, '_execute_phase', new_callable=AsyncMock) as mock_execute, \\\n             patch.object(orchestrator, '_perform_final_validation', new_callable=AsyncMock) as mock_qa:\n            \n            # Mock execution plan\n            from ..schemas import ExecutionPlan, ProvisioningPhase\n            mock_plan.return_value = ExecutionPlan(\n                session_id=orchestrator.session_id,\n                phases=[ProvisioningPhase.INITIALIZATION, ProvisioningPhase.VALIDATION],\n                task_dependencies=[],\n                estimated_duration=120.0,\n                parallel_execution_groups=[],\n                critical_path=[]\n            )\n            \n            # Simulate some failures\n            mock_execute.side_effect = [True, False, True]  # Mixed success/failure\n            \n            # Mock QA with some issues\n            from ..schemas import QAResult\n            mock_qa.return_value = QAResult(\n                task_id=\"final_validation\",\n                validation_passed=False,\n                success_criteria_met=[\"system_setup\"],\n                failures=[\"shell_config: zsh not set as default\"],\n                remediation_suggestions=[\"Run: chsh -s $(which zsh)\"],\n                confidence_score=0.65\n            )\n            \n            # Execute provisioning\n            response = await orchestrator.provision_environment(request)\n            \n            # Verify response shows issues\n            assert isinstance(response, ProvisioningResponse)\n            assert response.status in [TaskStatus.PARTIALLY_COMPLETED, TaskStatus.FAILED]\n            assert len(response.failed_tasks) > 0 or response.progress_percentage < 100\n    \n    @pytest.mark.asyncio\n    async def test_human_intervention_workflow(self, orchestrator_with_stubs, temp_spec_file):\n        \"\"\"Test human intervention workflow when failures exceed threshold.\"\"\"\n        orchestrator, stub_factory = orchestrator_with_stubs\n        \n        # Create agents that always fail\n        for agent_type in [\"installer\", \"shell_master\", \"mise_master\"]:\n            stub_factory.create_failure_prone_agent(agent_type, failure_rate=1.0)\n        \n        request = ProvisioningRequest(\n            environment_spec_path=temp_spec_file,\n            user_preferences={},\n            dry_run=True\n        )\n        \n        # Mock consistent failures\n        with patch.object(orchestrator, '_create_execution_plan', new_callable=AsyncMock) as mock_plan, \\\n             patch.object(orchestrator, '_execute_phase', new_callable=AsyncMock) as mock_execute, \\\n             patch.object(orchestrator, '_request_human_intervention', new_callable=AsyncMock) as mock_human:\n            \n            # Mock execution plan\n            from ..schemas import ExecutionPlan, ProvisioningPhase\n            mock_plan.return_value = ExecutionPlan(\n                session_id=orchestrator.session_id,\n                phases=[ProvisioningPhase.SYSTEM_SETUP],\n                task_dependencies=[],\n                estimated_duration=60.0,\n                parallel_execution_groups=[],\n                critical_path=[]\n            )\n            \n            # Simulate repeated failures that should trigger human intervention\n            mock_execute.return_value = False\n            mock_human.return_value = {\"action\": \"manual_fix\", \"notes\": \"User intervention required\"}\n            \n            # Execute provisioning\n            response = await orchestrator.provision_environment(request)\n            \n            # Verify human intervention was requested\n            assert mock_human.called\n            assert response.human_interventions_required > 0\n    \n    def test_checklist_management_integration(self):\n        \"\"\"Test integration between orchestrator and checklist manager.\"\"\"\n        checklist_manager = ChecklistManager(\"test_session\")\n        \n        # Verify default checklist is loaded\n        assert len(checklist_manager.categories) > 0\n        assert len(checklist_manager.items) > 0\n        \n        # Test getting ready items\n        ready_items = checklist_manager.get_ready_items()\n        assert len(ready_items) > 0\n        \n        # Test updating item status\n        first_item = ready_items[0]\n        checklist_manager.update_item_status(\n            first_item.id, \n            ChecklistStatus.COMPLETED,\n            \"Test completion\"\n        )\n        \n        # Verify status change\n        assert checklist_manager.items[first_item.id].status == ChecklistStatus.COMPLETED\n        \n        # Test progress summary\n        progress = checklist_manager.get_progress_summary()\n        assert \"total_items\" in progress\n        assert \"progress_percentage\" in progress\n        assert progress[\"progress_percentage\"] > 0\n    \n    def test_failure_tracking_integration(self):\n        \"\"\"Test integration between orchestrator and failure tracker.\"\"\"\n        failure_tracker = FailureTracker(failure_threshold=3)\n        \n        # Simulate multiple failures\n        task_id = \"test_task\"\n        agent_type = \"installer\"\n        \n        for i in range(4):\n            count = failure_tracker.record_failure(task_id, agent_type, f\"Error {i}\")\n        \n        # Verify failure tracking\n        assert failure_tracker.total_failures == 4\n        assert task_id in failure_tracker.task_failures\n        \n        # Verify human intervention is required\n        task_failure = failure_tracker.task_failures[task_id]\n        assert task_failure.requires_human_intervention\n        \n        # Get failure report\n        report = failure_tracker.get_failure_report(task_id)\n        assert report is not None\n        assert report.failure_count == 4\n        assert len(report.failure_reasons) == 4\n    \n    @pytest.mark.asyncio\n    async def test_agent_factory_integration(self):\n        \"\"\"Test agent factory integration with different agent types.\"\"\"\n        with patch('src.orchestrator.agent_factory.instructor'), \\\n             patch('src.orchestrator.agent_factory.OpenAI'):\n            \n            factory = AgentFactory()\n            \n            # Test creating different agent types\n            agent_types = [\"researcher\", \"installer\", \"shell_master\", \"qa_expert\"]\n            \n            for agent_type in agent_types:\n                agent = factory.create_agent(agent_type)\n                assert agent is not None\n                \n                # Test agent caching\n                agent2 = factory.create_agent(agent_type)\n                assert agent is agent2\n            \n            # Test agent status\n            for agent_type in agent_types:\n                status = factory.get_agent_status(agent_type)\n                assert status[\"type\"] == agent_type\n                assert \"status\" in status\n    \n    @pytest.mark.asyncio\n    async def test_task_scheduler_integration(self):\n        \"\"\"Test task scheduler integration with complex dependencies.\"\"\"\n        scheduler = TaskScheduler()\n        \n        # Create tasks with dependencies\n        from ..schemas import AgentRequest\n        \n        # Base task (no dependencies)\n        base_request = AgentRequest(\n            agent_type=\"researcher\",\n            task_description=\"Analyze environment\",\n            context={}\n        )\n        base_request.task_id = \"base_task\"\n        base_id = scheduler.schedule_task(base_request)\n        \n        # Dependent task\n        dep_request = AgentRequest(\n            agent_type=\"installer\",\n            task_description=\"Install packages\",\n            context={}\n        )\n        dep_request.task_id = \"dep_task\"\n        dep_id = scheduler.schedule_task(dep_request, dependencies=[base_id])\n        \n        # Verify task scheduling\n        assert base_id in scheduler.tasks\n        assert dep_id in scheduler.tasks\n        assert base_id in scheduler.dependency_graph[dep_id]\n        \n        # Test ready tasks (only base should be ready initially)\n        ready_tasks = scheduler.get_ready_tasks()\n        assert base_id in ready_tasks\n        assert dep_id not in ready_tasks\n        \n        # Complete base task\n        scheduler.mark_task_running(base_id)\n        from ..schemas import TaskResponse\n        response = TaskResponse(\n            task_id=base_id,\n            status=TaskStatus.COMPLETED,\n            duration=1.0\n        )\n        scheduler.complete_task(base_id, response)\n        \n        # Now dependent task should be ready\n        ready_tasks = scheduler.get_ready_tasks()\n        assert dep_id in ready_tasks\n    \n    def test_checklist_export_import(self):\n        \"\"\"Test checklist export and import functionality.\"\"\"\n        original_manager = ChecklistManager(\"export_test\")\n        \n        # Modify some items\n        ready_items = original_manager.get_ready_items()\n        if ready_items:\n            original_manager.update_item_status(\n                ready_items[0].id,\n                ChecklistStatus.COMPLETED\n            )\n        \n        # Export to temporary file\n        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:\n            temp_path = f.name\n        \n        try:\n            original_manager.save_checklist(temp_path)\n            \n            # Create new manager and import\n            new_manager = ChecklistManager(\"import_test\")\n            new_manager.load_checklist(temp_path)\n            \n            # Verify data integrity\n            assert new_manager.session_id == \"export_test\"\n            assert len(new_manager.categories) == len(original_manager.categories)\n            assert len(new_manager.items) == len(original_manager.items)\n            assert new_manager.execution_order == original_manager.execution_order\n            \n        finally:\n            if os.path.exists(temp_path):\n                os.unlink(temp_path)\n    \n    def test_system_status_monitoring(self, orchestrator_with_stubs):\n        \"\"\"Test system status and monitoring capabilities.\"\"\"\n        orchestrator, _ = orchestrator_with_stubs\n        \n        # Get orchestrator status\n        status = orchestrator.get_orchestration_status()\n        \n        assert status.orchestrator_id is not None\n        assert isinstance(status.active_sessions, list)\n        assert isinstance(status.agent_status, dict)\n        assert isinstance(status.system_health, dict)\n        assert status.uptime >= 0\n        \n        # Verify system health indicators\n        health = status.system_health\n        assert \"memory_usage\" in health\n        assert \"active_tasks\" in health\n        assert \"error_rate\" in health\n\n\nif __name__ == \"__main__\":\n    pytest.main([__file__, \"-v\"])