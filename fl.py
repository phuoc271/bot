from flask import Flask, request, jsonify
import openai
import os
import PyPDF2

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
    pdf_file = request.files.get('pdf_file')
    context = None
    
    # Read text from uploaded PDF file
    if pdf_file:
        context = read_pdf(pdf_file)
    
    # Make a request to OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý thông minh. Bạn chỉ được trả lời các câu hỏi liên quan đến tư vấn của công ty."},
            {"role": "user", "content": message}
        ]
    )
    reply = response.choices[0].message.content
    chat_history.append({"user": message, "bot": reply})
    return jsonify({"response": reply})

@app.route('/api/histories', methods=['GET'])
def histories():
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)
