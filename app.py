import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API Key:", os.getenv("OPENAI_API_KEY"))  # Debugging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Full video title
videoTitle = "How to Make an Origami Heart - Easy Tutorial for Beginners"

# Full video transcript
videoTranscript = """
0:00
hello everyone welcome to a new video
0:03
today I'm going to teach how to make a
0:05
very simple origami heart this is a
0:08
traditional model I think it's ideal for
0:11
beginners and all we need to make it is
0:14
a square of paper you can use any size
0:17
and any type I recommend 15x 15 cm 6X 6
0:23
in and the first step is to folding half
0:26
along both diagonals as letter
0:28
x first this
0:31
[Music]
0:35
one then the
0:38
[Music]
0:47
opposite now rotate the paper in this
0:49
position and fold the top corner to the
0:53
middle just like
0:58
that now fold this the bottom
1:01
corner to the
1:04
[Music]
1:09
top with this done Let's Fold half of
1:13
the bottom Edge to the
1:16
middle first here on the right
1:24
side and then on the
1:28
left
1:32
[Music]
1:35
right turn the paper over and fold these
1:39
two top corners
1:44
down fold like this until this
1:52
line now let's do the same on the
1:54
lateral
1:57
Corners first this one
2:03
and also the
2:08
other with this done our origami heart
2:12
is
2:13
ready as I said very EAS to make I hope
2:17
most have been able to do if you enjoyed
2:19
this video don't forget to click on like
2:21
button and subscribe to my channel thank
2:24
you very much for watching and until the
2:26
next
2:28
time
2:38
[Music]
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
        The topic of the video is about {videoTitle}.
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
        The topic of the video is about {videoTitle}.
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
