from youtube_transcript_api import YouTubeTranscriptApi
import os


def fetch_transcripts(video_ids):
    all_text = []
    for vid in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vid)
            text = " ".join([t['text'] for t in transcript])
            all_text.append(text)
        except:
            continue
    return all_text


def update_content_file():
    video_ids = ["abc123", "def456"]  # Replace with actual Crypto Banter video IDs
    transcripts = fetch_transcripts(video_ids)
    with open("data/crypto_banter_content.txt", "a") as f:
        f.write("\n".join(transcripts))
