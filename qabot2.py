import streamlit as st
import PyPDF2
import json
import requests

css = """
<style>
.chat-box {
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 12px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.5;
}
.user {
    text-align: right;
    color: white;
    background-color: #444444;
    margin-left: 20%;
    border-bottom-right-radius: 2px;
}
.bot {
    text-align: left;
    color: #f1f1f1;
    background-color: #1a1a1a;
    margin-right: 20%;
    border: 1px solid #333333;
    border-bottom-left-radius: 2px;
}
div[data-testid="stForm"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-end !important; 
    gap: 10px !important;
    flex-wrap: nowrap !important;
}
div[data-testid="stForm"] div.stTextInput {
    flex-grow: 1 !important;
    width: auto !important;
    margin-bottom: 0 !important; 
}
div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
    display: inline-flex !important;  
    flex-direction: row !important;
    width: auto !important;          
    margin: 0 !important;
    gap: 10px !important;            
    flex-shrink: 0 !important;      
}
div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div {
    width: auto !important;
    min-width: unset !important;
    max-width: unset !important;
    flex: none !important;
}
div[data-testid="stFormSubmitButton"] button {
    height: 40px !important;
    padding: 0px 16px !important;
    white-space: nowrap !important;
    margin: 0 !important;
}
div[data-testid="stForm"] div[data-testid="element-container"] {
    margin-bottom: 0 !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

def read_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        return f"Lỗi đọc PDF: {str(e)}"

def read_json(file):
    try:
        data = json.load(file)
        return data
    except Exception as e:
        return {}

def get_response_from_api(message, context=None, model_choice="Tự động (Auto)"):
    url = "http://127.0.0.1:5000/api/chat"
    payload = {
        "message": message,
        "context": context,
        "model": model_choice  
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "Không có phản hồi từ API.")
        else:
            return f"Lỗi Backend Flask: Lỗi HTTP {response.status_code}"
    except Exception as e:
        return f"Không thể kết nối tới Backend Flask: {str(e)}"

def main():
    st.title("Chatbot Tư Vấn Doanh Nghiệp (Groq & Gemini)")
    
    st.sidebar.header("Cấu hình AI & Tài liệu")
    
    model_choice = st.sidebar.selectbox(
        "Chọn Model AI tư vấn:",
        ["Tự động (Auto)", "Groq (Llama 3.3)", "Gemini (3.1 Flash Lite)"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Tải lên Tài liệu (PDF/JSON)")
    st.sidebar.markdown(
        "<small style='color: #888888;'>"
        "• Giới hạn dung lượng: <b>Tối đa 1 MB / file</b><br>"
        "• Giới hạn nội dung: <b>Tối đa 15,000 ký tự văn bản</b>"
        "</small>", 
        unsafe_allow_html=True
    )
    
    uploaded_files = st.sidebar.file_uploader(
        "Chọn các tệp dữ liệu hướng dẫn cho chatbot", 
        type=["pdf", "json"], 
        accept_multiple_files=True
    )

    combined_text = ""
    is_valid_files = True

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.size > 1048576:
                st.sidebar.error(f"File {uploaded_file.name} vượt quá giới hạn 1 MB!")
                is_valid_files = False
                break
            
            if uploaded_file.name.endswith(".pdf"):
                combined_text += read_pdf(uploaded_file) + "\n"
            elif uploaded_file.name.endswith(".json"):
                json_data = read_json(uploaded_file)
                combined_text += json.dumps(json_data, indent=4, ensure_ascii=False) + "\n"
        
        if is_valid_files:
            total_chars = len(combined_text)
            if total_chars > 15000:
                st.sidebar.error(
                    f"Tổng văn bản trích xuất quá lớn ({total_chars} ký tự). "
                    "Vui lòng rút ngắn nội dung tài liệu xuống dưới 15,000 ký tự."
                )
                is_valid_files = False
            else:
                st.sidebar.success(
                    f"Đã nạp thành công: {len(uploaded_files)} file.\n"
                    f"Tổng độ dài: {total_chars}/15,000 ký tự."
                )

    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
        
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = {"questions": [], "answers": []}

    def delete_chat(index):
        if index < len(st.session_state.chat_sessions):
            del st.session_state.chat_sessions[index]
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Đoạn chat đã lưu")
    for i, session in enumerate(st.session_state.chat_sessions):
        col1, col2 = st.sidebar.columns([8, 2])
        with col1:
            if st.sidebar.button(f"Đoạn chat {i + 1}", key=f"session_btn_{i}"):
                st.session_state.current_chat = session
                st.rerun()
        with col2:
            if st.sidebar.button("X", key=f"delete_{i}", help="Xóa cuộc trò chuyện này"):
                delete_chat(i)

    st.subheader("Trò chuyện")
    if st.session_state.current_chat["questions"]:
        for q, a in zip(st.session_state.current_chat["questions"], st.session_state.current_chat["answers"]):
            st.markdown(f'<div class="chat-box user"><b>Bạn:</b><br>{q}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chat-box bot"><b>Trợ lý:</b></div>', unsafe_allow_html=True)
            st.markdown(a)
            st.markdown("---")
    else:
        st.info("Hãy bắt đầu cuộc hội thoại bằng cách nhập câu hỏi phía dưới!")

    with st.form(key="user_input_form", clear_on_submit=True):
        user_input = st.text_input("Nhập câu hỏi của bạn:", "")
        col_send, col_new = st.columns([1, 1])
        
        with col_send:
            submit_button = st.form_submit_button(label="Gửi")
        with col_new:
            new_chat_button = st.form_submit_button(label="Tạo đoạn chat mới")

        if submit_button and user_input.strip() != "":
            if not is_valid_files:
                st.warning("Hệ thống đã chặn gửi tài liệu do vi phạm giới hạn kích thước. Vui lòng kiểm tra lại file ở Sidebar.")
                response_text = get_response_from_api(user_input, None, model_choice)
            else:
                response_text = get_response_from_api(user_input, combined_text if uploaded_files else None, model_choice)
            
            st.session_state.current_chat["questions"].append(user_input)
            st.session_state.current_chat["answers"].append(response_text)
            st.rerun()

        if new_chat_button:
            if st.session_state.current_chat["questions"]:
                st.session_state.chat_sessions.append(st.session_state.current_chat)
            st.session_state.current_chat = {"questions": [], "answers": []}
            st.rerun()

if __name__ == "__main__":
    main()