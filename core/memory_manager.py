"""
Memory Manager for HAWK-AI
===========================
Manages persistent shared memory for inter-agent collaboration and historical reasoning.

Stores:
- Last queries
- Agents invoked
- Their outputs
- Reflections

Usage:
    from core.memory_manager import append_entry
    
    append_entry({
        "query": "Conflict escalation in Sudan",
        "agents": ["analyst", "geo"],
        "confidence": 0.88
    })

CLI:
    python core/memory_manager.py --show
    → prints last 3 memory entries with timestamps
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Memory file path
MEMORY_PATH = "data/memory/agent_memory.json"


def load_memory() -> List[Dict[str, Any]]:
    """
    Load memory from the JSON file.
    
    Returns:
        List of memory entries. Empty list if file doesn't exist.
    """
    if not os.path.exists(MEMORY_PATH):
        logger.info(f"Memory file not found at {MEMORY_PATH}, returning empty memory")
        return []
    
    try:
        with open(MEMORY_PATH, "r") as f:
            memory = json.load(f)
            logger.debug(f"Loaded {len(memory)} memory entries")
            return memory
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode memory file: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading memory: {e}")
        return []


def save_memory(memory: List[Dict[str, Any]]) -> bool:
    """
    Save memory to the JSON file.
    
    Args:
        memory: List of memory entries to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
        with open(MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)
        logger.debug(f"Saved {len(memory)} memory entries")
        return True
    except Exception as e:
        logger.error(f"Error saving memory: {e}")
        return False


def append_entry(entry: dict) -> bool:
    """
    Append a new entry to the memory log.
    
    Args:
        entry: Dictionary containing memory entry data
               Expected fields: query, agents, outputs (optional), 
                              reflection (optional), confidence (optional)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        mem = load_memory()
        entry["timestamp"] = datetime.utcnow().isoformat()
        mem.append(entry)
        
        if save_memory(mem):
            query = entry.get('query', 'N/A')
            logger.info(f"Added memory entry: {query}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error appending entry: {e}")
        return False


def get_recent_entries(count: int = 3) -> List[Dict[str, Any]]:
    """
    Get the most recent memory entries.
    
    Args:
        count: Number of recent entries to retrieve (default: 3)
        
    Returns:
        List of recent memory entries
    """
    memory = load_memory()
    return memory[-count:] if len(memory) >= count else memory


def search_memory(
    query_text: Optional[str] = None,
    agent_name: Optional[str] = None,
    min_confidence: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search memory entries based on criteria.
    
    Args:
        query_text: Filter by query text (substring match, case-insensitive)
        agent_name: Filter by agent name
        min_confidence: Filter by minimum confidence score
        
    Returns:
        List of matching memory entries
    """
    memory = load_memory()
    results = memory
    
    if query_text:
        results = [
            entry for entry in results
            if query_text.lower() in entry.get('query', '').lower()
        ]
    
    if agent_name:
        results = [
            entry for entry in results
            if agent_name in entry.get('agents', [])
        ]
    
    if min_confidence is not None:
        results = [
            entry for entry in results
            if entry.get('confidence', 0) >= min_confidence
        ]
    
    return results


def clear_memory() -> bool:
    """
    Clear all memory entries.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        return save_memory([])
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        return False


def get_memory_stats() -> Dict[str, Any]:
    """
    Get statistics about the memory log.
    
    Returns:
        Dictionary with memory statistics
    """
    memory = load_memory()
    
    if not memory:
        return {
            "total_entries": 0,
            "agents_used": [],
            "avg_confidence": 0,
            "date_range": None
        }
    
    # Collect all agents
    all_agents = set()
    confidences = []
    timestamps = []
    
    for entry in memory:
        all_agents.update(entry.get('agents', []))
        if 'confidence' in entry:
            confidences.append(entry['confidence'])
        if 'timestamp' in entry:
            timestamps.append(entry['timestamp'])
    
    stats = {
        "total_entries": len(memory),
        "agents_used": sorted(list(all_agents)),
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
        "date_range": {
            "first": min(timestamps) if timestamps else None,
            "last": max(timestamps) if timestamps else None
        }
    }
    
    return stats


def print_memory_entries(entries: List[Dict[str, Any]], verbose: bool = False):
    """
    Pretty print memory entries.
    
    Args:
        entries: List of memory entries to print
        verbose: If True, print full details including outputs
    """
    if not entries:
        print("No memory entries found.")
        return
    
    print(f"\n{'='*80}")
    print(f"Memory Entries ({len(entries)} total)")
    print(f"{'='*80}\n")
    
    for i, entry in enumerate(entries, 1):
        timestamp = entry.get('timestamp', 'N/A')
        query = entry.get('query', 'N/A')
        agents = ', '.join(entry.get('agents', []))
        confidence = entry.get('confidence', 'N/A')
        
        print(f"[{i}] {timestamp}")
        print(f"    Query: {query}")
        print(f"    Agents: {agents}")
        print(f"    Confidence: {confidence}")
        
        if verbose:
            if 'outputs' in entry:
                print(f"    Outputs: {entry['outputs']}")
            if 'reflection' in entry:
                print(f"    Reflection: {entry['reflection']}")
        
        print()


def main():
    """CLI interface for memory manager."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='HAWK-AI Memory Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python core/memory_manager.py --show
  python core/memory_manager.py --show --count 5
  python core/memory_manager.py --stats
  python core/memory_manager.py --search "Sudan"
  python core/memory_manager.py --search-agent analyst
  python core/memory_manager.py --clear
        """
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show recent memory entries'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of recent entries to show (default: 3)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show full entry details including outputs'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show memory statistics'
    )
    parser.add_argument(
        '--search',
        type=str,
        help='Search memory by query text'
    )
    parser.add_argument(
        '--search-agent',
        type=str,
        help='Search memory by agent name'
    )
    parser.add_argument(
        '--min-confidence',
        type=float,
        help='Filter by minimum confidence score'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all memory entries (use with caution!)'
    )
    
    args = parser.parse_args()
    
    # Handle clear command
    if args.clear:
        confirm = input("Are you sure you want to clear all memory? (yes/no): ")
        if confirm.lower() == 'yes':
            if clear_memory():
                print("Memory cleared successfully.")
            else:
                print("Failed to clear memory.")
        else:
            print("Clear operation cancelled.")
        return
    
    # Handle stats command
    if args.stats:
        stats = get_memory_stats()
        print(f"\n{'='*80}")
        print("Memory Statistics")
        print(f"{'='*80}")
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Agents Used: {', '.join(stats['agents_used']) if stats['agents_used'] else 'None'}")
        print(f"Average Confidence: {stats['avg_confidence']:.2f}")
        if stats['date_range']:
            print(f"Date Range: {stats['date_range']['first']} to {stats['date_range']['last']}")
        print()
        return
    
    # Handle search commands
    if args.search or args.search_agent or args.min_confidence:
        results = search_memory(
            query_text=args.search,
            agent_name=args.search_agent,
            min_confidence=args.min_confidence
        )
        print_memory_entries(results, verbose=args.verbose)
        return
    
    # Default: show recent entries
    if args.show or True:  # Default behavior
        entries = get_recent_entries(args.count)
        print_memory_entries(entries, verbose=args.verbose)


if __name__ == "__main__":
    main()

