"""
Agent Testing Example
=====================

Demonstrates testing individual specialized agents.
"""

import asyncio
import logging
from ..agents import ResearcherAgent, InstallerAgent, QAExpertAgent
from ..orchestrator import AgentFactory
from ..schemas import AgentRequest

# Configure logging
logging.basicConfig(level=logging.INFO)


async def test_researcher_agent():
    """Test the Researcher Agent."""
    print("🔍 Testing Researcher Agent")
    print("-" * 40)
    
    factory = AgentFactory()
    researcher = factory.create_agent("researcher")
    
    # Test environment specification analysis
    request = AgentRequest(
        agent_type="researcher",
        task_description="Analyze environment specification and validate requirements",
        context={
            "spec_content": """
# Sample WSL Environment Spec
- Ubuntu 22.04 with WSL 2
- Python 3.12.9 via mise
- Node.js latest via mise
- zsh with oh-my-zsh
- Docker integration
            """,
            "user_preferences": {"minimal_install": False}
        }
    )
    
    response = await researcher.run_async(request)
    
    print(f"Status: {response.status}")
    print(f"Execution Time: {response.execution_time:.2f}s")
    
    if response.result:
        analysis = response.result
        print(f"Analysis Type: {analysis.get('analysis_type')}")
        print(f"Requirements Found: {len(analysis.get('requirements', {}))}")
        print(f"Validation Passed: {analysis.get('validation', {}).get('valid', False)}")
        print(f"Estimated Install Time: {analysis.get('estimated_install_time', 0)} minutes")
        
        if analysis.get('potential_issues'):
            print("Potential Issues:")
            for issue in analysis['potential_issues'][:3]:
                print(f"  - {issue}")
    
    print()


async def test_installer_agent():
    """Test the Installer Agent."""
    print("📦 Testing Installer Agent")
    print("-" * 40)
    
    factory = AgentFactory()
    installer = factory.create_agent("installer")
    
    # Test base tools installation (dry run)
    request = AgentRequest(
        agent_type="installer", 
        task_description="Install base development tools",
        context={"dry_run": True}
    )
    
    response = await installer.run_async(request)
    
    print(f"Status: {response.status}")
    print(f"Execution Time: {response.execution_time:.2f}s")
    
    if response.result:
        result = response.result
        print(f"Task Type: {result.get('task_type')}")
        print(f"Packages Attempted: {result.get('packages_attempted', 0)}")
        print(f"Packages Successful: {result.get('packages_successful', 0)}")
        print(f"Overall Success: {result.get('overall_success', False)}")
    
    print()


async def test_qa_expert_agent():
    """Test the QA Expert Agent."""
    print("✅ Testing QA Expert Agent")
    print("-" * 40)
    
    factory = AgentFactory()
    qa_expert = factory.create_agent("qa_expert")
    
    # Test comprehensive validation
    request = AgentRequest(
        agent_type="qa_expert",
        task_description="Perform comprehensive validation of WSL environment",
        context={
            "session_id": "test_session",
            "completed_tasks": ["install_base_tools", "setup_shell", "configure_git"],
            "failed_tasks": ["setup_docker"]
        }
    )
    
    response = await qa_expert.run_async(request)
    
    print(f"Status: {response.status}")
    print(f"Execution Time: {response.execution_time:.2f}s")
    
    # QA Expert returns QAResult, which might be in the result field
    if hasattr(response, 'result') and response.result:
        qa_result = response.result
        if isinstance(qa_result, dict):
            print(f"Validation Passed: {qa_result.get('validation_passed', False)}")
            print(f"Success Criteria Met: {len(qa_result.get('success_criteria_met', []))}")
            print(f"Failures: {len(qa_result.get('failures', []))}")
            print(f"Confidence Score: {qa_result.get('confidence_score', 0):.2f}")
            
            if qa_result.get('remediation_suggestions'):
                print("Remediation Suggestions:")
                for suggestion in qa_result['remediation_suggestions'][:3]:
                    print(f"  - {suggestion}")
    
    print()


async def test_all_agents():
    """Test all specialized agents."""
    print("🤖 WSL Orchestrator - Agent Testing Suite")
    print("=" * 60)
    
    try:
        await test_researcher_agent()
        await test_installer_agent()
        await test_qa_expert_agent()
        
        # Test agent metrics
        factory = AgentFactory()
        
        print("📊 Agent Metrics Summary")
        print("-" * 40)
        
        for agent_type in ["researcher", "installer", "qa_expert"]:
            agent = factory.create_agent(agent_type)
            if hasattr(agent, 'get_agent_metrics'):
                metrics = agent.get_agent_metrics()
                print(f"{agent_type.title()} Agent:")
                print(f"  Total Executions: {metrics.get('total_executions', 0)}")
                print(f"  Success Rate: {metrics.get('success_rate', 0):.1f}%")
                print(f"  Average Execution Time: {metrics.get('average_execution_time', 0):.2f}s")
        
        print("\n✅ Agent testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during agent testing: {str(e)}")
        logging.error(f"Agent testing failed: {e}")


def sync_test_all_agents():
    """Synchronous wrapper for the async test function."""
    asyncio.run(test_all_agents())


if __name__ == "__main__":
    sync_test_all_agents()