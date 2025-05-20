import requests
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image
from io import BytesIO
import os
import uuid

# Configs (adicione suas chaves)
TTSMAKER_API_KEY = "YOUR_TTSMAKER_KEY"
PIXABAY_API_KEY = "YOUR_PIXABAY_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_KEY"

def get_related_image(query):
    response = requests.get(f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&orientation=vertical&safesearch=true")
    data = response.json()
    if data["hits"]:
        return data["hits"][0]["largeImageURL"]
    return None

def get_summary_gemini(text):
    prompt = f"Summarize this football news in 50 words, urgent tone, perfect for YouTube Shorts narration:

{text}"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    json_data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json=json_data
    )
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

def get_tts_audio(text, voice="en_us_001"):
    response = requests.post("https://api.ttsmaker.com/v1/tts",
        json={
            "text": text,
            "voice": voice,
            "lang": "en",
            "speed": 1.0,
            "format": "mp3",
            "api_key": TTSMAKER_API_KEY
        })
    audio_url = response.json().get("url")
    audio = requests.get(audio_url)
    filename = f"temp/audio_{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(audio.content)
    return filename

def create_video(image_url, audio_path, text):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_path = f"temp/img_{uuid.uuid4()}.jpg"
    img.save(img_path)

    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(img_path).set_duration(audio_clip.duration).resize((720, 1280))
    final_clip = CompositeVideoClip([image_clip])
    final_clip = final_clip.set_audio(audio_clip)
    output_path = f"output/video_{uuid.uuid4()}.mp4"
    final_clip.write_videofile(output_path, fps=24)

    return output_path

# Exemplo de uso
if __name__ == "__main__":
    fake_news = "Cristiano Ronaldo was suspended after an incident during the last game. The fans are furious and the club is under pressure."
    summary = get_summary_gemini(fake_news)
    print("Resumo:", summary)
    image_url = get_related_image("Cristiano Ronaldo")
    audio_path = get_tts_audio(summary)
    video_path = create_video(image_url, audio_path, summary)
    print("Vídeo gerado em:", video_path)
