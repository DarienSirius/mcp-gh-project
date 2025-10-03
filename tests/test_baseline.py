"""
Test Server Startup and Basic Functionality

CRITICAL: Run this BEFORE refactoring to establish baseline.
Tests that v0.0.1 server starts and tools are accessible.
"""

import subprocess
import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def test_server_starts():
    """Test that server.py starts without crashing"""
    print("🧪 Test 1: Server starts without errors...")
    
    # Start server (will hang waiting for stdin)
    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "src" / "server.py")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it 2 seconds to crash if there's an import/syntax error
    time.sleep(2)
    
    # Check if still running
    if proc.poll() is None:
        print("✅ Server started successfully (no immediate crash)")
        proc.terminate()
        proc.wait()
        return True
    else:
        stdout, stderr = proc.communicate()
        print(f"❌ Server crashed immediately:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

def test_tools_list():
    """Test that tools/list RPC call works"""
    print("\n🧪 Test 2: List available tools...")
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "src" / "server.py")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = proc.communicate(json.dumps(request) + "\n", timeout=5)
        
        # Parse response
        try:
            response = json.loads(stdout)
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'unknown')}")
                return len(tools) == 11  # Expect 11 tools in v0.0.1
            else:
                print(f"❌ Unexpected response format: {response}")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"STDOUT: {stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        proc.kill()
        print("❌ Server timed out (might be hung)")
        return False

def main():
    print("="*60)
    print("BASELINE TESTS - v0.0.1 Server Validation")
    print("="*60)
    print("\nThese tests establish that current code works.")
    print("Run again after refactoring to catch regressions.\n")
    
    results = []
    
    results.append(("Server Startup", test_server_starts()))
    results.append(("Tools List", test_tools_list()))
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All baseline tests passed!")
        print("Safe to begin refactoring.")
        return 0
    else:
        print("\n⚠️  Some tests failed!")
        print("Fix issues before refactoring.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
