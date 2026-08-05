import sys
import os

# Ensure the backend directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.modules.chat.agent import graph

try:
    png_data = graph.get_graph().draw_mermaid_png()
    with open("a:\\Projects\\Trendly\\langgraph.png", "wb") as f:
        f.write(png_data)
    print("Graph successfully saved to langgraph.png!")
except Exception as e:
    print(f"Could not generate PNG: {e}")
