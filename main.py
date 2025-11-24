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

def run_module(module_name):
    print(f"\n--- Running module {module_name} ---")
    # Execute using -m to preserve package structure and imports
    cmd = [sys.executable, "-m", module_name]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {module_name}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Synthetic Data Generation Pipeline")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without API key")
    args = parser.parse_args()

    print("Starting Synthetic Data Generation Pipeline...")

    if not check_env(args.mock):
        sys.exit(1)

    # Step 1: Curriculum Design
    run_module("src.curriculum_design")

    # Step 2: Content Generation
    run_module("src.content_generator")

    print("\nPipeline completed successfully!")
    print("Output available in data/english_cefr_dataset.jsonl")

if __name__ == "__main__":
    main()
