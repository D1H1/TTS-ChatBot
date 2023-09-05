import requests
import pygame


def send_tts_request(text, api_key, speed=1, speaker="64191022c25c1f00222c0ab1"):
    url = "https://api.genny.lovo.ai/api/v1/tts"
    payload = {
        "speed": speed,
        "speaker": speaker,
        "text": text
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": api_key
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    return response.json()['id']  # Assuming the response contains a JSON payload


def get_audio_link(audio_id, api_key):
    try:
        url = f"https://api.genny.lovo.ai/api/v1/tts/{audio_id}"
        headers = {
            "accept": "application/json",
            "X-API-KEY": api_key
        }
        response = requests.get(url, headers=headers)
        audio_data = response.json()  # Assuming the response contains a JSON payload

        if audio_data['status'] == 'in_progress':
            return get_audio_link(audio_id, api_key)

        # Extract the URL from the nested data structure
        audio_url = audio_data['data'][0]['urls'][0]
    except (KeyError, IndexError):
        print("Could not extract audio URL from API response.")
        return None
    return audio_url


def get_audio(text, api_key):
    print(text)
    audio_id = send_tts_request(text, api_key)
    audio_url = get_audio_link(audio_id, api_key)
    print(audio_url)
    response = requests.get(audio_url)
    return response.content


def play_audio_from_url(audio_url):
    # Fetch and save audio
    audio_data = requests.get(audio_url).content
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data)

    # Initialize pygame and play audio
    pygame.mixer.init()
    audio_path = "temp_audio.wav"
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


if __name__ == "__main__":
    response_id = send_tts_request('Hello Friend! What are you looking for today?')
    audio_url = get_audio_link(response_id)
    play_audio_from_url(audio_url)
