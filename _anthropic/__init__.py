from anthropic import Anthropic

API_KEY = "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"

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
