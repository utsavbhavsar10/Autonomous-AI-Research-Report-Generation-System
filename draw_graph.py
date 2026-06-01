from app.graph.workflow import workflow

print("Generating workflow.png...")
# This uses the public mermaid API, so you must have an internet connection
png_data = workflow.get_graph().draw_mermaid_png()

with open("workflow.png", "wb") as f:
    f.write(png_data)
    
print("Done! Open workflow.png in VS Code to view.")