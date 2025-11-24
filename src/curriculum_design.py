import os
import json
import random
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from src.utils import get_available_model

# Load environment variables
load_dotenv()

# Define Pydantic models
class LessonPlan(BaseModel):
    topic: str = Field(..., description="The topic of the lesson")
    level: Literal["B1", "B2", "C1"] = Field(..., description="The CEFR level of the lesson")
    target_vocabulary: List[str] = Field(..., description="List of 5-10 target vocabulary words suitable for the level")

class Curriculum(BaseModel):
    lessons: List[LessonPlan]

def generate_curriculum(num_lessons: int = 50) -> Curriculum:
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("Warning: GOOGLE_API_KEY not found or invalid. Using mock data.")
        return generate_mock_curriculum(num_lessons)

    try:
        # Use dynamic model selection
        model_name = get_available_model(api_key)
        print(f"Using model for curriculum design: {model_name}")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        Generate a curriculum plan with {num_lessons} unique English lesson topics.
        The topics should be a mix of CEFR levels B1, B2, and C1.
        For each lesson, provide a topic name, the CEFR level, and a list of 5-10 target vocabulary words.
        Ensure the output conforms to the specified JSON schema.
        """

        result = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=Curriculum
            )
        )

        return Curriculum.model_validate_json(result.text)

    except Exception as e:
        print(f"Error generating curriculum with API: {e}. Falling back to mock data.")
        return generate_mock_curriculum(num_lessons)

def generate_mock_curriculum(num_lessons: int) -> Curriculum:
    levels = ["B1", "B2", "C1"]
    topics = [
        "Technology and Society", "Environmental Issues", "Travel and Culture",
        "Health and Wellness", "Business and Economy", "Art and Literature",
        "Science and Innovation", "Education Trends", "History and Mystery",
        "Food and Nutrition"
    ]

    lessons = []
    for i in range(num_lessons):
        level = random.choice(levels)
        topic = f"{random.choice(topics)} - {i+1}"
        vocab = [f"word_{j}_{i}" for j in range(5)] # Dummy vocab
        lessons.append(LessonPlan(topic=topic, level=level, target_vocabulary=vocab))

    return Curriculum(lessons=lessons)

def main():
    print("Generating curriculum plan...")
    curriculum = generate_curriculum(50)

    output_path = "data/curriculum_plan.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(curriculum.model_dump_json(indent=2))

    print(f"Curriculum plan saved to {output_path}")

if __name__ == "__main__":
    main()
