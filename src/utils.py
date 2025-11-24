import google.generativeai as genai
import time

def get_available_model(api_key: str) -> str:
    """
    Queries the API to find the best available model.
    Prioritizes: gemini-2.5-flash > gemini-1.5-flash > gemini-pro
    """
    if not api_key or api_key == "your_api_key_here":
        # Default fallback for mock mode
        return "gemini-1.5-flash"

    try:
        genai.configure(api_key=api_key)

        # List models - this helps check what's actually available to the key
        # However, list_models returns an iterator of Model objects.
        # We will just check the names explicitly or iterate.
        available_models = [m.name for m in genai.list_models()]

        # Normalize names (sometimes they come as 'models/gemini-pro')
        available_models = [m.replace("models/", "") for m in available_models]

        priorities = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]

        for model in priorities:
            if model in available_models:
                print(f"Selected model: {model}")
                return model

        # Fallback if none of the specific ones are found (unlikely)
        # Just return the first priority to try anyway, or a safe default
        print(f"Warning: Preferred models not found in list. Defaulting to {priorities[1]}.")
        return priorities[1]

    except Exception as e:
        print(f"Error selecting model: {e}. Defaulting to gemini-1.5-flash.")
        return "gemini-1.5-flash"
