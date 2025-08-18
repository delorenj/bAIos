"""
Stub Agent Tests
================

Tests for stub agent functionality.
"""

import pytest
import asyncio
from unittest.mock import patch
from ..agents.stub_agent import StubAgent, StubQAExpertAgent, StubAgentFactory
from ..schemas import AgentRequest, QAResult


class TestStubAgent:
    """Test cases for StubAgent."""
    
    @pytest.fixture
    def stub_agent(self):
        """Create a test stub agent."""
        return StubAgent("researcher", success_rate=1.0, execution_delay=0.1)
    
    @pytest.fixture
    def sample_request(self):
        """Create a sample agent request."""
        return AgentRequest(
            agent_type="researcher",
            task_description="Test task",
            context={"test": True}
        )
    
    def test_stub_agent_initialization(self, stub_agent):
        """Test stub agent initialization."""
        assert stub_agent.agent_type == "researcher"
        assert stub_agent.success_rate == 1.0
        assert stub_agent.execution_delay == 0.1
        assert stub_agent.execution_count == 0
    
    @pytest.mark.asyncio
    async def test_stub_agent_successful_execution(self, stub_agent, sample_request):
        """Test successful stub agent execution."""
        result = await stub_agent._execute_task(sample_request)
        
        assert result["success"] is True
        assert result["task_type"] == "researcher"
        assert result["execution_count"] == 1
        assert "analysis_type" in result  # Researcher-specific data
        assert "requirements" in result
    
    @pytest.mark.asyncio
    async def test_stub_agent_failure_execution(self, sample_request):
        """Test stub agent failure execution."""
        # Create agent that always fails
        failing_agent = StubAgent("installer", success_rate=0.0, execution_delay=0.1)
        
        result = await failing_agent._execute_task(sample_request)
        
        assert result["success"] is False
        assert result["task_type"] == "installer"
        assert "error_code" in result
        assert result["retry_suggested"] is True
    
    def test_stub_agent_metrics(self, stub_agent):
        """Test getting stub agent metrics."""
        metrics = stub_agent.get_stub_metrics()
        
        assert metrics["agent_type"] == "researcher"
        assert metrics["success_rate"] == 1.0
        assert metrics["execution_delay"] == 0.1
        assert metrics["stub_mode"] is True
    
    @pytest.mark.asyncio
    async def test_multiple_executions(self, stub_agent, sample_request):
        """Test multiple executions increment counter."""
        await stub_agent._execute_task(sample_request)
        await stub_agent._execute_task(sample_request)
        result = await stub_agent._execute_task(sample_request)
        
        assert result["execution_count"] == 3
        assert stub_agent.execution_count == 3


class TestStubQAExpertAgent:
    """Test cases for StubQAExpertAgent."""
    
    @pytest.fixture
    def stub_qa_agent(self):
        """Create a test stub QA agent."""
        return StubQAExpertAgent(success_rate=1.0)
    
    @pytest.fixture
    def qa_request(self):
        """Create a QA-specific request."""
        return AgentRequest(
            agent_type="qa_expert",
            task_description="Validate environment",
            context={"task_id": "test_validation", "session_id": "test"}
        )
    
    @pytest.mark.asyncio
    async def test_qa_agent_successful_validation(self, stub_qa_agent, qa_request):
        """Test successful QA validation."""
        result = await stub_qa_agent._execute_task(qa_request)
        
        assert isinstance(result, QAResult)
        assert result.validation_passed is True
        assert result.task_id == "test_validation"
        assert len(result.success_criteria_met) > 0
        assert len(result.failures) == 0
        assert result.confidence_score > 0.9
    
    @pytest.mark.asyncio
    async def test_qa_agent_failed_validation(self, qa_request):
        """Test failed QA validation."""
        # Create QA agent that always fails
        failing_qa = StubQAExpertAgent(success_rate=0.0)
        
        result = await failing_qa._execute_task(qa_request)
        
        assert isinstance(result, QAResult)
        assert result.validation_passed is False
        assert len(result.failures) > 0
        assert len(result.remediation_suggestions) > 0
        assert result.confidence_score < 0.9


class TestStubAgentFactory:
    """Test cases for StubAgentFactory."""
    
    @pytest.fixture
    def factory(self):
        """Create a test stub agent factory."""
        return StubAgentFactory(default_success_rate=0.9, default_delay=0.1)
    
    def test_factory_initialization(self, factory):
        """Test factory initialization."""
        assert factory.default_success_rate == 0.9
        assert factory.default_delay == 0.1
        assert len(factory.stub_agents) == 0
    
    def test_create_stub_agent(self, factory):
        """Test creating stub agents."""
        agent = factory.create_stub_agent("researcher")
        
        assert isinstance(agent, StubAgent)
        assert agent.agent_type == "researcher"
        assert agent.success_rate == 0.95  # Type-specific rate
    
    def test_create_qa_stub_agent(self, factory):
        """Test creating QA stub agent."""
        agent = factory.create_stub_agent("qa_expert")
        
        assert isinstance(agent, StubQAExpertAgent)
        assert agent.agent_type == "qa_expert"
        assert agent.success_rate == 0.80  # Type-specific rate
    
    def test_agent_caching(self, factory):
        """Test that agents are cached."""
        agent1 = factory.create_stub_agent("researcher")
        agent2 = factory.create_stub_agent("researcher")
        
        assert agent1 is agent2
        assert len(factory.stub_agents) == 1
    
    def test_create_failure_prone_agent(self, factory):
        """Test creating failure-prone agent."""
        agent = factory.create_failure_prone_agent("installer", failure_rate=0.8)
        
        assert agent.success_rate == 0.2  # 1.0 - 0.8
    
    def test_custom_success_rate(self, factory):
        """Test creating agent with custom success rate."""
        agent = factory.create_stub_agent("shell_master", success_rate=0.5)
        
        assert agent.success_rate == 0.5
    
    def test_get_all_stub_agents(self, factory):
        """Test getting all stub agents."""
        factory.create_stub_agent("researcher")
        factory.create_stub_agent("installer")
        factory.create_stub_agent("qa_expert")
        
        agents = factory.get_all_stub_agents()
        
        assert len(agents) == 3
        assert "researcher" in agents
        assert "installer" in agents
        assert "qa_expert" in agents
    
    def test_reset_agents(self, factory):
        """Test resetting all agents."""
        factory.create_stub_agent("researcher")
        factory.create_stub_agent("installer")
        
        assert len(factory.stub_agents) == 2
        
        factory.reset_agents()
        
        assert len(factory.stub_agents) == 0


class TestStubAgentIntegration:
    """Integration tests for stub agents with orchestrator."""
    
    @pytest.mark.asyncio
    async def test_stub_agents_with_different_types(self):
        """Test creating and using different types of stub agents."""
        factory = StubAgentFactory()
        
        agent_types = ["researcher", "installer", "shell_master", "mise_master", 
                      "authorizer", "progress_tracker", "qa_expert"]
        
        agents = {}
        for agent_type in agent_types:
            agents[agent_type] = factory.create_stub_agent(agent_type)
        
        # Test each agent type
        for agent_type, agent in agents.items():
            request = AgentRequest(
                agent_type=agent_type,
                task_description=f"Test {agent_type} task",
                context={"test": True}
            )
            
            result = await agent._execute_task(request)
            
            if agent_type == "qa_expert":
                assert isinstance(result, QAResult)
            else:
                assert isinstance(result, dict)
                assert "task_type" in result
    
    @pytest.mark.asyncio
    async def test_stub_agent_reliability_simulation(self):
        """Test stub agents with different reliability scenarios."""
        factory = StubAgentFactory()
        
        # Create agents with different success rates
        reliable_agent = factory.create_stub_agent("researcher", success_rate=0.95)
        unreliable_agent = factory.create_stub_agent("installer", success_rate=0.3)
        
        request = AgentRequest(
            agent_type="test",
            task_description="Reliability test",
            context={}
        )
        
        # Test reliable agent (should mostly succeed)
        reliable_results = []
        for _ in range(20):
            result = await reliable_agent._execute_task(request)
            reliable_results.append(result["success"])
        
        success_rate = sum(reliable_results) / len(reliable_results)
        assert success_rate >= 0.8  # Should be mostly successful
        
        # Test unreliable agent (should mostly fail)
        unreliable_results = []
        for _ in range(20):
            result = await unreliable_agent._execute_task(request)
            unreliable_results.append(result["success"])
        
        success_rate = sum(unreliable_results) / len(unreliable_results)
        assert success_rate <= 0.5  # Should be mostly failures


if __name__ == "__main__":
    pytest.main([__file__])