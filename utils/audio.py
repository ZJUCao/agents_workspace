import whisper

model = whisper.load_model("base")
def speech_to_text(audio_path):
    return model.transcribe(audio_path)["text"]
