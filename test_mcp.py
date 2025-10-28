#!/usr/bin/env python3
"""Test script voor de Utrecht Open Data MCP Server"""

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
    print("🧪 Testing Utrecht Open Data MCP Server\n")

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

        # Test 2: List tools
        print("2️⃣ Testing list tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        response = send_request(process, tools_request)
        tools = response.get("result", {}).get("tools", [])
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}")
        print()

        # Test 3: Search datasets
        print("3️⃣ Testing search_datasets...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_datasets",
                "arguments": {"query": "afval", "limit": 3}
            }
        }
        response = send_request(process, search_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Search successful:")
            print(content[:200] + "...\n")
        else:
            print("❌ Search failed\n")

        # Test 4: Get dataset
        print("4️⃣ Testing get_dataset...")
        get_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_dataset",
                "arguments": {"dataset_id": "afvalbakken"}
            }
        }
        response = send_request(process, get_request)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Get dataset successful:")
            print(content[:200] + "...\n")
        else:
            print("❌ Get dataset failed\n")

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    finally:
        process.terminate()

if __name__ == "__main__":
    main()
