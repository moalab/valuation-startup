from faster_whisper import WhisperModel

def transcribe(audio_path: str, device: str = "cpu", compute_type: str = "int8"):
    model = WhisperModel("small", device=device, compute_type=compute_type)
    segments, info = model.transcribe(audio_path)
    text = " ".join([s.text for s in segments])
    return {"language": info.language, "duration": info.duration, "text": text}
