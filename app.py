import os
import json
import time
import schedule
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import google.generativeai as genai  # Using Google PaLM
from google import genai
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load API Key
# genai.configure(api_key=os.getenv("GOOGLE_PALM_API_KEY"))
client = genai.Client(api_key="AIzaSyCBZq7zmsqFKj-63hYTmpGHympTQIGFlXc")
# Path to the QMD file
QMD_FILE_PATH = "passives.qmd"
# Path to store generated questions
JSON_FILE_PATH = "questions.json"

# Maintain in system memeory to reduce regular write operation
questions_cache = {
    "easy": [],
    "medium": [],
    "hard": []
}

# Function to read QMD file
def read_qmd_file():
    with open(QMD_FILE_PATH, "r", encoding="utf-8") as file:
        return file.read()

# Function to generate questions using AI
# def generate_questions():
#     qmd_content = read_qmd_file()

#     prompt = f"""
#     Generate quiz questions based on the following content:
#     {qmd_content}

#     Provide questions in JSON format with fields: "question", "options", "correctAnswer", and "level" (easy, medium, hard).
#     """
    
#     response = genai.chat(model="models/text-bison-001", messages=[{"role": "user", "content": prompt}])
#     ai_output = response.last.text

#     try:
#         questions = json.loads(ai_output)  # Convert AI response to JSON
#         with open(JSON_FILE_PATH, "w", encoding="utf-8") as file:
#             json.dump(questions, file, indent=4)
#         print("Questions updated successfully!")
#     except json.JSONDecodeError:
#         print("Error: AI response is not valid JSON.")

# # Schedule to update questions periodically
# def save_json():
#     """Saves the current question cache to a JSON file."""
#     with open("questions.json", "w", encoding="utf-8") as file:
#         json.dump(questions_cache, file, indent=4)
#     print("✅ Questions cache saved to questions.json!")
# schedule.every(1).minutes.do(save_json)

def generate_questions(level, prev):
    """Generates fresh quiz questions every time it's called."""
    print(f"Generating new {level} level questions...")

    qmd_content = read_qmd_file()
    
    if not qmd_content:
        print("⚠️ QMD file is empty. Cannot generate questions.")
        return []

    prompt = f"""
    Generate exactly 10 **new and unique** quiz questions for the {level} level based on the following content:
    {qmd_content}

    Provide the output **strictly in JSON format** with fields:
    - "question"
    - "options" (list)
    - "correctAnswer"
    - "level" (set as "{level}")
    - "avoid questions {prev}"

    Ensure **no duplicate** questions.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        if not response or not hasattr(response, "text"):
            print("⚠️ AI response is invalid.")
            return []

        ai_output = response.text.strip()

        # Ensure JSON output is correctly formatted
        if ai_output.startswith("```json"):
            ai_output = ai_output[7:-3].strip()

        try:
            questions = json.loads(ai_output)
            return questions  # Return new questions directly
        except json.JSONDecodeError:
            print("❌ Error: AI response is not valid JSON. Full response below:")
            print(ai_output)
            return []
    
    except Exception as e:
        print(f"❌ Error generating questions: {e}")
        return []

# Schedule to update questions every 24 hours (fixing 24 seconds issue)
# generate_questions()
# schedule.every(24).hours.do(generate_questions)


# Endpoint to get questions based on difficulty
@app.route("/get-questions", methods=["GET"])
def get_questions():
    level = request.args.get("level")
    if not level:
        return jsonify({"error": "Please provide a level (easy, medium, hard)."}), 400

    print(f"🔄 Generating new questions for level: {level}")
    
    # Generate new questions dynamically without saving to file
    new_questions = generate_questions(level, questions_cache[level])
    questions_cache[level] = new_questions
    return jsonify(new_questions)

@app.route("/", methods=["GET"])
def home():
    return "Server is running!"

# Run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start Flask app
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=True)
    # app.run(debug=True)
