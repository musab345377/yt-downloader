import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.background import BackgroundTasks
import yt_dlp

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Fast YT Downloader</title>
    <style>
        body { font-family: sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; background: #121212; color: #fff; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: none; box-sizing: border-box; }
        input { background: #222; color: #fff; border: 1px solid #444; }
        button { background: #00b4d8; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #0096c7; }
    </style>
</head>
<body>
    <h2>🚀 Render YT Downloader</h2>
    <form action="/download" method="post">
        <input type="url" name="url" placeholder="Paste YouTube link here" required>
        <select name="resolution">
            <option value="1080">1080p</option>
            <option value="720">720p</option>
            <option value="144">144p</option>
        </select>
        <button type="submit">Download Video</button>
    </form>
</body>
</html>
"""

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

@app.post("/download")
def download_video(background_tasks: BackgroundTasks, url: str = Form(...), resolution: str = Form(...)):
    out_filename = f"video_{resolution}p.mp4"
    
       ydl_opts = {
        'format': f'bv*[height<={resolution}][ext=mp4]+ba[ext=m4a]/b[height<={resolution}][ext=mp4]/b',
        'outtmpl': out_filename,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'client': ['ios'],
                'skip': ['dash', 'hls']
            }
        }
    }

    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(out_filename):
            background_tasks.add_task(remove_file, out_filename)
            return FileResponse(path=out_filename, filename=out_filename, media_type='video/mp4')
        else:
            raise HTTPException(status_code=500, detail="File processing failed.")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download Error: {str(e)}")
