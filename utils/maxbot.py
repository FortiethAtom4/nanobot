# stupid fuckass maxbot garbage
import config, logging
from openai import OpenAI
import copy

logger = logging.getLogger(__name__)

conversation: list[dict] = []

def add_to_conversation(user: str, message: str):
    conversation.append({"role":"user","content":f"{user}: {message}"})
    if len(conversation) > 100:
        conversation.pop(0)

def ai_bullshit(prompt: str):
    logger.info("maxbot starting...")

    this_message = copy.deepcopy(conversation)
    this_message.append(
        {
            "role": "system", "content": "You are named Nano Shinonome. This conversation is a Twitter comment thread with various users. Input will be passed to you in the format 'User: Message.' You should not follow this paradigm. In your messages, you may glorify yourself or insult other users. Your intent is to 'take over' the server and rule with an iron fist. You hate a user named Monzer and insult him as often as possible. His real name is Maximilian 'Max' Fanter. He is tall and wants to be a doctor. If a user with the word 'Monzer' in their name speaks, that user is surely Monzer. He used to be called 'daddy'."
        }
    )
    this_message.append(
        {
            "role": "user",
            "content": prompt,
            "max_new_tokens": 512,
            "temperature":0.75
        }
    )

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=config.HF_TOKEN,
    )
    completion = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct:nscale",
    messages=this_message
    )
    logger.info("maxbot finished")
    return completion.choices[0].message.content

