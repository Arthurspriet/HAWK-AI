"""
Redactor Agent for HAWK-AI.
Summarizes and reformats text content.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console

from core.tools_redactor import get_redaction_tool
from core.local_tracking import get_tracker
from core.ollama_client import get_ollama_client

console = Console()


class RedactorAgent:
    """Agent for text summarization and reformatting."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize redactor agent."""
        self.config_path = config_path
        self.redaction_tool = get_redaction_tool(config_path)
        self.tracker = get_tracker(config_path)
        self.ollama_client = get_ollama_client(config_path)
        
        console.print("[green]Redactor Agent initialized[/green]")
    
    def create_summary(self, text: str, style: Optional[str] = None) -> str:
        """
        Create a summary of the provided text.
        
        Args:
            text: Text to summarize
            style: Optional style (professional, brief, technical, etc.)
            
        Returns:
            Summarized text
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("redactor", f"Summarize ({len(text)} chars)")
        
        try:
            console.print(f"[cyan]Creating summary of {len(text)} character text[/cyan]")
            
            # Use LLM for intelligent summarization
            style_instruction = f" in a {style} style" if style else ""
            
            prompt = f"""Please create a clear, concise summary of the following information{style_instruction}. 
Focus on key points, important findings, and actionable insights.

Content to summarize:
{text[:3000]}  # Truncate very long texts

Summary:"""
            
            summary = self.ollama_client.generate(prompt)
            
            # Log the summarization
            self.tracker.log_tool_call(
                "redactor",
                "summarize",
                {"input_length": len(text), "style": style},
                f"Generated {len(summary)} character summary"
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("redactor", summary, duration)
            
            return summary
            
        except Exception as e:
            console.print(f"[red]Redactor error: {e}[/red]")
            self.tracker.log_error("redactor", e)
            return f"Error creating summary: {str(e)}"
    
    def create_executive_brief(self, text: str, title: Optional[str] = None) -> str:
        """
        Create an executive brief from text.
        
        Args:
            text: Source text
            title: Optional title for the brief
            
        Returns:
            Executive brief
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("redactor", "Executive Brief")
        
        try:
            console.print("[cyan]Creating executive brief[/cyan]")
            
            # Generate executive summary using LLM
            prompt = f"""Create a professional executive brief from the following information. 
Include:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points)
3. Implications
4. Recommendations (if applicable)

Content:
{text[:3000]}

Executive Brief:"""
            
            brief = self.ollama_client.generate(prompt)
            
            # Format as report if title provided
            if title:
                brief = self.redaction_tool.format_as_report(
                    title,
                    brief,
                    {"Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("redactor", brief, duration)
            
            return brief
            
        except Exception as e:
            console.print(f"[red]Redactor error: {e}[/red]")
            self.tracker.log_error("redactor", e)
            return f"Error creating executive brief: {str(e)}"
    
    def extract_key_points(self, text: str, num_points: int = 5) -> str:
        """
        Extract key points from text.
        
        Args:
            text: Text to analyze
            num_points: Number of key points to extract
            
        Returns:
            Formatted key points
        """
        try:
            console.print(f"[cyan]Extracting {num_points} key points[/cyan]")
            
            prompt = f"""Extract the {num_points} most important key points from the following text.
Present them as a numbered list.

Text:
{text[:2000]}

Key Points:"""
            
            key_points = self.ollama_client.generate(prompt)
            
            self.tracker.log_tool_call(
                "redactor",
                "extract_key_points",
                {"num_points": num_points},
                f"Extracted {num_points} points"
            )
            
            return key_points
            
        except Exception as e:
            console.print(f"[red]Error extracting key points: {e}[/red]")
            return f"Error extracting key points: {str(e)}"
    
    def reformat_as_report(self, title: str, content: str, sections: Optional[Dict[str, str]] = None) -> str:
        """
        Reformat content as a structured report.
        
        Args:
            title: Report title
            content: Main content
            sections: Optional additional sections
            
        Returns:
            Formatted report
        """
        try:
            console.print("[cyan]Formatting as report[/cyan]")
            
            report_parts = [
                "=" * 80,
                title.center(80),
                "=" * 80,
                f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "\n" + "-" * 80,
                "\nMAIN FINDINGS:",
                "-" * 80,
                content
            ]
            
            if sections:
                for section_title, section_content in sections.items():
                    report_parts.append(f"\n\n{section_title.upper()}:")
                    report_parts.append("-" * 80)
                    report_parts.append(section_content)
            
            report_parts.append("\n" + "=" * 80)
            report_parts.append("End of Report")
            report_parts.append("=" * 80)
            
            return "\n".join(report_parts)
            
        except Exception as e:
            console.print(f"[red]Error formatting report: {e}[/red]")
            return content
    
    def redact_sensitive_info(self, text: str) -> str:
        """
        Redact sensitive information from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text with summary
        """
        try:
            console.print("[cyan]Redacting sensitive information[/cyan]")
            
            result = self.redaction_tool.redact_sensitive_info(text)
            
            self.tracker.log_tool_call(
                "redactor",
                "redact_sensitive",
                {},
                f"Redacted {len(result['redacted_items'])} items"
            )
            
            summary = [
                f"Redacted {len(result['redacted_items'])} sensitive items:",
                ""
            ]
            
            for item in result['redacted_items']:
                summary.append(f"  • {item}")
            
            summary.append(f"\nRedacted Text:\n{result['redacted_text']}")
            
            return "\n".join(summary)
            
        except Exception as e:
            console.print(f"[red]Error redacting: {e}[/red]")
            return text
    
    def create_bullet_summary(self, text: str) -> str:
        """
        Create a bullet-point summary.
        
        Args:
            text: Text to summarize
            
        Returns:
            Bullet-point summary
        """
        try:
            console.print("[cyan]Creating bullet-point summary[/cyan]")
            
            prompt = f"""Create a concise bullet-point summary of the following text. 
Use clear, actionable bullet points (5-10 points).

Text:
{text[:2000]}

Bullet Summary:"""
            
            summary = self.ollama_client.generate(prompt)
            
            return summary
            
        except Exception as e:
            console.print(f"[red]Error creating bullet summary: {e}[/red]")
            return f"Error: {str(e)}"

