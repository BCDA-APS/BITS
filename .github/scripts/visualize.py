"""
nuanced graph
"""

from pathlib import Path

from nuanced import CodeGraph

# Set path relative to the script location
base_path = Path(__file__).resolve().parent.parent.parent / "src"

# Initialize the graph for the entire src directory
graph = CodeGraph.init(str(base_path))

#


# Integrate into your development workflow
def pre_commit_analysis():
    """
    Generate fresh call graph before committing
    """
    graph = CodeGraph.init(str(base_path))
    # Perform additional checks or logging
    return graph
