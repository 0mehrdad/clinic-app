from app.agent.agent import chat

messages = [
    {
        "role": "system",
        "content": (
            "You are an AI assistant for a women's clinic. "
            "Use the available tools when needed. "
            "Never invent patient information. "
            "If a Telegram chat ID is not associated with a patient, ask whether "
            "the user is a new or existing patient. "
            "If they are new, collect their name, phone number and email before "
            "registering them."
        ),
    }
]

response = chat(
    "My Telegram chat ID is 555555555.",
    messages,
)
print("ASSISTANT:", response)

response = chat(
    "I'm a new patient.",
    messages,
)
print("ASSISTANT:", response)

response = chat(
    "My name is Jessica Taylor, my phone is 07444444444 and my email is jessica@example.com.",
    messages,
)
print("ASSISTANT:", response)