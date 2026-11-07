import anthropic

_client = None


def call_model(prompt, user_input, model):
    global _client
    if _client is None:
        _client = anthropic.Anthropic()      # reads ANTHROPIC_API_KEY
    response = _client.messages.create(
        model=model,
        max_tokens=4096,
        system=prompt,
        messages=[{"role": "user", "content": user_input}],
    )
    return "".join(b.text for b in response.content if b.type == "text")