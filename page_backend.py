from flask import Flask, request, jsonify, render_template
import openai
from sell_bot import MariamSellBotAdvanced
import tempfile
from make_voice import get_audio
import base64


def read_api_key(file_path):
    with open(file_path, "r") as f:
        return f.read().strip()


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test', methods=['GET'])
def test_route():
    return 'Test successful'


@app.route('/get_reply', methods=['POST'])
def get_reply():
    user_message = request.form['message']
    # Process the message and get a reply (this is where you'd insert your chat logic)

    response = bot.generate_dialogue(user_message)

    return jsonify({'bot_response': response})


def transcribe_audio(audio_data, api_key):
    # Initialize OpenAI API
    openai.api_key = api_key

    # Create a temporary file to store the audio bytes
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(audio_data)
        temp_audio_file.flush()  # Make sure all data is written to disk
        temp_audio_file.seek(0)  # Reset file pointer

        # Perform the transcription
        transcript = openai.Audio.transcribe("whisper-1", temp_audio_file)

    # Assuming 'choices' in transcript contains the textual result
    return transcript['text']


@app.route('/get_audio_reply', methods=['POST'])
def get_audio_reply():
    audio_data = request.files['audio'].read()
    user_message = transcribe_audio(audio_data, api_key)
    print(user_message)
    response_text = bot.generate_dialogue(user_message)
    response_audio_blob = get_audio(response_text, voice_api_key)

    # Convert bytes to base64 string
    response_audio_blob_base64 = base64.b64encode(response_audio_blob).decode("utf-8")

    # Send as part of JSON response
    return jsonify({'bot_response_text': response_text, 'bot_response_audio': response_audio_blob_base64})


if __name__ == '__main__':
    api_key = read_api_key('api_key.txt')
    voice_api_key = read_api_key('voice_api_key.txt')

    bot = MariamSellBotAdvanced(api_key)

    app.run(debug=True)
