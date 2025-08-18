"""
Test Suite for Root Orchestrator
================================

Unit tests for the root orchestrator functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from ..orchestrator import RootOrchestrator, AgentFactory, TaskScheduler, FailureTracker
from ..schemas import ProvisioningRequest, ProvisioningResponse, AgentRequest, AgentResponse, TaskStatus


class TestRootOrchestrator:
    """Test cases for the Root Orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a test orchestrator instance."""
        with patch('src.orchestrator.root_orchestrator.instructor'), \
             patch('src.orchestrator.root_orchestrator.OpenAI'):
            return RootOrchestrator()
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample provisioning request."""
        return ProvisioningRequest(
            environment_spec_path="/test/spec.md",
            user_preferences={"minimal_install": True},
            dry_run=True
        )
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'agent_factory')
        assert hasattr(orchestrator, 'task_scheduler')
        assert hasattr(orchestrator, 'failure_tracker')
        assert orchestrator.session_id is not None
    
    @pytest.mark.asyncio 
    async def test_provision_environment_dry_run(self, orchestrator, sample_request):
        """Test dry run provisioning."""
        with patch.object(orchestrator, '_read_environment_spec', return_value="test spec"), \
             patch.object(orchestrator, '_execute_phase', new_callable=AsyncMock), \
             patch.object(orchestrator, '_create_execution_plan', new_callable=AsyncMock) as mock_plan, \
             patch.object(orchestrator, '_perform_final_validation', new_callable=AsyncMock) as mock_qa:
            
            # Mock execution plan
            from ..schemas import ExecutionPlan, ProvisioningPhase
            mock_plan.return_value = ExecutionPlan(
                session_id="test",
                phases=[ProvisioningPhase.INITIALIZATION, ProvisioningPhase.VALIDATION],
                task_dependencies=[],
                estimated_duration=60.0,
                parallel_execution_groups=[],
                critical_path=[]
            )
            
            # Mock QA result
            from ..schemas import QAResult
            mock_qa.return_value = QAResult(
                task_id="final_validation",
                validation_passed=True,
                success_criteria_met=["test_criteria"],
                failures=[],
                remediation_suggestions=[],
                confidence_score=0.9
            )
            
            response = await orchestrator.provision_environment(sample_request)
            
            assert isinstance(response, ProvisioningResponse)
            assert response.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            assert response.session_id is not None
            assert response.progress_percentage >= 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_status(self, orchestrator):
        """Test getting orchestrator status."""
        status = orchestrator.get_orchestration_status()
        
        assert status.orchestrator_id is not None
        assert isinstance(status.active_sessions, list)
        assert isinstance(status.agent_status, dict)
        assert isinstance(status.system_health, dict)
        assert status.uptime >= 0


class TestAgentFactory:
    """Test cases for the Agent Factory."""
    
    @pytest.fixture
    def factory(self):
        """Create a test agent factory."""
        return AgentFactory()
    
    def test_factory_initialization(self, factory):
        """Test factory initialization."""
        assert factory is not None
        assert len(factory.agent_classes) == 7  # 7 specialized agents
        assert "researcher" in factory.agent_classes
        assert "installer" in factory.agent_classes
        assert "qa_expert" in factory.agent_classes
    
    def test_create_agent_valid_type(self, factory):
        """Test creating a valid agent type."""
        with patch('src.orchestrator.agent_factory.instructor'), \
             patch('src.orchestrator.agent_factory.OpenAI'):
            agent = factory.create_agent("researcher")
            assert agent is not None
    
    def test_create_agent_invalid_type(self, factory):
        """Test creating an invalid agent type."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            factory.create_agent("invalid_agent")
    
    def test_agent_caching(self, factory):
        """Test that agents are cached properly."""
        with patch('src.orchestrator.agent_factory.instructor'), \
             patch('src.orchestrator.agent_factory.OpenAI'):
            agent1 = factory.create_agent("researcher")
            agent2 = factory.create_agent("researcher")
            assert agent1 is agent2  # Should be the same cached instance
    
    def test_get_agent_status(self, factory):
        """Test getting agent status."""
        status = factory.get_agent_status("researcher")
        assert status["type"] == "researcher"
        assert "status" in status
        assert "cached" in status


class TestTaskScheduler:
    """Test cases for the Task Scheduler."""
    
    @pytest.fixture
    def scheduler(self):
        """Create a test task scheduler."""
        return TaskScheduler()
    
    @pytest.fixture
    def sample_task_request(self):
        """Create a sample task request."""
        return AgentRequest(
            agent_type="researcher",
            task_description="Test task",
            context={"test": True}
        )
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization."""
        assert scheduler is not None
        assert len(scheduler.tasks) == 0
        assert len(scheduler.dependency_graph) == 0
        assert len(scheduler.running_tasks) == 0
    
    def test_schedule_task(self, scheduler, sample_task_request):
        """Test scheduling a task."""
        sample_task_request.task_id = "test_task_1"
        task_id = scheduler.schedule_task(sample_task_request)
        
        assert task_id == "test_task_1"
        assert task_id in scheduler.tasks
        assert task_id in scheduler.dependency_graph
    
    def test_schedule_task_with_dependencies(self, scheduler, sample_task_request):
        """Test scheduling a task with dependencies."""
        # First schedule a dependency
        sample_task_request.task_id = "dependency_task"
        dep_id = scheduler.schedule_task(sample_task_request)
        
        # Then schedule a task that depends on it
        dependent_request = AgentRequest(
            agent_type="installer",
            task_description="Dependent task",
            context={"test": True}
        )
        dependent_request.task_id = "dependent_task"
        
        task_id = scheduler.schedule_task(dependent_request, dependencies=[dep_id])
        
        assert task_id in scheduler.tasks
        assert dep_id in scheduler.dependency_graph[task_id]
    
    def test_get_ready_tasks(self, scheduler, sample_task_request):
        """Test getting ready tasks."""
        sample_task_request.task_id = "ready_task"
        scheduler.schedule_task(sample_task_request)
        
        ready_tasks = scheduler.get_ready_tasks()
        assert "ready_task" in ready_tasks
    
    def test_task_lifecycle(self, scheduler, sample_task_request):
        """Test complete task lifecycle."""
        sample_task_request.task_id = "lifecycle_task"
        task_id = scheduler.schedule_task(sample_task_request)
        
        # Mark as running
        scheduler.mark_task_running(task_id)
        assert task_id in scheduler.running_tasks
        
        # Complete the task
        from ..schemas import TaskResponse
        response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            duration=1.0
        )
        scheduler.complete_task(task_id, response)
        
        assert task_id in scheduler.completed_tasks
        assert task_id not in scheduler.running_tasks
    
    def test_get_execution_summary(self, scheduler, sample_task_request):
        """Test getting execution summary."""
        sample_task_request.task_id = "summary_task"
        scheduler.schedule_task(sample_task_request)
        
        summary = scheduler.get_execution_summary()
        
        assert "total_tasks" in summary
        assert "pending_tasks" in summary
        assert "progress_percentage" in summary
        assert summary["total_tasks"] == 1


class TestFailureTracker:
    """Test cases for the Failure Tracker."""
    
    @pytest.fixture
    def tracker(self):
        """Create a test failure tracker."""
        return FailureTracker(failure_threshold=3)
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initialization."""
        assert tracker is not None
        assert tracker.failure_threshold == 3
        assert tracker.total_failures == 0
        assert len(tracker.task_failures) == 0
    
    def test_record_failure(self, tracker):
        """Test recording a failure."""
        failure_count = tracker.record_failure("test_task", "researcher", "Test error")
        
        assert failure_count == 1
        assert "test_task" in tracker.task_failures
        assert tracker.total_failures == 1
    
    def test_multiple_failures_same_task(self, tracker):
        """Test recording multiple failures for the same task."""
        task_id = "failing_task"
        
        # Record multiple failures
        for i in range(4):
            count = tracker.record_failure(task_id, "installer", f"Error {i}")
        
        assert count == 4
        assert tracker.task_failures[task_id].requires_human_intervention
        assert tracker.intervention_requests > 0
    
    def test_get_failure_report(self, tracker):
        """Test getting failure report."""
        task_id = "report_task"
        tracker.record_failure(task_id, "researcher", "Test error")
        
        report = tracker.get_failure_report(task_id)
        
        assert report is not None
        assert report.task_id == task_id
        assert report.failure_count == 1
        assert len(report.failure_reasons) == 1
    
    def test_get_failure_statistics(self, tracker):
        """Test getting failure statistics."""
        # Record some failures
        tracker.record_failure("task1", "researcher", "Error 1")
        tracker.record_failure("task2", "installer", "Error 2")
        
        stats = tracker.get_failure_statistics()
        
        assert "total_failures" in stats
        assert "agent_failure_counts" in stats
        assert stats["total_failures"] == 2
        assert "researcher" in stats["agent_failure_counts"]
        assert "installer" in stats["agent_failure_counts"]


if __name__ == "__main__":
    pytest.main([__file__])