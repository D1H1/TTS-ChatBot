import json
import sqlite3
from transformers import BertTokenizer, BertModel


def embed_text(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().detach().cpu().numpy()


def process_function_calls(user_message, function_message, api_key):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    function_name = function_message.get('name', None)
    function_args_str = function_message.get('arguments', "{}")
    function_args = json.loads(function_args_str)
    output_text = ""

    # Dispatch to the correct function based on the function_name
    if function_name == "get_instrument_details":
        output_text = get_instrument_details(function_args['instrument_name'])
    elif function_name == "extract_wishes":
        output_text = extract_wishes(function_args['user_message'])
    else:
        output_text = "Unknown function call"

    # openai.api_key = "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"
    # openai.api_key = api_key
    #
    # message = [{"role": "user", "content": "Question: " + user_message},
    #            {"role": "system", "content": "Answer : " + output_text}]
    #
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=message,
    # )
    #
    # return response['choices'][0]['message']['content']

    return output_text


def get_instrument_details(query_name):
    # Initialize SQLite database
    conn = sqlite3.connect('instruments.db')
    c = conn.cursor()

    # Break the query_name into individual words
    query_words = query_name.split(" ")

    # Create SQL query string using LIKE operator to match words in the name
    query_string = "SELECT name, description FROM instruments WHERE " + \
                   " OR ".join(["name LIKE ?" for _ in query_words])

    # Execute the query
    c.execute(query_string, tuple([f"%{word}%" for word in query_words]))
    records = c.fetchall()

    # Close the connection
    conn.close()

    if records:
        matching_instruments = "\n".join([f"{record[0]}: {record[1]}" for record in records])
        return f"Details about matching instruments:\n{matching_instruments}"
    else:
        return f"No details available for {query_name}"


def extract_wishes(user_message):
    # Connect to SQLite database
    conn = sqlite3.connect("instruments.db")
    cursor = conn.cursor()

    # Split the user message into individual words
    query_words = user_message.split(" ")

    # Create SQL query string using LIKE operator for each word in the description
    query_string = "SELECT id, description FROM instruments WHERE " + \
                   " OR ".join(["description LIKE ?" for _ in query_words])

    # Execute the query
    cursor.execute(query_string, tuple([f"%{word}%" for word in query_words]))
    records = cursor.fetchall()

    conn.close()

    if records:
        word_count_dict = {}

        for record in records:
            id, desc = record
            word_count = sum(desc.lower().count(word.lower()) for word in query_words)
            word_count_dict[id] = {'description': desc, 'word_count': word_count}

        # Sort by word_count in descending order
        sorted_records = sorted(word_count_dict.values(), key=lambda x: x['word_count'], reverse=True)

        # Assuming you want the description with the most word matches
        best_match = sorted_records[0]['description']

        return f"Best matching instrument: {best_match}"

    else:
        return f"Extracted wishes: {user_message}. No similar instruments found."


# Sample usage
if __name__ == "__main__":
    # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # model = BertModel.from_pretrained('bert-base-uncased')
    # print(extract_wishes("I'm looking for a guitar with high-gain tones", model, tokenizer))

    # Test the function with an example
    instrument_name_query = "Streamliner"  # Change this to test other queries
    result = get_instrument_details(instrument_name_query)
    print(result)
