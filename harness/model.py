import anthropic

_client = None


def call_model(prompt, user_input, model):
    global _client
    if _client is None:
        _client = anthropic.Anthropic()      # reads ANTHROPIC_API_KEY
    response = _client.messages.create(
        model=model,
        max_tokens=1024,
        system=prompt,
        messages=[{"role": "user", "content": user_input}],
    )
    return response.content[0].text