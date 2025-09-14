from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# 🔑 API Key configure
genai.configure(api_key="AIzaSyD7KyKnYSgCqU3-jifOM4Ej7Dfi7ef-fJU")

# Serve the frontend (index.html with CSS/JS inside)
@app.route("/")
def home():
    return render_template("index.html")

# 🎵 Lyrics Generator with Context
@app.route("/api/lyrics", methods=["POST"])
def generate_lyrics():
    try:
        data = request.json
        song_name = data.get("song_name", "Unknown Song")

        # Step 1: Ask Gemini about the song context (movie, mood, situation)
        context_prompt = f"""
        You are a Tamil cinema music expert.
        Song: {song_name}

        - Identify if this song belongs to a Tamil movie or popular culture.
        - Tell me the movie name, the mood (action, love, devotional, sad, inspirational, kuthu etc.)
        - Tell me in 2 lines only: What situation this song is usually used in.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        context_resp = model.generate_content(context_prompt)

        song_context = context_resp.text if context_resp and context_resp.text else "Unknown movie & mood"
        
        # Step 2: Generate Lyrics based on that context
        lyrics_prompt = f"""
        Generate Tamil Thanglish lyrics (minimum 15 lines) based on the following song details:

        Song name: {song_name}
        Context: {song_context}

        - Match the mood & feel of the original context.
        - If action/intro song → give powerful, energetic cinema vibe.
        - If love/emotional → give romantic, poetic style.
        - If devotional/historical → give mild, spiritual or kingly style.
        - If kuthu/dance → only then give local dance vibe.
        - Do NOT add explanations, only lyrics output.
        """

        lyrics_resp = model.generate_content(lyrics_prompt)
        lyrics = lyrics_resp.text if lyrics_resp and lyrics_resp.text else "No lyrics generated."

        return jsonify({
            "song_name": song_name,
            "context": song_context,
            "lyrics": lyrics
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: Dummy Poster API
@app.route("/api/poster", methods=["POST"])
def poster():
    import random
    return jsonify({
        "poster": f"https://picsum.photos/300/300?random={random.randint(1,1000)}"
    })

if __name__ == "__main__":
    # For Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
