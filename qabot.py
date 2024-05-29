import streamlit as st
import PyPDF2
import openai
import requests
import json
import os
from transformers import GPT2Tokenizer

# Load GPT-2 tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# CSS tùy chỉnh với class lồng nhau
css = """
<style>
.chat-box {
    padding: 10px;
    margin-bottom: 10px;
}
.user {
    text-align: right;
    color: white;
    background-color: grey;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 5px;
}
.bot {
    text-align: left;
    color: white;
    background-color: black;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 5px;
}
</style>
"""

# Thêm CSS vào ứng dụng
st.markdown(css, unsafe_allow_html=True)

# Load API key from environment variable or other source
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to read PDF content
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Hàm gọi API /api/chat để nhận phản hồi
# Hàm gọi API /api/chat để nhận phản hồi
def get_response_from_api(user_input):
    url = "http://127.0.0.1:5000/api/chat"  # URL của API local
    headers = {"Content-Type": "application/json"}
    payload = {"message": user_input}
    
    response = requests.post(url, headers=headers, json=payload)  # Sử dụng json thay vì data
    if response.status_code == 200:
        return response.json().get("response", "Không có phản hồi từ API.")
    else:
        return "Lỗi khi gọi API."

# Hàm gọi API /api/histories để lấy lịch sử trò chuyện
def get_chat_history():
    url = "http://127.0.0.1:5000/api/histories"  # URL của API local
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []  # Trả về một danh sách trống nếu có lỗi


# Danh sách các từ khóa hoặc cụm từ liên quan đến tư vấn của công ty
company_keywords = ["tư vấn", "công ty", "dịch vụ", "sản phẩm", "hỗ trợ", "trang phục", "điều"]

# Function to call OpenAI API / ChatGPT
def get_response_from_chatgpt(user_input, context=None):
    relevant_question_count = sum(keyword in user_input.lower() for keyword in company_keywords)
    
    if relevant_question_count > 0:
        messages = [
            {"role": "system", "content": "Bạn là một trợ lý thông minh. Bạn chỉ được trả lời các câu hỏi liên quan đến tư vấn của công ty."},
            {"role": "user", "content": user_input}
        ]
        
        if context:
            messages.insert(1, {"role": "user", "content": f"Văn bản sau đây là từ các tài liệu PDF: {context}"})
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
        ),
        
        return response.choices[0].message.content
    else:
        return "Câu hỏi của bạn không liên quan đến mục đích tư vấn của công ty."

# Main function to control the interface
def main():
    st.title("Chatbot đọc và trả lời từ nhiều tệp PDF bằng Streamlit")

    uploaded_files = st.file_uploader("Chọn các tệp PDF", type="pdf", accept_multiple_files=True)
    combined_text = ""

    if uploaded_files:
        for uploaded_file in uploaded_files:
            combined_text += read_pdf(uploaded_file)
        
        tokens = tokenizer.encode(combined_text)
        if len(tokens) > 16385:
            st.error("Nội dung văn bản quá dài, cần rút ngắn lại.")

    st.header("Chat với Chatbot")
    
    if "history" not in st.session_state:
        st.session_state.history = []

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    if st.session_state.history:
        for chat in st.session_state.history:
            st.markdown(f'<div class="chat-box user">{chat["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-box bot">{chat["answer"]}</div>', unsafe_allow_html=True)
            st.markdown("---")
    
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn vào đây:", st.session_state.user_input)
        submit_button = st.form_submit_button(label="Gửi")
        
        if submit_button:
            response_text = get_response_from_api(user_input)
            st.session_state.history.append({"question": user_input, "answer": response_text})
            st.session_state.user_input = ""  # Clear the input box after sending the question
            st.experimental_rerun()  # Rerun the script to update the UI

if __name__ == "__main__":
    main()
