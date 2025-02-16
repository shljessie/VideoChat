import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API Key:", os.getenv("OPENAI_API_KEY"))  # Debugging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Index file not found")

@app.post("/process-image")
async def process_image(request: Request):
    try:
        data = await request.json()
        base64_image = data.get("image")
        if not base64_image:
            raise HTTPException(status_code=400, detail="No image provided.")
        
        image_data_url = f"data:image/jpeg;base64,{base64_image}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are describing this image to a blind and low vision user. What is in this image? Can you describe it?",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                ],
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        
        description = response.choices[0].message.content
        return JSONResponse({"description": description})
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-question")
async def process_question(request: Request):
    try:
        data = await request.json()
        base64_image = data.get("image")
        question = data.get("question")
        if not base64_image or not question:
            raise HTTPException(status_code=400, detail="Image and question are required.")
        
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are describing this image to a blind and low vision user. What is in this image? Can you describe it?",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                ],
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        answer = response.choices[0].message.content
        return JSONResponse({"answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
