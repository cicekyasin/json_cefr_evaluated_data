import os
import json
import time
import difflib
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_too_similar(new_text: str, existing_texts: List[str], threshold: float = 0.6) -> bool:
    """
    Checks if new_text is too similar to any text in existing_texts.
    Returns True if similarity ratio > threshold.
    """
    for text in existing_texts:
        # Quick length check optimization: if lengths differ vastly, they aren't similar
        if abs(len(new_text) - len(text)) / max(len(new_text), len(text)) > 0.5:
             continue

        similarity = difflib.SequenceMatcher(None, new_text, text).ratio()
        if similarity > threshold:
            return True
    return False

def generate_passage(topic: str, level: str, target_vocab: List[str]) -> Optional[str]:
    """Generates a reading passage using Gemini API with specific creativity settings."""
    api_key = os.getenv("GOOGLE_API_KEY")

    # Mock behavior
    if not api_key or api_key == "your_api_key_here":
         # Return a semi-random string to allow testing diversity check if we were to loop multiple times
         # timestamp included to make it unique by default
         return f"This is a mock passage about {topic} at level {level}. It includes words like {', '.join(target_vocab)}. Timestamp: {time.time()} (Mock data generated because API key is missing)"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        Write a 150-word reading passage about "{topic}" suited for CEFR level {level}.
        You MUST include the following target vocabulary words in the text: {', '.join(target_vocab)}.
        Highlight the target vocabulary words by wrapping them in **double asterisks** (e.g., **word**).
        The text should be engaging and educational.
        """

        # Updated config for higher creativity
        generation_config = genai.GenerationConfig(
            temperature=0.85,
            top_p=0.95
        )

        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        print(f"Error generating content for {topic}: {e}")
        return None

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

    generated_passages = []

    with open(output_path, "w") as outfile:
        for i, lesson in enumerate(lessons):
            topic = lesson["topic"]
            level = lesson["level"]
            vocab = lesson["target_vocabulary"]

            print(f"[{i+1}/{len(lessons)}] Processing: {topic} ({level})")

            passage = None
            max_retries = 3

            for attempt in range(max_retries):
                candidate_passage = generate_passage(topic, level, vocab)

                if candidate_passage is None:
                    # API error, maybe retry? For now let's just break to next attempt
                    continue

                if is_too_similar(candidate_passage, generated_passages):
                    print(f"  [Warning] Attempt {attempt+1}/{max_retries}: Passage for '{topic}' rejected due to high similarity (> 0.6). Retrying...")
                    continue
                else:
                    passage = candidate_passage
                    break

            if passage:
                generated_passages.append(passage)

                # Format for fine-tuning (messages format)
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
                outfile.flush() # Ensure it writes to disk

                # Respect rate limits if using real API
                if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_API_KEY") != "your_api_key_here":
                    time.sleep(1)
            else:
                print(f"  [Error] Failed to generate unique content for '{topic}' after {max_retries} attempts. Skipping.")

    print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    main()
