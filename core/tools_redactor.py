"""
Redaction and text summarization tools for HAWK-AI.
Provides text rewriting, summarization, and filtering capabilities.
"""
from typing import Dict, Any, Optional
import yaml
from rich.console import Console

console = Console()


class RedactionTool:
    """Tool for text redaction and summarization."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize redaction tool."""
        self.config = self._load_config(config_path)
        self.max_tokens = self.config['redaction']['max_tokens']
        self.style = self.config['redaction']['style']
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def summarize(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Summarize text to a shorter version.
        
        Args:
            text: Text to summarize
            max_length: Maximum length in characters
            
        Returns:
            Summarized text
        """
        if max_length is None:
            max_length = self.max_tokens * 4  # Rough estimate
        
        if len(text) <= max_length:
            return text
        
        # Simple truncation with ellipsis
        # In a real implementation, this would use the LLM
        console.print(f"[cyan]Truncating text from {len(text)} to {max_length} chars[/cyan]")
        return text[:max_length] + "..."
    
    def extract_key_points(self, text: str, num_points: int = 5) -> list[str]:
        """
        Extract key points from text.
        
        Args:
            text: Text to analyze
            num_points: Number of key points to extract
            
        Returns:
            List of key points
        """
        console.print(f"[cyan]Extracting {num_points} key points...[/cyan]")
        
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        # Return first N sentences as key points (simple implementation)
        # In a real implementation, this would use NLP or LLM
        return sentences[:num_points]
    
    def rewrite_style(self, text: str, style: Optional[str] = None) -> str:
        """
        Rewrite text in a specific style.
        
        Args:
            text: Text to rewrite
            style: Target style (professional, casual, technical, etc.)
            
        Returns:
            Rewritten text
        """
        if style is None:
            style = self.style
        
        console.print(f"[cyan]Rewriting text in {style} style...[/cyan]")
        
        # This is a placeholder - in reality, this would use the LLM
        return text
    
    def redact_sensitive_info(self, text: str) -> Dict[str, Any]:
        """
        Redact potentially sensitive information from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Dictionary with redacted text and list of redacted items
        """
        console.print("[cyan]Redacting sensitive information...[/cyan]")
        
        redacted_items = []
        redacted_text = text
        
        # Simple patterns for sensitive data
        import re
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            redacted_text = redacted_text.replace(email, '[EMAIL_REDACTED]')
            redacted_items.append(f"Email: {email}")
        
        # Phone numbers (simple pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            redacted_text = redacted_text.replace(phone, '[PHONE_REDACTED]')
            redacted_items.append(f"Phone: {phone}")
        
        console.print(f"[green]Redacted {len(redacted_items)} items[/green]")
        
        return {
            "redacted_text": redacted_text,
            "redacted_items": redacted_items,
            "original_length": len(text),
            "redacted_length": len(redacted_text)
        }
    
    def create_executive_summary(self, text: str, max_paragraphs: int = 3) -> str:
        """
        Create an executive summary of the text.
        
        Args:
            text: Text to summarize
            max_paragraphs: Maximum number of paragraphs in summary
            
        Returns:
            Executive summary
        """
        console.print(f"[cyan]Creating executive summary ({max_paragraphs} paragraphs)...[/cyan]")
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        
        # Return first N paragraphs (simple implementation)
        # In a real implementation, this would use LLM for intelligent summarization
        summary_paragraphs = paragraphs[:max_paragraphs]
        
        return '\n\n'.join(summary_paragraphs)
    
    def format_as_report(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Format content as a structured report.
        
        Args:
            title: Report title
            content: Report content
            metadata: Optional metadata to include
            
        Returns:
            Formatted report
        """
        console.print("[cyan]Formatting report...[/cyan]")
        
        report_parts = [
            "=" * 80,
            f"{title.center(80)}",
            "=" * 80,
            ""
        ]
        
        if metadata:
            report_parts.append("METADATA:")
            for key, value in metadata.items():
                report_parts.append(f"  {key}: {value}")
            report_parts.append("")
        
        report_parts.append("CONTENT:")
        report_parts.append("-" * 80)
        report_parts.append(content)
        report_parts.append("")
        report_parts.append("=" * 80)
        
        return "\n".join(report_parts)


def get_redaction_tool(config_path: str = "config/settings.yaml") -> RedactionTool:
    """Get redaction tool instance."""
    return RedactionTool(config_path)

