import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API Key:", os.getenv("OPENAI_API_KEY"))  # Debugging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Full video transcript
videoTranscript = """
0:00 Here's how you add a filter in iPhone camera app. Let's open up the camera.
0:02 Camera app so let's open up the camera.
0:05 But on the newer iPhones, we need to tap on this Arrow here.
0:07 Then we're going to see the filter icon. It looks like three overlapping circles.
0:13 Slide across to select whatever filter you would like.
0:15 whatever filter you would like once you
0:18 have selected the filter you just tap on
0:22 the icon here you tap on the Arrow to
0:26 remove get the picture you would like
0:28 and take the picture
0:30 now if you've already taken a picture
0:33 and you want to add a filter just tap on
0:36 edit and from here you're can to tap on
0:39 the filter icon and even though you've
0:41 already taken the filter you can change
0:44 the filter like so maybe you liked Vivid
0:47 and you can also change the intensity by
0:50 using the slider 100 being the most
0:53 Vivid zero being the least and of course
0:56 applies for each mode as well
"""

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

        prompt='''
        You are describing this image to a blind or low-vision user. 
        Provide a short, clear, and practical description of the image content. 
        Avoid using visual terms like 'looks like' or 'appears.' 
        Instead, describe what is present in a way that helps the user understand its function or context. 
        Be concise yet informative enough for the user to act on the information. 
        The topic of the video is about how to add a filter on an iPhone camera app.
        The user paused the video at timestamp {video_time} seconds.

        Here is the **FULL** video transcript for context:
        {videoTranscript}

        Here is an example of a good description:

        Example: 'The screen shows a settings menu with five selectable options. The third option, labeled 'Accessibility,' is currently highlighted. 
        With a screen reader, the user would hear each menu item read aloud as they swipe through, with the currently highlighted option announced as "Accessibility, button, double-tap to select."' 
        
        Now, describe the following image:
        '''
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                ],
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
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

        prompt='''
        You are answering a question based on an image for a blind or low-vision user. 
        Ensure your response is clear, direct, and useful for someone relying on a screen reader. 
        Avoid visual references like 'as seen' or 'looks like.' 
        Instead, describe relevant details in functional terms. 
        When appropriate, include how a screen reader might announce elements in the image. 
        The user paused the video at timestamp {video_time} seconds.

        Here is the **FULL** video transcript for context:
        {videoTranscript}
        
        Example 1: 'The settings menu is open with five options. The third option, labeled 'Accessibility,' is currently selected. A screen reader would announce: 'Accessibility, button, double-tap to select.'' 
        Example 2: 'The photo gallery shows three recent images. The first image is highlighted. A screen reader would say: 'Photo, 1 of 3, selected. Double-tap to open.'' 
        
        Now, answer the following question based on this image: '{question}'."
        '''

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the user's question: {question}. Answer in a succinct manner.".format(question=question),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                ],
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        answer = response.choices[0].message.content
        return JSONResponse({"answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
