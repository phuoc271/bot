import streamlit as st
import PyPDF2
import openai
import os
import requests
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

openai.api_key = "sk-proj-pX9SzG2pFHppVyyHfJ61T3BlbkFJG4YJc4P00tdg2e6osgpp"


# Function to read PDF content
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


# Hàm gọi API /api/history để lấy lịch sử trò chuyện
def get_chat_history():
    url = "http://127.0.0.1:5000/api/history"  # URL của API local
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []  # Trả về một danh sách trống nếu có lỗi

# Function to call OpenAI API / ChatGPT
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
    
    # Gửi phản hồi từ ChatGPT tới API local
    api_response = get_response_from_api(response_text)
    
    return api_response

def get_response_from_api(user_input):
    url = "http://127.0.0.1:5000/api/chat"  # URL của API local
    headers = {"Content-Type": "application/json"}
    payload = {"message": user_input}
    
    response = requests.post(url, headers=headers, json=payload)  # Sử dụng json thay vì data
    if response.status_code == 200:
        return response.json().get("response", "Không có phản hồi từ API.")
    else:
        return "Lỗi khi gọi API."
    
def main():
    st.title("Chatbot đọc và trả lời từ nhiều tệp PDF bằng Streamlit")

    uploaded_files = st.file_uploader("Chọn các tệp PDF", type="pdf", accept_multiple_files=True)
    combined_text = ""

    if uploaded_files:
        for uploaded_file in uploaded_files:
            combined_text += read_pdf(uploaded_file)
        
        # Check token length
        tokens = tokenizer.encode(combined_text)
        if len(tokens) > 16385:
            st.error("Nội dung văn bản quá dài, cần rút ngắn lại.")

    st.header("Chat với Chatbot")
    
    # Sử dụng hai cột để bố trí giao diện
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Lịch sử trò chuyện")
        history = get_chat_history()
        if history:  # Kiểm tra nếu lịch sử không rỗng
            for chat in history:
                if chat.get("role") == "user":
                    st.markdown(f'<div class="chat-box user">{chat.get("content", "")}</div>', unsafe_allow_html=True)
                elif chat.get("role") == "bot":
                    st.markdown(f'<div class="chat-box bot">{chat.get("content", "")}</div>', unsafe_allow_html=True)
                st.markdown("---")
            # Sau khi hiển thị lịch sử trò chuyện từ get_chat_history(), hãy cập nhật vào st.session_state.history
            st.session_state.history = history
        else:
            st.write("Lịch sử trống")

    with col2:
        st.subheader("Trò chuyện mới")
        if "history" not in st.session_state:
            st.session_state.history = []

        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        if st.session_state.history:
            for chat in st.session_state.history:
                if chat.get("role") == "user":
                    st.markdown(f'<div class="chat-box user">{chat.get("content", "")}</div>', unsafe_allow_html=True)
                elif chat.get("role") == "bot":
                    st.markdown(f'<div class="chat-box bot">{chat.get("content", "")}</div>', unsafe_allow_html=True)
                st.markdown("---")

    # Form for user input to enable Enter key submission
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn vào đây:", st.session_state.user_input)
        submit_button = st.form_submit_button(label="Gửi")
        
        if submit_button:
            if uploaded_files:
                response_text = get_response_from_chatgpt(user_input, combined_text)
            else:
                response_text = get_response_from_chatgpt(user_input)
                
            st.session_state.history.append({"role": "user", "content": user_input})  # Thêm dữ liệu từ người dùng vào lịch sử
            st.session_state.history.append({"role": "bot", "content": response_text})  # Thêm dữ liệu từ bot vào lịch sử
            st.session_state.user_input = ""  # Clear the input box after sending the question
            st.experimental_rerun()  # Rerun the script to update the UI

if __name__ == "__main__":
    main()