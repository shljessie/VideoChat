# Vidi: Video Assistant Agent for Blind and Low Vision Users

This project is a FastAPI application paired with a front-end interface that allows users to interact with video frames. It provides the ability to:

- Extract keyframes from a video when paused.
- Automatically generate a description of the frame.
- Ask questions about the frame and receive AI-generated answers.
- Read the generated descriptions and answers aloud using text-to-speech.
- Stop text-to-speech at any time with the `Esc` key.

---

## Features

1. **Keyframe Extraction:**
   - When the video is paused, the current frame is captured and analyzed.
   - A textual description of the frame is generated using OpenAI's GPT-4o Mini model.

2. **Question Asking:**
   - Users can ask a question about the paused frame by pressing the `Q` key.
   - The application sends the frame and the question to OpenAI and displays the response.

3. **Text-to-Speech:**
   - Descriptions and answers are read aloud to users.
   - Speech can be stopped at any time by pressing the `Esc` key.

4. **Keyboard-Driven Interaction:**
   - `Q` key: Ask a question about the paused frame.
   - `Esc` key: Stop any ongoing text-to-speech.

---


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo


2. Set Up a Virtual Environment
bash
Copy
Edit
python -m venv venv
```markdown
3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Create a .env File

In the project root directory, create a file named `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

5. Run the Application

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The application will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## How to Use

### Open the App:

Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.


