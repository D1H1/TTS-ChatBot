import openai
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine
import json

from process_functions import process_function_calls


def get_instrument_details():
    function = {
        "name": "get_instrument_details",
        "description": "In last message user wants to know details about specific instrument",
        "parameters": {
            "type": "object",
            "properties": {
                "instrument_name": {"type": "string"}
            },
            "required": ["instrument_name"],
        }
    }
    return function


def get_user_wishes():
    function = {
        "name": "extract_wishes",
        "description": "Extract characteristics about instrument which user want to find in last message",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {"type": "string"}
            },
            "required": ["user_message"],
        }
    }
    return function


class MariamSellBotAdvanced:
    def __init__(self, api_key):
        self.conversation = [
            {"role": "system",
             "content": "You are Mariam, a sell-bot for a music shop. You can only discuss musical instruments and company-related topics."}
        ]
        self.allowed_topics = ["guitar", "piano", "drum", "saxophone", "music shop"]
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.functions = [get_user_wishes(), get_instrument_details()]
        self.api_key = api_key

    def embed_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().detach().cpu().numpy()

    def generate_dialogue(self, user_message):
        self.conversation.append({"role": "user", "content": user_message})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.conversation,
            function_call="auto",
            functions=self.functions
        )

        assistant_message = response['choices'][0]['message']['content']

        if "function_call" in response['choices'][0]['message']:
            print(response['choices'][0]['message']["function_call"]["name"])
            function_message = response['choices'][0]['message']['function_call']
            function_response = process_function_calls(user_message, function_message, self.api_key)

            assistant_message = function_response

        if self.is_response_valid(assistant_message):
            self.conversation.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        else:
            self.conversation = self.conversation[:-1]  # Remove user unrelated message
            return "I can only discuss musical instruments and company-related topics."

    def is_response_valid(self, message):
        assistant_embedding = self.embed_text(message)
        topic_similarities = [1 - cosine(assistant_embedding, self.embed_text(topic)) for topic in self.allowed_topics]

        threshold = 0.6
        return any(similarity > threshold for similarity in topic_similarities)


if __name__ == "__main__":

    api_key = "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"
    openai.api_key = api_key
    bot = MariamSellBotAdvanced(api_key)

    user_message = "Tell me about the stuff you have."
    bot_response = bot.generate_dialogue(user_message)
    print(f"User: {user_message}")
    print(f"Mariam: {bot_response}")

    user_message = "I want to know more details about specific instrument: electric gibson guitar"
    bot_response = bot.generate_dialogue(user_message)
    print(f"User: {user_message}")
    print(f"Mariam: {bot_response}")

    user_message = "I want to find guitar with good gain sound"
    bot_response = bot.generate_dialogue(user_message)
    print(f"User: {user_message}")
    print(f"Mariam: {bot_response}")
