from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import subprocess
import json
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "YouTube Transcript API is running"

@app.route("/transcript", methods=["POST"])
def get_transcript():
    data = request.json
    youtube_url = data.get("url")

    if not youtube_url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    try:
        video_id = extract_video_id(youtube_url)

        # Use yt-dlp to get transcript using uploaded cookies
        result = subprocess.run([
            "yt-dlp",
            "--cookies", "www.youtube.com_cookies.txt",
            "--write-auto-sub",
            "--skip-download",
            "--sub-lang", "en",
            "--sub-format", "json3",
            "--output", "%(id)s.%(ext)s",
            f"https://www.youtube.com/watch?v={video_id}"
        ], capture_output=True, text=True)

        # Expect a .json3 subtitle file
        subtitle_file = f"{video_id}.en.json3"
        if not os.path.exists(subtitle_file):
            return jsonify({"error": "Subtitle file not found"}), 404

        with open(subtitle_file, "r", encoding="utf-8") as f:
            caption_data = json.load(f)

        events = caption_data.get("events", [])
        full_text = " ".join([
            seg["segs"][0]["utf8"]
            for seg in events if "segs" in seg and seg["segs"]
        ])

        # Clean up
        os.remove(subtitle_file)

        return jsonify({"transcript": full_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    else:
        raise ValueError("Invalid YouTube URL format")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
