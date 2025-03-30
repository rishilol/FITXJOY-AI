from groq import Groq
import os

# Set API key directly
api_key = "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"
print(f"Using API key: {api_key[:10]}...")  # Only print first 10 chars for security

client = Groq(api_key=api_key)

# Test the connection with a simple prompt
try:
    response = client.chat.completions.create(
        model="mixtral-8x7b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, Groq is working!'"}
        ],
        max_tokens=50,
        temperature=0.7
    )
    print("Groq API Test Result:")
    print(response.choices[0].message.content)
    print("\nGroq integration is working correctly!")
except Exception as e:
    print(f"Error testing Groq integration: {str(e)}") 