from anthropic import Anthropic

API_KEY = None

client = Anthropic(
    api_key=API_KEY,
)

message = client.messages.create(
    max_tokens=64,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-3-5-sonnet-latest",
)

print(message.content)
