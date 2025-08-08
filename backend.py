import os
import sqlite3
import requests
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
from urllib.parse import quote

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

app = FastAPI()

def get_file_info(code):
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT file_name, file_size, file_path FROM files WHERE share_code=?", (code,))
    row = c.fetchone()
    conn.close()
    return row

@app.get("/d/{code}")
def download_file(code: str, request: Request):
    file_info = get_file_info(code)
    if not file_info:
        return Response(content="File not found", status_code=404)
    
    file_name, file_size, file_path = file_info
    file_url = API_URL + file_path

    headers = {}
    range_header = request.headers.get("range")
    if range_header:
        headers["Range"] = range_header

    def iterfile():
        with requests.get(file_url, headers=headers, stream=True) as r:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

    response_headers = {
        "Content-Disposition": f'attachment; filename="{quote(file_name)}"',
        "Accept-Ranges": "bytes"
    }

    return StreamingResponse(iterfile(), headers=response_headers, media_type="application/octet-stream")
