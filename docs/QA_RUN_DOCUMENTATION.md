# bAIos QA Testing - Step-by-Step Run Documentation

## 🎯 **PURPOSE**
Validate actual functionality of the bAIos onboarding system components.

## ⚡ **QUICK START (5 minutes)**

### **Test 1: Verify Core System Structure**
```bash
# Navigate to project
cd /home/delorenj/code/AIOnboarding/bAIos

# Check all deliverables exist
ls -la docs/INVENTORY_ENHANCED.md     # ✅ Should exist
ls -la docs/dependency_graph.md      # ✅ Should exist
ls -la agents/coordinator/agent.py   # ✅ Should exist
ls -la mcp/baios_server.py           # ✅ Should exist
ls -la agents/shell_master/agent.py  # ✅ Should exist
ls -la tests/test_coordinator.py     # ✅ Should exist
```

### **Test 2: Run MCP Server (Basic Functionality)**
```bash
# Test MCP server starts without errors
cd mcp/
python3 -c "
import asyncio
from baios_server import BaiosToolsServer

async def test():
    server = BaiosToolsServer()
    print('✅ MCP Server initialized successfully')
    
    # Test a safe command
    result = await server.execute_command('echo \"Hello bAIos\"')
    print(f'✅ Command execution: {result}')

asyncio.run(test())
"
```
**Expected Output:** 
```
✅ MCP Server initialized successfully
✅ Command execution: {'success': True, 'stdout': 'Hello bAIos', ...}
```

### **Test 3: Coordinator Agent Dry Run**
```bash
# Test coordinator without making changes
cd agents/coordinator/
python3 -c "
from agent import BaiosCoordinatorAgent
import asyncio

async def test():
    agent = BaiosCoordinatorAgent()
    agent.dry_run = True
    
    print('✅ Coordinator initialized')
    
    # Test dependency resolution
    deps = agent.dependency_manager.get_dependency_graph()
    print(f'✅ Dependency graph loaded: {len(deps)} nodes')
    
    # Test execution planning (dry run)
    plan = agent.dependency_manager.get_execution_plan()
    print(f'✅ Execution plan: {len(plan)} phases')
    
    for i, phase in enumerate(plan[:3]):  # Show first 3 phases
        print(f'   Phase {i+1}: {len(phase)} items')

asyncio.run(test())
"
```
**Expected Output:**
```
✅ Coordinator initialized
✅ Dependency graph loaded: 40+ nodes
✅ Execution plan: 6 phases
   Phase 1: 3 items
   Phase 2: 8 items
   Phase 3: 12 items
```

### **Test 4: Shell Master Agent Test**
```bash
# Test shell master configuration loading
cd agents/shell_master/
python3 -c "
import yaml
from agent import ShellMasterAgent
import asyncio

async def test():
    # Test configuration loading
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print(f'✅ Config loaded: {len(config)} sections')
    
    # Test agent initialization
    agent = ShellMasterAgent()
    agent.dry_run = True
    print('✅ ShellMaster agent initialized')
    
    # Test verification without installation
    verifiers = agent.get_available_verifiers()
    print(f'✅ Available verifiers: {verifiers}')

asyncio.run(test())
"
```

## 🔬 **DETAILED FUNCTIONALITY TESTS**

### **Test 5: MCP Tools Validation**
```bash
cd mcp/
python3 -c "
import asyncio
from baios_server import BaiosToolsServer

async def test_tools():
    server = BaiosToolsServer()
    
    # Test 1: System info (safe)
    info = await server.get_system_info()
    print(f'✅ System info: {info[\"platform\"]} {info[\"version\"]}')
    
    # Test 2: File operations (safe)
    test_content = 'bAIos test file'
    write_result = await server.write_file('/tmp/baios_test.txt', test_content)
    print(f'✅ File write: {write_result[\"success\"]}')
    
    read_result = await server.read_file('/tmp/baios_test.txt')
    print(f'✅ File read: {read_result[\"content\"] == test_content}')
    
    # Test 3: Command execution (safe)
    cmd_result = await server.execute_command('whoami')
    print(f'✅ Command exec: {cmd_result[\"success\"]}')
    
    # Test 4: Dangerous command blocking
    try:
        danger_result = await server.execute_command('rm -rf /')
        print('❌ Dangerous command not blocked!')
    except Exception as e:
        print('✅ Dangerous command properly blocked')
    
    # Cleanup
    await server.execute_command('rm -f /tmp/baios_test.txt')

asyncio.run(test_tools())
"
```

### **Test 6: Dependency Graph Functionality**
```bash
cd agents/coordinator/tools/
python3 -c "
from dependency_manager import DependencyManager

# Test dependency resolution
dm = DependencyManager()
graph = dm.get_dependency_graph()

print(f'✅ Graph nodes: {len(graph.nodes())}')
print(f'✅ Graph edges: {len(graph.edges())}')

# Test topological sort (execution order)
plan = dm.get_execution_plan()
print(f'✅ Execution phases: {len(plan)}')

# Test specific dependencies
if dm.has_dependency('oh-my-zsh', 'zsh'):
    print('✅ oh-my-zsh correctly depends on zsh')

if dm.has_dependency('docker-compose', 'docker'):
    print('✅ docker-compose correctly depends on docker')

# Test cycle detection
if not dm.has_cycles():
    print('✅ No dependency cycles detected')
else:
    print('❌ Dependency cycles found')
"
```

### **Test 7: Progress Tracking**
```bash
cd agents/coordinator/tools/
python3 -c "
from checklist_tracker import ChecklistTracker

# Initialize with some test items
tracker = ChecklistTracker()

# Add test items
test_items = [
    ('zsh', 'pending', 'high'),
    ('oh-my-zsh', 'pending', 'high'),
    ('neovim', 'pending', 'medium'),
    ('docker', 'pending', 'low')
]

for name, status, priority in test_items:
    tracker.add_item(name, status, priority)

print(f'✅ Added {len(test_items)} test items')

# Test status updates
tracker.update_item_status('zsh', 'in_progress')
tracker.update_item_status('oh-my-zsh', 'completed')

# Test progress calculation
progress = tracker.get_progress_summary()
print(f'✅ Progress: {progress[\"completion_percentage\"]}%')

# Test report generation
report = tracker.generate_report()
print('✅ Progress report generated')
print(f'   - Pending: {report[\"status_counts\"][\"pending\"]}')
print(f'   - Completed: {report[\"status_counts\"][\"completed\"]}')
"
```

## 🔥 **LIVE DEMO (Optional - 10 minutes)**

### **Demo 1: Safe Shell Master Installation**
```bash
# WARNING: This will modify your shell config (creates backups)
cd agents/shell_master/

# Create backup first
cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Run shell master in safe mode (with prompts)
python3 agent.py --mode interactive --dry-run false --verbose

# This will:
# 1. Check if zsh is installed
# 2. Install zsh if missing (via apt)
# 3. Install oh-my-zsh framework
# 4. Configure basic shell settings
# 5. Verify installation
```

### **Demo 2: Complete System Test**
```bash
# Full coordinator test (dry run - no changes)
cd agents/coordinator/

python3 agent.py \
  --mode interactive \
  --dry-run true \
  --verbose \
  --config config.yaml

# This will:
# 1. Load dependency graph
# 2. Plan execution phases
# 3. Show what would be installed
# 4. Display progress tracking
# 5. Generate final report
```

## ✅ **SUCCESS CRITERIA**

### **Minimum Passing Requirements:**
1. ✅ All file structure checks pass
2. ✅ MCP server initializes and executes commands
3. ✅ Coordinator loads dependency graph (40+ nodes)
4. ✅ Dangerous commands are blocked
5. ✅ Progress tracking works
6. ✅ No Python errors in any test

### **Full Functionality Demonstrated:**
1. ✅ MCP tools execute safely with proper blocking
2. ✅ Dependency graph resolves correctly 
3. ✅ Agent coordination protocols work
4. ✅ Progress tracking updates in real-time
5. ✅ File operations with backup/restore
6. ✅ Configuration loading and validation

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**
```bash
# Python import errors
pip3 install pyyaml networkx asyncio pathlib

# Permission errors
chmod +x agents/*/agent.py

# Missing dependencies
sudo apt update && sudo apt install -y python3-pip python3-yaml

# MCP server port conflicts
ps aux | grep python3  # Kill any running Python processes
```

### **Expected Runtime:**
- **Quick tests (1-4)**: ~2 minutes
- **Detailed tests (5-7)**: ~5 minutes  
- **Live demo**: ~10 minutes
- **Total validation**: ~15-20 minutes

## 📊 **TEST RESULTS TEMPLATE**

```
bAIos QA Test Results - [Date/Time]
==========================================

✅/❌ Test 1: File structure validation
✅/❌ Test 2: MCP server functionality  
✅/❌ Test 3: Coordinator dry run
✅/❌ Test 4: Shell master initialization
✅/❌ Test 5: MCP tools validation
✅/❌ Test 6: Dependency graph functionality
✅/❌ Test 7: Progress tracking

Overall Status: PASS/FAIL
Issues Found: [List any problems]
Recommendations: [Any suggested improvements]
```

This run doc provides concrete, executable validation of the bAIos system functionality that your QA team can complete in under 20 minutes.