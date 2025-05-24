import os

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"Your ANTHROPIC_API_KEY is: {api_key}")
else:
    print("ANTHROPIC_API_KEY is not set.")
