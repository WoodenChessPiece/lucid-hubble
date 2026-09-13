import json
from src.publisher.youtube_uploader import upload_video_to_youtube

video_path = "storage/videos/CYBERPUNK_COUNCIL_BENCHMARK.mp4"
thumb_path = "storage/videos/CYBERPUNK_COUNCIL_BENCHMARK_thumb.png"
meta_path = "storage/videos/CYBERPUNK_COUNCIL_BENCHMARK_youtube.json"

with open(meta_path, "r") as f:
    meta = json.load(f)

print("Publishing benchmark test video to YouTube as UNLISTED...")
video_id = upload_video_to_youtube(
    video_file_path=video_path,
    thumbnail_file_path=thumb_path,
    metadata=meta
)
print(f"🎉 SUCCESS! Live URL: https://youtu.be/{video_id}")
