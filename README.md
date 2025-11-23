# Constraint-Satisfaction Synthetic Data Pipeline

This project implements a pipeline to generate synthetic English reading materials based on CEFR constraints using the Google Gemini API. The pipeline is designed to create high-quality datasets for fine-tuning NLP models, specifically ensuring that generated content adheres to specific vocabulary and complexity levels.

## Project Structure

- `src/curriculum_design.py`: Generates a lesson plan with topics, CEFR levels, and target vocabulary.
- `src/content_generator.py`: Consumes the lesson plan and generates reading passages using the Gemini API.
- `main.py`: Orchestrates the entire pipeline.
- `data/`: Stores generated artifacts (`curriculum_plan.json` and `english_cefr_dataset.jsonl`).
- `.github/workflows/`: Contains CI/CD automation.

## Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment:**
    Copy `.env.example` to `.env` and set your `GOOGLE_API_KEY`.
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your key:
    ```
    GOOGLE_API_KEY=your_actual_api_key
    ```

## Usage

To run the full pipeline:

```bash
python main.py
```

This will:
1.  Check for the API key.
2.  Generate a curriculum of 50 lessons (saved to `data/curriculum_plan.json`).
3.  Generate reading passages for each lesson (saved to `data/english_cefr_dataset.jsonl`).

## Output Format

The final output `data/english_cefr_dataset.jsonl` is in a chat-completion format suitable for fine-tuning:

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "metadata": { ... }
}
```

## Automation

A GitHub Actions workflow (`.github/workflows/daily_generation.yml`) is configured to run this pipeline daily at midnight. It requires the `GOOGLE_API_KEY` to be set as a GitHub Secret.
