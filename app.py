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
videoTitle = "How to Make an EASY Paper Airplane in 1 Minute (60 seconds) — Flies REALLY Far"

# Full video transcript
videoTranscript = """
Intro
0:00
in this video I'm going to teach you how
0:01
to make this absolutely amazing paper
0:03
airplane that flies over 100 ft and it
0:06
is so easy to fold that I'm going to
0:08
teach you how to make it in literally 60
0:09
seconds or less so grab your sheet of
0:12
paper it can be 8 1/2 by 11 in or A4
0:15
whatever you have on hand and we're
0:16
going to begin in 3 2 one go Begin by
Tutorial
0:21
folding it in half like
0:24
this open the paper up and you can fold
0:27
triangles like this but leave a little
0:29
gap between The Edge and the center
0:31
crease do the same thing on the other
0:34
side and now fold this edge here to Land
0:38
again close to the center crease but not
0:40
all the way to it and do the same thing
0:43
on the other
0:47
side and we're going to fold in one more
0:49
time just like this making it really
0:53
narrow and you want to leave a gap once
0:55
again do the same thing on this
0:58
side
1:00
just like that and now you can fold this
1:03
in half and fold the Wings by taking
1:06
this edge here all the way to that
1:07
bottom Edge just like that and unfold
1:11
that do the same thing on this
1:14
side just like that and this is a
1:17
finished paper airplane so if you want
Outro
1:20
you can use a little tape to hold that
1:22
together but it'll fly well even if you
1:23
don't do that so let's see this thing in
1:28
action
1:37
for
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
