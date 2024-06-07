from flask import Flask, request, jsonify
import openai
import os
import PyPDF2
import json

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

chat_history = []

# Function to read PDF content
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    context = data.get('context', '')

    # Make a request to OpenAI API
    messages = [
        {"role": "system", "content": "Bạn là một trợ lý thông minh. Bạn chỉ được trả lời các câu hỏi liên quan đến tư vấn của công ty."},
        {"role": "user", "content": message}
    ]

    if context:
        messages.insert(1, {"role": "user", "content": f"Văn bản sau đây là từ các tài liệu PDF: {context}"})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    reply = response.choices[0].message.content
    chat_history.append({"user": message, "bot": reply})

    # Convert to JSON with Vietnamese characters
    json_response = json.dumps({"response": reply}, ensure_ascii=False)
    return json_response

@app.route('/api/histories', methods=['GET'])
def histories():
    # Convert chat history to JSON with Vietnamese characters
    json_history = json.dumps(chat_history, ensure_ascii=False)
    return json_history

if __name__ == '__main__':
    app.run(debug=True)
