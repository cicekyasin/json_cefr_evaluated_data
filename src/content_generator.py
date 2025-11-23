import os
import json
import time
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_passage(topic: str, level: str, target_vocab: List[str]) -> str:
    """Generates a reading passage using Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
         return f"This is a mock passage about {topic} at level {level}. It includes words like {', '.join(target_vocab)}. (Mock data generated because API key is missing)"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Write a 150-word reading passage about "{topic}" suited for CEFR level {level}.
        You MUST include the following target vocabulary words in the text: {', '.join(target_vocab)}.
        Highlight the target vocabulary words by wrapping them in **double asterisks** (e.g., **word**).
        The text should be engaging and educational.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content for {topic}: {e}")
        return f"Error generating passage for {topic}. (Mock fallback)"

def main():
    input_path = "data/curriculum_plan.json"
    output_path = "data/english_cefr_dataset.jsonl"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Please run curriculum_design.py first.")
        return

    print("Loading curriculum plan...")
    with open(input_path, "r") as f:
        data = json.load(f)
        lessons = data.get("lessons", [])

    print(f"Found {len(lessons)} lessons. Generating content...")

    with open(output_path, "w") as outfile:
        for i, lesson in enumerate(lessons):
            topic = lesson["topic"]
            level = lesson["level"]
            vocab = lesson["target_vocabulary"]

            print(f"[{i+1}/{len(lessons)}] Generating content for: {topic} ({level})")

            passage = generate_passage(topic, level, vocab)

            # Format for fine-tuning (messages format)
            # This is a common format for instruction tuning
            messages_entry = {
                "messages": [
                    {"role": "system", "content": f"You are an expert English teacher creating reading materials for CEFR level {level}."},
                    {"role": "user", "content": f"Write a passage about {topic} including these words: {', '.join(vocab)}."},
                    {"role": "assistant", "content": passage}
                ],
                "metadata": {
                    "topic": topic,
                    "level": level,
                    "target_vocabulary": vocab
                }
            }

            outfile.write(json.dumps(messages_entry) + "\n")

            # Respect rate limits if using real API (simple sleep)
            if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_API_KEY") != "your_api_key_here":
                time.sleep(1)

    print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    main()
