import os
import subprocess
import sys
import argparse
from dotenv import load_dotenv

def check_env(mock_mode=False):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        if mock_mode:
            print("Warning: GOOGLE_API_KEY not found. Running in MOCK mode.")
            return True
        else:
            print("Error: GOOGLE_API_KEY environment variable is not set.")
            print("Please set GOOGLE_API_KEY or run with --mock to generate dummy data.")
            return False

    if api_key == "your_api_key_here":
        if mock_mode:
             print("Warning: Using placeholder key in MOCK mode.")
             return True
        else:
             print("Error: GOOGLE_API_KEY is set to the example value.")
             print("Please set a real API key or run with --mock.")
             return False

    return True

def run_script(script_path, mock_mode=False):
    print(f"\n--- Running {script_path} ---")
    cmd = [sys.executable, script_path]
    # If we implement passing arguments to the scripts, we would add them here.
    # For now, the scripts check the environment variable themselves.
    # However, to be consistent, we should probably let the scripts know they should be mocking if needed,
    # or rely on the fact that if the key is missing/invalid, they mock.
    # But since we are enforcing the check here, we can just run them.

    # Actually, the sub-scripts (curriculum_design.py and content_generator.py) currently auto-mock
    # if the key is missing/invalid. This behavior is fine, but we want to control it from main.

    # Let's trust the check_env function to gatekeep.

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generation Pipeline")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API key")
    args = parser.parse_args()

    print("Starting Synthetic Data Generation Pipeline...")

    if not check_env(args.mock):
        sys.exit(1)

    # Step 1: Curriculum Design
    run_script("src/curriculum_design.py")

    # Step 2: Content Generation
    run_script("src/content_generator.py")

    print("\nPipeline completed successfully!")
    print("Output available in data/english_cefr_dataset.jsonl")

if __name__ == "__main__":
    main()
