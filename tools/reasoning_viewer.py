#!/usr/bin/env python3
"""
HAWK-AI Reasoning Chain Viewer
Displays each thinking step and its reasoning chain in console or Streamlit.
"""

import json
import os
import argparse

DATA_PATH = "data/analysis/last_reasoning.json"


def show_reasoning_cli():
    """Display reasoning chain in CLI with formatted output."""
    if not os.path.exists(DATA_PATH):
        print("❌ No reasoning file found.")
        print(f"   Expected: {os.path.abspath(DATA_PATH)}")
        return
    
    try:
        with open(DATA_PATH, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"\n🧠 HAWK-AI Reasoning Chain for: {data.get('query', 'Unknown Query')}")
    print("=" * 70)
    
    reasoning_steps = ["patterns", "hypotheses", "evaluation", "synthesis", "review"]
    
    for step in reasoning_steps:
        step_data = data.get(step, "")
        print(f"\n🔹 {step.upper()}")
        print("-" * 70)
        
        if isinstance(step_data, str):
            # Truncate long text for readability
            truncated = step_data[:1200]
            if len(step_data) > 1200:
                truncated += "\n... [truncated]"
            print(truncated)
        elif isinstance(step_data, (dict, list)):
            print(json.dumps(step_data, indent=2)[:1200])
        else:
            print(step_data)
        
        print("-" * 70)
    
    runtime = data.get('runtime_s', '?')
    print(f"\n⏱️  Total reasoning time: {runtime}s")
    print(f"📊 Model: {data.get('model', 'Unknown')}")
    print(f"📅 Timestamp: {data.get('timestamp', 'Unknown')}\n")


def show_reasoning_streamlit():
    """Display reasoning chain in Streamlit UI."""
    try:
        import streamlit as st
    except ImportError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
        return
    
    st.set_page_config(
        page_title="HAWK-AI Reasoning Viewer",
        page_icon="🧠",
        layout="wide"
    )
    
    if not os.path.exists(DATA_PATH):
        st.error(f"❌ No reasoning file found at: {os.path.abspath(DATA_PATH)}")
        st.info("Run a HAWK-AI analysis to generate reasoning data.")
        return
    
    try:
        with open(DATA_PATH, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing JSON: {e}")
        return
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return
    
    # Header
    st.title(f"🧠 HAWK-AI Reasoning Chain")
    st.markdown(f"**Query:** {data.get('query', 'Unknown Query')}")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Runtime", f"{data.get('runtime_s', '?')}s")
    with col2:
        st.metric("Model", data.get('model', 'Unknown'))
    with col3:
        st.metric("Timestamp", data.get('timestamp', 'Unknown'))
    
    st.divider()
    
    # Reasoning steps
    reasoning_steps = [
        ("patterns", "🔍 Pattern Recognition", "Identified patterns in the data"),
        ("hypotheses", "💡 Hypothesis Formation", "Generated hypotheses from patterns"),
        ("evaluation", "⚖️ Evaluation", "Evaluated hypotheses against evidence"),
        ("synthesis", "🔗 Synthesis", "Synthesized findings into coherent analysis"),
        ("review", "✅ Review", "Final review and quality check")
    ]
    
    for step_key, step_title, step_desc in reasoning_steps:
        with st.expander(step_title, expanded=True):
            st.caption(step_desc)
            step_data = data.get(step_key, "No data available")
            
            if isinstance(step_data, str):
                st.text_area(
                    label=f"{step_key}_content",
                    value=step_data,
                    height=200,
                    label_visibility="collapsed"
                )
            elif isinstance(step_data, (dict, list)):
                st.json(step_data)
            else:
                st.write(step_data)
    
    # Footer
    st.divider()
    st.success(f"✅ Reasoning chain completed in {data.get('runtime_s', '?')}s")
    
    # Export option
    if st.button("📥 Download Reasoning JSON"):
        st.download_button(
            label="Download",
            data=json.dumps(data, indent=2),
            file_name="hawk_ai_reasoning.json",
            mime="application/json"
        )


def main():
    """Main entry point with argument parsing."""
    global DATA_PATH
    
    parser = argparse.ArgumentParser(
        description="HAWK-AI Reasoning Chain Viewer - Display reasoning steps in CLI or Streamlit"
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "streamlit"],
        default="cli",
        help="Display mode: 'cli' for terminal output, 'streamlit' for web UI"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help=f"Path to reasoning JSON file (default: {DATA_PATH})"
    )
    
    args = parser.parse_args()
    
    # Override default data path if provided
    if args.data_path:
        DATA_PATH = args.data_path
    
    if args.mode == "streamlit":
        try:
            import streamlit.web.cli as stcli
            import sys
            
            # Get the absolute path to this script
            script_path = os.path.abspath(__file__)
            
            # Run streamlit with this script
            sys.argv = ["streamlit", "run", script_path]
            sys.exit(stcli.main())
            
        except ImportError:
            print("❌ Streamlit not installed. Install with: pip install streamlit")
            print("   Falling back to CLI mode...")
            show_reasoning_cli()
    else:
        show_reasoning_cli()


if __name__ == "__main__":
    # When called from streamlit, show the UI
    # When called normally, parse args
    import sys
    
    if "streamlit" in sys.modules:
        # Running inside Streamlit
        show_reasoning_streamlit()
    else:
        # Running from command line
        main()

