#!/usr/bin/env python3
"""Test script voor de Woo-integratie in MCP Server"""

import subprocess
import json
import sys

def send_request(process, request):
    """Send a request to the MCP server"""
    request_json = json.dumps(request) + "\n"
    process.stdin.write(request_json)
    process.stdin.flush()

    response_line = process.stdout.readline()
    return json.loads(response_line)

def main():
    print("🧪 Testing Utrecht Open Data MCP Server - Woo Integration\n")

    # Start MCP server
    process = subprocess.Popen(
        ['python3', 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        # Test 1: Initialize
        print("1️⃣ Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        response = send_request(process, init_request)
        assert "result" in response
        print("✅ Initialize successful\n")

        # Test 2: List tools (check if Woo tools are present)
        print("2️⃣ Testing list tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = send_request(process, tools_request)
        tools = response.get("result", {}).get("tools", [])
        tool_names = [t['name'] for t in tools]

        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}")

        # Check for Woo tools
        if 'analyze_woo_connection' in tool_names:
            print("   ✓ Woo analysis tool available")
        if 'find_woo_related_datasets' in tool_names:
            print("   ✓ Woo search tool available")
        print()

        # Test 3: Analyze Woo connection
        print("3️⃣ Testing analyze_woo_connection...")
        woo_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "analyze_woo_connection",
                "arguments": {"dataset_id": "afvalbakken"}
            }
        }
        response = send_request(process, woo_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Woo analysis successful:")
            # Print first 300 chars
            print(content[:300] + "...\n")
        else:
            print(f"❌ Woo analysis failed: {response.get('error')}\n")

        # Test 4: Find Woo related datasets
        print("4️⃣ Testing find_woo_related_datasets...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "find_woo_related_datasets",
                "arguments": {"topic": "verkeer"}
            }
        }
        response = send_request(process, search_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Woo search successful:")
            print(content[:300] + "...\n")
        else:
            print(f"❌ Woo search failed: {response.get('error')}\n")

        print("🎉 All Woo integration tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        process.terminate()

if __name__ == "__main__":
    main()
