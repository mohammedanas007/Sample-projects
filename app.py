from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    messages = history + [{"role": "user", "content": user_message}]

    def generate():
        with requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": True},
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
