from fastapi import FastAPI, HTTPException
import httpx
from urllib.parse import urlparse, parse_qs

app = FastAPI()

# مفتاح RapidAPI الخاص بك
RAPIDAPI_KEY = "4848487419mshb80c4f2707bc182p189123jsn4208a36d1741"
RAPIDAPI_HOST = "youtube-transcriptor.p.rapidapi.com"

def extract_video_id(youtube_url: str) -> str:
    """
    استخراج معرف الفيديو من رابط يوتيوب.
    """
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in {"www.youtube.com", "youtube.com"}:
        query_params = parse_qs(parsed_url.query)
        return query_params.get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    return None

@app.post("/get-transcript/")
async def get_transcript(youtube_url: str, lang: str = "en"):
    """
    يأخذ رابط فيديو يوتيوب ويعيد النص التفريغي (Transcript).
    """
    # استخراج معرف الفيديو
    video_id = extract_video_id(youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # إعداد طلب API
    url = f"https://{RAPIDAPI_HOST}/transcript"
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    params = {
        "video_id": video_id,
        "lang": lang
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from API: {response.text}"
            )
        transcript_data = response.json()
        if not transcript_data or "transcriptionAsText" not in transcript_data[0]:
            raise HTTPException(status_code=404, detail="Transcription not available")
        
        transcription_text = transcript_data[0]["transcriptionAsText"]
        return {"transcription": transcription_text}
