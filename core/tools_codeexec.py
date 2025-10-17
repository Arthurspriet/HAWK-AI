"""
Code execution tools for HAWK-AI.
Provides safe sandboxed code execution capabilities.
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from rich.console import Console

console = Console()


class CodeExecutionTool:
    """Tool for safe code execution."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize code execution tool."""
        self.config = self._load_config(config_path)
        self.timeout = self.config['code_execution']['timeout']
        self.max_output_length = self.config['code_execution']['max_output_length']
        self.allowed_imports = set(self.config['code_execution']['allowed_imports'])
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _validate_code(self, code: str) -> tuple[bool, str]:
        """
        Validate code for safety.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for dangerous operations
        dangerous_keywords = [
            'os.system', 'subprocess.call', 'eval', 'exec',
            '__import__', 'open(', 'file(', 'input(',
            'os.remove', 'os.rmdir', 'shutil.rmtree'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in code:
                return False, f"Dangerous operation detected: {keyword}"
        
        # Basic import validation
        import_lines = [line.strip() for line in code.split('\n') if line.strip().startswith(('import ', 'from '))]
        for line in import_lines:
            parts = line.split()
            if len(parts) >= 2:
                module = parts[1].split('.')[0]
                if module not in self.allowed_imports and module not in ['sys', 'math', 'random', 'datetime', 'json', 'collections']:
                    return False, f"Import not allowed: {module}"
        
        return True, ""
    
    def execute_python(self, code: str, validate: bool = True) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            validate: Whether to validate code before execution
            
        Returns:
            Dictionary with execution results
        """
        if validate:
            is_valid, error_msg = self._validate_code(code)
            if not is_valid:
                console.print(f"[red]Code validation failed: {error_msg}[/red]")
                return {
                    "status": "validation_error",
                    "error": error_msg,
                    "stdout": "",
                    "stderr": ""
                }
        
        try:
            console.print("[cyan]Executing Python code...[/cyan]")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Clean up
            Path(temp_file).unlink()
            
            stdout = result.stdout[:self.max_output_length]
            stderr = result.stderr[:self.max_output_length]
            
            if result.returncode == 0:
                console.print("[green]Code executed successfully[/green]")
                return {
                    "status": "success",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": result.returncode
                }
            else:
                console.print(f"[yellow]Code execution failed with return code {result.returncode}[/yellow]")
                return {
                    "status": "error",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            console.print("[red]Code execution timed out[/red]")
            return {
                "status": "timeout",
                "error": f"Execution exceeded {self.timeout} seconds",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            console.print(f"[red]Execution error: {e}[/red]")
            return {
                "status": "error",
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def execute_shell(self, command: str) -> Dict[str, Any]:
        """
        Execute shell command (restricted).
        
        Args:
            command: Shell command to execute
            
        Returns:
            Dictionary with execution results
        """
        # Whitelist of safe commands
        safe_commands = ['ls', 'pwd', 'echo', 'cat', 'grep', 'wc', 'head', 'tail']
        
        cmd_base = command.split()[0]
        if cmd_base not in safe_commands:
            console.print(f"[red]Command not allowed: {cmd_base}[/red]")
            return {
                "status": "validation_error",
                "error": f"Command not in whitelist: {cmd_base}",
                "stdout": "",
                "stderr": ""
            }
        
        try:
            console.print(f"[cyan]Executing: {command}[/cyan]")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            stdout = result.stdout[:self.max_output_length]
            stderr = result.stderr[:self.max_output_length]
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": result.returncode
            }
            
        except Exception as e:
            console.print(f"[red]Execution error: {e}[/red]")
            return {
                "status": "error",
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        Format execution result for display.
        
        Args:
            result: Execution result dictionary
            
        Returns:
            Formatted string
        """
        parts = [f"Status: {result['status']}"]
        
        if result.get('stdout'):
            parts.append(f"\nOutput:\n{result['stdout']}")
        
        if result.get('stderr'):
            parts.append(f"\nErrors:\n{result['stderr']}")
        
        if result.get('error'):
            parts.append(f"\nError: {result['error']}")
        
        return "\n".join(parts)


def get_codeexec_tool(config_path: str = "config/settings.yaml") -> CodeExecutionTool:
    """Get code execution tool instance."""
    return CodeExecutionTool(config_path)


