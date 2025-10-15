"""
Code Execution Agent for HAWK-AI.
Executes code in a sandboxed environment.
"""
from typing import Dict, Any, Optional
import re
from datetime import datetime
from rich.console import Console

from core.tools_codeexec import get_codeexec_tool
from core.local_tracking import get_tracker

console = Console()


class CodeExecAgent:
    """Agent for safe code execution."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize code execution agent."""
        self.config_path = config_path
        self.codeexec_tool = get_codeexec_tool(config_path)
        self.tracker = get_tracker(config_path)
        
        console.print("[green]CodeExec Agent initialized[/green]")
    
    def execute_from_query(self, query: str) -> str:
        """
        Extract and execute code from a query.
        
        Args:
            query: Query containing code to execute
            
        Returns:
            Execution results
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("codeexec", query)
        
        try:
            # Extract code from query
            code = self._extract_code(query)
            
            if not code:
                return "No executable code found in query. Please provide code in markdown code blocks."
            
            console.print(f"[cyan]Executing code ({len(code)} characters)[/cyan]")
            
            # Execute code
            result = self.codeexec_tool.execute_python(code)
            
            # Log execution
            self.tracker.log_tool_call(
                "codeexec",
                "execute_python",
                {"code_length": len(code)},
                f"Status: {result['status']}"
            )
            
            # Format result
            formatted_result = self._format_execution_result(code, result)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("codeexec", formatted_result, duration)
            
            return formatted_result
            
        except Exception as e:
            console.print(f"[red]CodeExec error: {e}[/red]")
            self.tracker.log_error("codeexec", e)
            return f"Error executing code: {str(e)}"
    
    def execute_code(self, code: str, language: str = "python") -> str:
        """
        Execute code directly.
        
        Args:
            code: Code to execute
            language: Programming language (currently only python supported)
            
        Returns:
            Execution results
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("codeexec", f"{language} code")
        
        try:
            if language.lower() != "python":
                return f"Language '{language}' not supported. Currently only Python is supported."
            
            console.print(f"[cyan]Executing {language} code[/cyan]")
            
            # Execute code
            result = self.codeexec_tool.execute_python(code)
            
            # Log execution
            self.tracker.log_tool_call(
                "codeexec",
                "execute_python",
                {"language": language, "code_length": len(code)},
                f"Status: {result['status']}"
            )
            
            # Format result
            formatted_result = self._format_execution_result(code, result)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("codeexec", formatted_result, duration)
            
            return formatted_result
            
        except Exception as e:
            console.print(f"[red]CodeExec error: {e}[/red]")
            self.tracker.log_error("codeexec", e)
            return f"Error executing code: {str(e)}"
    
    def _extract_code(self, query: str) -> Optional[str]:
        """
        Extract code from markdown code blocks in query.
        
        Args:
            query: Query text
            
        Returns:
            Extracted code or None
        """
        # Look for markdown code blocks
        # Pattern: ```python\ncode\n``` or ```\ncode\n```
        pattern = r'```(?:python)?\n(.*?)```'
        matches = re.findall(pattern, query, re.DOTALL)
        
        if matches:
            # Return the first code block
            return matches[0].strip()
        
        # If no markdown blocks, check if entire query looks like code
        # Simple heuristic: contains common Python keywords
        if any(keyword in query for keyword in ['import ', 'def ', 'class ', 'for ', 'if ', 'print(']):
            return query.strip()
        
        return None
    
    def _format_execution_result(self, code: str, result: Dict[str, Any]) -> str:
        """
        Format execution result for display.
        
        Args:
            code: Executed code
            result: Execution result dictionary
            
        Returns:
            Formatted result string
        """
        formatted_parts = [
            "=" * 80,
            "CODE EXECUTION RESULT",
            "=" * 80,
            "\nEXECUTED CODE:",
            "-" * 80,
            code,
            "\n" + "-" * 80,
            f"\nSTATUS: {result['status'].upper()}"
        ]
        
        if result.get('stdout'):
            formatted_parts.append("\nOUTPUT:")
            formatted_parts.append("-" * 80)
            formatted_parts.append(result['stdout'])
        
        if result.get('stderr'):
            formatted_parts.append("\nERRORS/WARNINGS:")
            formatted_parts.append("-" * 80)
            formatted_parts.append(result['stderr'])
        
        if result.get('error'):
            formatted_parts.append("\nERROR:")
            formatted_parts.append("-" * 80)
            formatted_parts.append(result['error'])
        
        if 'returncode' in result:
            formatted_parts.append(f"\nReturn Code: {result['returncode']}")
        
        formatted_parts.append("\n" + "=" * 80)
        
        return "\n".join(formatted_parts)
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate code without executing it.
        
        Args:
            code: Code to validate
            
        Returns:
            Validation result
        """
        try:
            console.print("[cyan]Validating code...[/cyan]")
            
            is_valid, error_msg = self.codeexec_tool._validate_code(code)
            
            result = {
                "is_valid": is_valid,
                "message": "Code passed validation" if is_valid else error_msg
            }
            
            self.tracker.log_tool_call(
                "codeexec",
                "validate_code",
                {"code_length": len(code)},
                result['message']
            )
            
            if is_valid:
                console.print("[green]✓ Code validation passed[/green]")
            else:
                console.print(f"[red]✗ Code validation failed: {error_msg}[/red]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]Validation error: {e}[/red]")
            return {
                "is_valid": False,
                "message": f"Validation error: {str(e)}"
            }
    
    def execute_with_validation(self, code: str) -> str:
        """
        Validate and execute code.
        
        Args:
            code: Code to execute
            
        Returns:
            Execution results or validation error
        """
        # First validate
        validation = self.validate_code(code)
        
        if not validation['is_valid']:
            return f"Code validation failed: {validation['message']}"
        
        # Then execute
        return self.execute_code(code)

