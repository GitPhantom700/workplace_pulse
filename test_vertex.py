from google import genai
try:
    client = genai.Client(vertexai=True, project="workplacepulse", location="us-central1")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say hello"
    )
    print("SUCCESS:", response.text)
except Exception as e:
    print("FAILED:", e)
