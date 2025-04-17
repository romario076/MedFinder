#!/usr/bin/env python3

import requests
import logging, json

# Logging configuration
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S %Z"
)

# Connection settings
BASE_URL = "https://poplite-api.demo.dev-ops.top"
TOKEN_FILE = "token.txt"
POP_LITE_TOKEN
def read_api_key():
    """Reads the API key from a file"""
    try:
        with open(TOKEN_FILE, "r") as f:
            api_key = f.read().strip()
        logging.info("API key successfully loaded.")
        return api_key
    except FileNotFoundError:
        logging.error(f"File {TOKEN_FILE} not found. Run generate_token.py first.")
        return None


def get_models(api_key):
    """Retrieves a list of available models"""
    url = f"{BASE_URL}/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        models = response.json()["data"]
        model_ids = [model["id"] for model in models]
        logging.info(f"Available models: {json.dumps(model_ids, indent = 4)}")
        return model_ids
    else:
        logging.error("Error retrieving model list: %s", response.text)
        return None

def chat_with_model(api_key, model_id, message):
    """Send a message to the model and return the response"""
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": message}]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        #logging.info("Model response: %s", reply)
        return reply
    else:
        logging.error("Error during chat request: %s", response.text)
        return ''


api_key = read_api_key()

models = get_models(api_key)
model = 'azure-gpt-4o'
user_message = 'How are you'
response = chat_with_model(api_key=api_key, model_id=model, message=user_message)



