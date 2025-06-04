from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

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
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([segment["text"] for segment in transcript_list])
        return jsonify({"transcript": full_text})
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video"}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No transcript available"}), 404
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

