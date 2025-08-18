"""
Basic Usage Example
===================

Demonstrates basic usage of the WSL orchestrator system.
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)

from ..orchestrator import RootOrchestrator
from ..schemas import ProvisioningRequest


async def main():
    """Basic usage example."""
    print("🚀 WSL Environment Orchestrator - Basic Usage Example")
    print("=" * 60)
    
    # Initialize the root orchestrator
    orchestrator = RootOrchestrator()
    
    # Get current directory and construct path to environment spec
    current_dir = Path(__file__).parent.parent.parent
    spec_path = current_dir / "docs" / "WSL_ENVIRONMENT_SPEC.md"
    
    print(f"📋 Using environment specification: {spec_path}")
    
    # Create provisioning request
    request = ProvisioningRequest(
        environment_spec_path=str(spec_path),
        user_preferences={
            "minimal_install": False,
            "skip_optional_tools": False,
            "parallel_execution": True
        },
        dry_run=True,  # Set to False for actual provisioning
        force_reinstall=False
    )
    
    print(f"🔧 Starting {'DRY RUN' if request.dry_run else 'LIVE'} provisioning...")
    
    try:
        # Execute provisioning
        response = await orchestrator.provision_environment(request)
        
        # Display results
        print(f"\n✅ Provisioning Results:")
        print(f"   Session ID: {response.session_id}")
        print(f"   Status: {response.status}")
        print(f"   Current Phase: {response.current_phase}")
        print(f"   Progress: {response.progress_percentage}%")
        print(f"   Completed Tasks: {len(response.completed_tasks)}")
        print(f"   Failed Tasks: {len(response.failed_tasks)}")
        print(f"   Pending Tasks: {len(response.pending_tasks)}")
        print(f"   Total Time: {response.total_execution_time:.1f}s")
        print(f"   Human Interventions: {response.human_interventions_required}")
        
        if response.failed_tasks:
            print(f"\n❌ Failed Tasks:")
            for task in response.failed_tasks:
                print(f"   - {task}")
        
        if response.completed_tasks:
            print(f"\n✅ Completed Tasks:")
            for task in response.completed_tasks[:5]:  # Show first 5
                print(f"   - {task}")
            if len(response.completed_tasks) > 5:
                print(f"   ... and {len(response.completed_tasks) - 5} more")
        
        # Show orchestrator status
        status = orchestrator.get_orchestration_status()
        print(f"\n🏗️ Orchestrator Status:")
        print(f"   Active Sessions: {len(status.active_sessions)}")
        print(f"   System Uptime: {status.uptime:.1f}s")
        
    except Exception as e:
        print(f"\n❌ Error during provisioning: {str(e)}")
        logging.error(f"Provisioning failed: {e}")


def sync_main():
    """Synchronous wrapper for the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()