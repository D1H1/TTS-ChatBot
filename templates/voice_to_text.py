import openai

def transcribe_audio(audio_file, api_key):
    # Initialize OpenAI API (replace "your-openai-api-key" with your actual API key)
    openai.api_key = api_key

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript


if __name__ == "__main__":
    file_path = "/home/david/PycharmProjects/TTS_Music/static/Record (online-voice-recorder.com).mp3"
    result = transcribe_audio(file_path, "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")
    print(f"Transcript: {result['text']}")
