import os
from groq import Groq

def chat_with_groq(conteudo):
    client = Groq(
        api_key="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",
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": conteudo,
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content