import os
import json
import time
import difflib
from typing import List, Dict, Any, Optional, Set
import google.generativeai as genai
from dotenv import load_dotenv
from src.utils import get_available_model

# Load environment variables
load_dotenv()

def is_too_similar(new_text: str, existing_texts: List[str], threshold: float = 0.6) -> bool:
    """
    Checks if new_text is too similar to any text in existing_texts.
    Returns True if similarity ratio > threshold.
    """
    for text in existing_texts:
        # Quick length check optimization
        if abs(len(new_text) - len(text)) / max(len(new_text), len(text)) > 0.5:
             continue

        similarity = difflib.SequenceMatcher(None, new_text, text).ratio()
        if similarity > threshold:
            return True
    return False

def load_existing_topics(output_path: str) -> Set[str]:
    """Loads already generated topics from the output file to enable Smart Resume."""
    topics = set()
    if os.path.exists(output_path):
        try:
            with open(output_path, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # Check metadata for topic
                        if "metadata" in entry and "topic" in entry["metadata"]:
                            topics.add(entry["metadata"]["topic"])
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Warning: Could not read existing file for Smart Resume: {e}")
    return topics

def generate_passage(topic: str, level: str, target_vocab: List[str], model_name: str) -> Optional[str]:
    """Generates a reading passage using Gemini API with specific creativity settings."""
    api_key = os.getenv("GOOGLE_API_KEY")

    # Mock behavior
    if not api_key or api_key == "your_api_key_here":
         return f"This is a mock passage about {topic} at level {level}. It includes words like {', '.join(target_vocab)}. Timestamp: {time.time()} (Mock data generated because API key is missing)"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        Write a 150-word reading passage about "{topic}" suited for CEFR level {level}.
        You MUST include the following target vocabulary words in the text: {', '.join(target_vocab)}.
        Highlight the target vocabulary words by wrapping them in **double asterisks** (e.g., **word**).
        The text should be engaging and educational.
        """

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

    # Smart Resume: Load existing topics
    existing_topics = load_existing_topics(output_path)
    print(f"Found {len(existing_topics)} already generated topics.")

    # Filter lessons
    lessons_to_process = [l for l in lessons if l["topic"] not in existing_topics]
    print(f"Remaining lessons to process: {len(lessons_to_process)}")

    if not lessons_to_process:
        print("All lessons completed. Exiting.")
        return

    # Determine model once
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = get_available_model(api_key)
    print(f"Using model: {model_name}")

    # Load existing texts for similarity check (only if we are appending, we should check against ALL previous texts)
    # Note: In a very large dataset, loading all texts into memory for similarity check might become slow.
    # For now, we assume the dataset fits in memory.
    generated_passages = []
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    # Extract assistant content
                    messages = entry.get("messages", [])
                    if len(messages) > 2:
                        generated_passages.append(messages[2]["content"])
                except:
                    pass

    # Open in APPEND mode
    with open(output_path, "a") as outfile:
        for i, lesson in enumerate(lessons_to_process):
            topic = lesson["topic"]
            level = lesson["level"]
            vocab = lesson["target_vocabulary"]

            print(f"[{i+1}/{len(lessons_to_process)}] Processing: {topic} ({level})")

            passage = None
            max_retries = 3

            for attempt in range(max_retries):
                candidate_passage = generate_passage(topic, level, vocab, model_name)

                if candidate_passage is None:
                    continue

                if is_too_similar(candidate_passage, generated_passages):
                    print(f"  [Warning] Attempt {attempt+1}/{max_retries}: Passage for '{topic}' rejected due to high similarity (> 0.6). Retrying...")
                    continue
                else:
                    passage = candidate_passage
                    break

            if passage:
                generated_passages.append(passage)

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
                outfile.flush()

                # Rate limiting: Sleep 10 seconds
                if api_key and api_key != "your_api_key_here":
                    time.sleep(10)
            else:
                print(f"  [Error] Failed to generate unique content for '{topic}' after {max_retries} attempts. Skipping.")

    print(f"Dataset updated at {output_path}")

if __name__ == "__main__":
    main()
