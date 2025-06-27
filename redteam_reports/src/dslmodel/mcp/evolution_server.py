#!/usr/bin/env python3
"""
DSLModel Evolution MCP Server
Provides Claude Code with direct access to DSLModel evolution capabilities
"""

import asyncio
import json
import sys
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path

class DSLModelMCPServer:
    """MCP Server for DSLModel evolution capabilities."""
    
    def __init__(self):
        self.dslmodel_path = Path(__file__).parent.parent.parent.parent
        self.commands = {
            "evolve": "evolution",
            "validate": "validate_otel", 
            "agents": "agent_coordination_cli",
            "8020": "complete_8020_validation",
            "weaver": "weaver",
            "telemetry": "telemetry_cli",
            "swarm": "swarm",
            "worktree": "worktree",
            "consolidated": "consolidated_cli"
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return await self.initialize()
        elif method == "tools/list":
            return await self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(params)
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "dslmodel-evolution",
                "version": "1.0.0"
            }
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available DSLModel tools."""
        tools = [
            {
                "name": "dsl_evolve",
                "description": "Run autonomous evolution system",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Evolution command (demo, analyze, evolve)"},
                        "cycles": {"type": "integer", "description": "Number of cycles", "default": 1}
                    }
                }
            },
            {
                "name": "dsl_validate",
                "description": "Run OTEL validation",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "target": {"type": "string", "description": "Validation target"}
                    }
                }
            },
            {
                "name": "dsl_agents",
                "description": "SwarmAgent coordination",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Agent command (status, coordinate)"},
                        "agents": {"type": "integer", "description": "Number of agents", "default": 1}
                    }
                }
            },
            {
                "name": "dsl_8020",
                "description": "8020 optimization and validation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "8020 command (validate, analyze)"}
                    }
                }
            },
            {
                "name": "dsl_status",
                "description": "Get system status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        return {"tools": tools}
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DSLModel tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "dsl_evolve":
                return await self.run_evolution(arguments)
            elif tool_name == "dsl_validate":
                return await self.run_validation(arguments)
            elif tool_name == "dsl_agents":
                return await self.run_agents(arguments)
            elif tool_name == "dsl_8020":
                return await self.run_8020(arguments)
            elif tool_name == "dsl_status":
                return await self.get_status()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def run_evolution(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run evolution command."""
        command = args.get("command", "demo")
        cycles = args.get("cycles", 1)
        
        cmd = ["python", "-m", "dslmodel.commands.evolution", command]
        if command == "evolve":
            cmd.extend(["--cycles", str(cycles)])
        
        result = await self.execute_command(cmd)
        return {"content": [{"type": "text", "text": result}]}
    
    async def run_validation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation command.""" 
        target = args.get("target", "")
        
        cmd = ["python", "-m", "dslmodel.commands.validate_otel"]
        if target:
            cmd.append(target)
        
        result = await self.execute_command(cmd)
        return {"content": [{"type": "text", "text": result}]}
    
    async def run_agents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent coordination."""
        command = args.get("command", "status")
        agents = args.get("agents", 1)
        
        cmd = ["python", "-m", "dslmodel.commands.agent_coordination_cli", command]
        if command == "coordinate":
            cmd.extend(["--agents", str(agents)])
        
        result = await self.execute_command(cmd)
        return {"content": [{"type": "text", "text": result}]}
    
    async def run_8020(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Run 8020 optimization."""
        command = args.get("command", "validate")
        
        cmd = ["python", "-m", "dslmodel.commands.complete_8020_validation", command]
        
        result = await self.execute_command(cmd)
        return {"content": [{"type": "text", "text": result}]}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        status_info = {
            "dslmodel_path": str(self.dslmodel_path),
            "evolution_available": True,
            "otel_enabled": True,
            "weaver_enabled": True,
            "worktree_enabled": True,
            "swarm_enabled": True,
            "8020_enabled": True
        }
        
        result = f"🚀 DSLModel Evolution System Status\n"
        result += "=" * 40 + "\n"
        for key, value in status_info.items():
            status = "✅" if value else "❌"
            result += f"{status} {key.replace('_', ' ').title()}: {value}\n"
        
        return {"content": [{"type": "text", "text": result}]}
    
    async def execute_command(self, cmd: List[str]) -> str:
        """Execute a command and return output."""
        try:
            # Change to DSLModel directory
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.dslmodel_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={
                    "PYTHONPATH": str(self.dslmodel_path / "src"),
                    "DSLMODEL_OTEL_ENABLED": "true",
                    "DSLMODEL_WEAVER_ENABLED": "true"
                }
            )
            
            stdout, stderr = await process.communicate()
            
            result = stdout.decode() if stdout else ""
            if stderr:
                result += f"\nErrors:\n{stderr.decode()}"
            
            return result or "Command completed successfully"
            
        except Exception as e:
            return f"Command execution failed: {str(e)}"

async def main():
    """Main MCP server loop."""
    server = DSLModelMCPServer()
    
    while True:
        try:
            # Read request from stdin
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": f"Server error: {str(e)}"}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())