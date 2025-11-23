import gradio as gr
import pandas as pd
import json
import os

# --- CONFIGURATION ---
DATA_FILE = "data/english_cefr_dataset.jsonl"
# If you eventually upload this to Hugging Face Datasets, you can use:
# DATASET_NAME = "your-username/English-CEFR-Instruction-Tuning-Benchmark"
# and switch to loading from hub.

def load_data():
    """
    Loads the locally generated JSONL dataset.
    """
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame({"Error": [f"File not found: {DATA_FILE}. Run the pipeline first."]})

    try:
        # Load local JSONL file
        df = pd.read_json(DATA_FILE, lines=True)

        # Flatten the metadata structure
        # My data schema: metadata -> {topic, level, target_vocabulary}
        df["Level"] = df["metadata"].apply(lambda x: x.get("level", "N/A"))
        df["Topic"] = df["metadata"].apply(lambda x: x.get("topic", "N/A"))

        # Extract vocabulary list
        df["Vocabulary"] = df["metadata"].apply(lambda x: ", ".join(x.get("target_vocabulary", [])))

        # Extract the Assistant's response (Generated Text)
        def get_assistant_content(messages):
            for m in messages:
                if m.get("role") == "assistant":
                    return m.get("content", "")
            return "Error: No assistant content found"

        df["Generated_Text"] = df["messages"].apply(get_assistant_content)

        # Create a display ID
        df["id"] = df.index

        return df
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not load dataset: {str(e)}"]})

# Load data once at startup
df = load_data()

# --- THE AUDIT FUNCTION ---
def inspect_sample(evt: gr.SelectData):
    """
    When a user clicks a row in the table, show the deep details.
    """
    if "Error" in df.columns:
        return "Error loading data."

    try:
        row_index = evt.index[0]
        row = df.iloc[row_index]

        # Text for display
        audit_report = f"""
        ### 🎯 Level: {row['Level']} | Topic: {row['Topic']}

        **✅ Required Vocabulary:**
        {row['Vocabulary']}

        **📝 Generated Text:**
        {row['Generated_Text']}
        """
        return audit_report
    except Exception as e:
        return f"Error inspecting row: {e}"

# --- BUILD THE APP UI ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🇬🇧 English CEFR Benchmark Explorer")
    gr.Markdown(f"Viewing locally generated dataset: `{DATA_FILE}`. Click a row to audit the constraints.")

    with gr.Row():
        # Left side: The Big Data Table
        with gr.Column(scale=2):
            if "Error" in df.columns:
                 gr.Markdown(f"**Error:** {df['Error'][0]}")
                 table = gr.Dataframe() # Empty
            else:
                table = gr.Dataframe(
                    value=df[["id", "Level", "Topic", "Generated_Text"]],
                    headers=["ID", "Level", "Topic", "Preview"],
                    interactive=False,
                    wrap=True,
                    height=600
                )

        # Right side: The Inspector Panel
        with gr.Column(scale=1):
            gr.Markdown("## 🕵️ Constraint Auditor")
            audit_view = gr.Markdown("Select a row to see details...")

    # Connect the click event
    if "Error" not in df.columns:
        table.select(fn=inspect_sample, outputs=audit_view)

# Launch
if __name__ == "__main__":
    demo.launch()
