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

# Function to get response from ChatGPT
def get_response_from_chatgpt(user_input, context=None):
    messages = [
        {"role": "system", "content": "Bạn là một trợ lý thông minh .Luôn trả lời người dùng bằng tiếng việt . Hãy trả lời ngắn gọn và đúng trọng tâm câu hỏi của người dùng. Giới hạn câu trả lời của bạn trong 200 từ. Hãy trả lời chính xác các câu hỏi, và thông tin trả lời câu hỏi chỉ được lấy trực tiếp từ thông tin đã cung cấp."},
        {"role": "user", "content": user_input}
    ]
    if context:
        messages.insert(1, {"role": "user", "content": f"Văn bản sau đây là từ các tài liệu PDF: {context}"})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages
    )
    
    response_text = response.choices[0]["message"]["content"]  # Extract content from response
    
    return response_text

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message', '')
        pdf_file = request.files.get('pdf_file')
        context = None
        
        if pdf_file:
            context = read_pdf(pdf_file)
            
        # Lưu tin nhắn của người dùng vào lịch sử trước
        chat_history.append({"role": "user", "content": user_input})
        
        # Get response from ChatGPT
        bot_reply = get_response_from_chatgpt(user_input, context)
        
        # Lưu phản hồi của bot vào lịch sử sau
        chat_history.append({"role": "bot", "content": bot_reply})
        
        # Return the bot reply as JSON response
        return jsonify({"response": bot_reply})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def history():
    return jsonify(chat_history)

if __name__ == '__main__':
    app.run(debug=True)
