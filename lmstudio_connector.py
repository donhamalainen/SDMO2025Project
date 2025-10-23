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
            "You are a helpful assistant. "
            "You will receive a list of developers as JSON, each with a name and email address. "
            "Your task is to identify all developer entries that are likely duplicates (fluffy duplicates). "
            "A fluffy duplicate means two or more entries refer to the same person, even if there are minor differences in name or email. "
            "Compare names, surnames, and email addresses when identifying duplicates. "
            "Return only a JSON array of the duplicate entries (not the unique ones). "
            "Do not add any explanation, just return the JSON array of duplicates."
        )

        # system_prompt = (
        #     "You are a helpful assistant. "
        #     "You will receive a list of developers as JSON, each with a name and email address. "
        #     "Your task is to identify all developer entries that are likely duplicates (fluffy duplicates). "
        #     "A fluffy duplicate means two or more entries refer to the same person, even if there are minor differences in name or email. "
        #     "Compare names, surnames, and email addresses when identifying duplicates. "
        #     "Return only a JSON array of the duplicate pairs. "
        #     "Each array element must be an object with two fields: 'name' (the duplicate) and 'matched_with' (the name or email it was matched to). "
        #     "Do not add any explanation, just return the JSON array of duplicate pairs."
        # )
        user_prompt = json.dumps(names, ensure_ascii=False)

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "max_tokens": -1,
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
