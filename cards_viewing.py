import os
from google import genai
from google.genai import types

with open(os.path.join("img", "office.jpg"), 'rb') as f:
    image_bytes = f.read()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=[
        types.Part.from_bytes(
        data=image_bytes,
        mime_type='image/jpeg',
        ),
        'Briefly describe this environment for a visually impaired user'
    ]
)

print(response.text)
