import requests
import csv
import json

LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"


def send_devs_and_get_similarity(path, threshold=0.7, model="openai/gpt-oss-20b"):
    try:
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # skip header
            names = [row[0] for row in reader]

        # Rakennetaan system- ja user-promptit
        system_prompt = (
            "You are a precise and efficient assistant for fuzzy duplicate detection. "
            f"Use a similarity threshold of {threshold}. "
            "You will receive a JSON list of developer objects, each containing 'name' and 'email'. "
            "Your task is to identify entries that likely refer to the same person, even with minor differences "
            "in spelling, formatting, or domain variations. These are called 'fluffy duplicates'. "
            "When comparing entries, consider: first and last names (including common abbreviations), "
            "email usernames and domains, and potential typographical variations. "
            "Output only a JSON array of the detected duplicate groups, where each group contains the duplicate entries. "
            "Do not include unique developers. Do not add explanations or text outside the JSON array."
        )

        user_prompt = json.dumps(names, ensure_ascii=False)

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        response = requests.post(LMSTUDIO_API_URL, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        # Yritetään tulkita vastaus JSONiksi
        result = json.loads(reply)
        print("Received JSON from LM Studio")
        return result
    except Exception as e:
        print(f"Error reading {path} or sending to LM Studio: {e}")
        raise
