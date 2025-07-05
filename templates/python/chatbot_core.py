from transformers import pipeline
from database import save_chat

chatbot_pipeline = pipeline("conversational", model="microsoft/DialoGPT-medium")

def get_bot_response(user_id, message):
    try:
        response = chatbot_pipeline(message)
        bot_response = response[0]['generated_text']
    except:
        bot_response = "Sorry, I had trouble understanding that."

    save_chat(user_id, message, bot_response)
    return bot_response
