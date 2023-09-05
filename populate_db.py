import sqlite3
from transformers import BertTokenizer, BertModel


def bert_tokenization(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = model(**inputs)
    bert_tokens = outputs.last_hidden_state[:, 0, :].squeeze().detach().cpu().numpy()
    return bert_tokens.tobytes()  # Converting numpy array to bytes


def create_and_populate_db():
    # Initialize SQLite database
    conn = sqlite3.connect('instruments.db')
    c = conn.cursor()

    # Clear table
    c.execute('''DROP TABLE IF EXISTS instruments''')

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS instruments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  description TEXT, 
                  name TEXT,
                  bert_tokens_desc BLOB,
                  bert_tokens_name BLOB)''')


    # Initialize Bert tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    # Populate database with 10 guitars
    guitar_descriptions = [
        "Fender Stratocaster - Features a double-cutaway body, 3 single-coil pickups, and a two-point synchronized tremolo system. Suitable for genres from blues to metal.",

        "Gibson Les Paul - Equipped with dual humbucking pickups, a solid mahogany body, and a set neck construction, offering warm, fat tones ideal for rock and blues.",

        "Ibanez RG550 - Comes with a Wizard III neck, a double-locking tremolo system, and high-output DiMarzio pickups. Specifically designed for fast playing and high-gain tones.",

        "Yamaha Pacifica - Features a double-cutaway alder body, a bolt-on maple neck, and a vintage-style tremolo system. A beginner-friendly guitar with a balanced tonal range.",

        "PRS Custom 24 - Offers 24 frets, a mahogany body with a carved maple top, and custom-wound pickups with a 5-way switch, tailored for professional musicians.",

        "Epiphone Les Paul - A cost-effective alternative to the Gibson Les Paul, featuring a mahogany body, a maple veneer top, and Alnico Classic humbuckers.",

        "Gretsch G2622 Streamliner - Characterized by its laminated maple body, Broad’Tron humbucking pickups, and a thin U-shaped neck. Perfect for those aiming for a vintage sound and look.",

        "Jackson Dinky - Known for its lightweight alder body, one-piece maple neck, and high-gain Seymour Duncan pickups. Designed for rapid playing and shredding techniques.",

        "Suhr Modern Pro - Built with a basswood body, a Pau Ferro fingerboard, and an HSH pickup configuration. Known for its exceptional playability and tonal versatility.",

        "Rickenbacker 330 - Features a semi-hollow body, high-gain single-coil pickups, and a unique 'R'-tailpiece. Noted for its jangly, bright tones favored in alternative and indie rock."
    ]

    names = [
        "Fender Stratocaster",
        "Gibson Les Paul",
        "Ibanez RG550",
        "Yamaha Pacifica",
        "PRS Custom 24",
        "Epiphone Les Paul",
        "Gretsch G2622 Streamliner",
        "Jackson Dinky",
        "Suhr Modern Pro",
        "Rickenbacker 330"
    ]

    for name, desc in zip(names, guitar_descriptions):
        # Embedding the description
        bert_tokens_desc = bert_tokenization(desc, tokenizer, model)

        # Embedding the name of the instrument
        bert_tokens_name = bert_tokenization(name, tokenizer, model)

        # Store both description and name embeddings into the database
        c.execute("INSERT INTO instruments (name, description, bert_tokens_desc, bert_tokens_name) VALUES (?, ?, ?, ?)",
                  (name, desc, bert_tokens_desc, bert_tokens_name))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_and_populate_db()
