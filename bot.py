import streamlit as st
import PyPDF2
import requests

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

# Hàm đọc nội dung PDF
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Hàm gọi API /api/histories để lấy lịch sử trò chuyện
def get_chat_history():
    url = "http://127.0.0.1:5000/api/histories"  # URL của API local
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []  # Trả về một danh sách trống nếu có lỗi

# Hàm gọi API local /api/chat
def get_response_from_api(user_input, context=None):
    url = "http://127.0.0.1:5000/api/chat"  # URL của API local
    headers = {"Content-Type": "application/json"}
    payload = {"message": user_input, "context": context}
    
    response = requests.post(url, headers=headers, json=payload)  # Sử dụng json thay vì data
    if response.status_code == 200:
        return response.json().get("response", "Không có phản hồi từ API.")
    else:
        return "Lỗi khi gọi API."

# Hàm chính
def main():
    st.title("Chatbot đọc và trả lời từ nhiều tệp PDF bằng Streamlit")

    uploaded_files = st.file_uploader("Chọn các tệp PDF", type="pdf", accept_multiple_files=True)
    combined_text = ""

    if uploaded_files:
        for uploaded_file in uploaded_files:
            combined_text += read_pdf(uploaded_file)
        
        # Kiểm tra độ dài token
        if len(combined_text) > 16385:
            st.error("Nội dung văn bản quá dài, cần rút ngắn lại.")

    st.header("Chat với Chatbot")
    
    if "history" not in st.session_state:
        st.session_state.history = []

    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
        
    if "user_input" not in st.session_state:
            st.session_state.user_input = ""
            
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = {"questions": [], "answers": []}

    # Xử lý việc xóa đoạn chat
    def delete_chat(index):
        if index < len(st.session_state.chat_sessions):
            del st.session_state.chat_sessions[index]
            st.experimental_rerun()

    # Hiển thị danh sách các đoạn chat cũ
    st.sidebar.header("Các đoạn chat cũ")
    for i, session in enumerate(st.session_state.chat_sessions):
        col1, col2 = st.sidebar.columns([8, 1])
        with col1:
            if st.sidebar.button(f"Đoạn chat {i + 1}"):
                st.session_state.current_chat = session
                st.experimental_rerun()
        with col2:
            if st.sidebar.button("X", key=f"delete_{i}", help="Xóa đoạn chat này"):
                delete_chat(i)

    # Hiển thị lịch sử đoạn chat hiện tại
    if st.session_state.current_chat["questions"]:
        for questions, answers in zip(st.session_state.current_chat["questions"], st.session_state.current_chat["answers"]):
            st.markdown(f'<div class="chat-box user">{questions}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-box bot">{answers}</div>', unsafe_allow_html=True)
            st.markdown("---")
    
    # Form for user input to enable Enter key submission
    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn vào đây:", "")
        submit_button = st.form_submit_button(label="Gửi")
        new_chat_button = st.form_submit_button(label="Tạo đoạn chat mới")

        if submit_button:
            response_text = get_response_from_api(user_input, combined_text if uploaded_files else None)
            st.session_state.current_chat["questions"].append(user_input)
            st.session_state.current_chat["answers"].append(response_text)
            st.experimental_rerun()  # Rerun the script to update the UI

        if new_chat_button:
            # Lưu đoạn chat hiện tại vào danh sách các đoạn chat cũ
            if st.session_state.current_chat["questions"]:
                st.session_state.chat_sessions.append(st.session_state.current_chat)
            
            # Tạo đoạn chat mới
            st.session_state.current_chat = {"questions": [], "answers": []}
            st.experimental_rerun()

if __name__ == "__main__":
    main()
