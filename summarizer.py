# this is using huggingface's transformers library


import requests

API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {API_KEY}"}

def summarize_text(text, max_length=150, min_length=50):
    if not text:
        return "Error: No text provided for summarization."
    
    if len(text.split()) > 900:  
        text = " ".join(text.split()[:900])
        
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_length, 
            "min_length": min_length,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    else:
        return f"Error: {response.json()}"


# import openai

# openai.api_key = "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"

# try:
#     openai.Model.list()
#     print("API Key is valid.")
# except openai.error.AuthenticationError:
#     print("Invalid API Key. Check your key at https://platform.openai.com/account/api-keys")
    
# def summarize_text(text):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": f"Summarize this: {text}"}]
#     )
#     return response["choices"][0]["message"]["content"]

# text_to_summarize = "You only get 24 hours in a day and the difference between Oprah and the person that's broke..."
# summary = summarize_text(text_to_summarize)
# print(summary)
