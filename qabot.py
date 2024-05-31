import streamlit as st
import PyPDF2
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
st.markdown(css, unsafe_allow_html=True)

# Function to read PDF content
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to get response from API
def get_response_from_api(question, context=None):
    response = requests.post(
        "http://127.0.0.1:5000/api/chat",
        json={"message": question},
        files={"pdf_file": context} if context else None
    )
    return response.json()["response"]

# Main function to control the interface
def main():
    st.title("Chatbot đọc và trả lời từ nhiều tệp PDF bằng Streamlit")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.header("Lịch sử cuộc trò chuyện")
        if "conversations" not in st.session_state:
            st.session_state.conversations = []

        conversation_labels = [f"Cuộc trò chuyện {i+1}: {conv['initial_question']}" for i, conv in enumerate(st.session_state.conversations)]
        selected_conversation_label = st.selectbox("Chọn cuộc trò chuyện đã lưu", [""] + conversation_labels)

        if selected_conversation_label:
            index = conversation_labels.index(selected_conversation_label)
            st.session_state.current_conversation = st.session_state.conversations[index]

    with col2:
        uploaded_files = st.file_uploader("Chọn các tệp PDF", type="pdf", accept_multiple_files=True)
        combined_text = ""

        if uploaded_files:
            for uploaded_file in uploaded_files:
                combined_text += read_pdf(uploaded_file)
            
            tokens = tokenizer.encode(combined_text)
            if len(tokens) > 16385:
                st.error("Nội dung văn bản quá dài, cần rút ngắn lại.")

        st.header("Chat với Chatbot")
        
        if "current_conversation" not in st.session_state:
            st.session_state.current_conversation = {"initial_question": "", "messages": []}

        if st.session_state.current_conversation["messages"]:
            for message in st.session_state.current_conversation["messages"]:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-box user">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-box bot">{message["content"]}</div>', unsafe_allow_html=True)

        with st.form(key="user_input_form", clear_on_submit=True):
            user_input = st.text_input("Nhập câu hỏi của bạn vào đây:", "")
            submit_button = st.form_submit_button(label="Gửi")
            
            if submit_button:
                context_file = uploaded_files[0] if uploaded_files else None
                response_text = get_response_from_api(user_input, context_file)

                if not st.session_state.current_conversation["initial_question"]:
                    st.session_state.current_conversation["initial_question"] = user_input

                st.session_state.current_conversation["messages"].append({"role": "user", "content": user_input})
                st.session_state.current_conversation["messages"].append({"role": "bot", "content": response_text})

                st.experimental_rerun()  # Rerun the script to update the UI

        # if st.button("Lưu cuộc trò chuyện"):
        #     st.session_state.conversations.append(st.session_state.current_conversation)
        #     st.session_state.current_conversation = {"initial_question": "", "messages": []}
        #     st.experimental_rerun()

        # Define a flag to track if the current conversation has been saved
        conversation_saved = False

        # Add a button to create a new conversation
        if st.button("Tạo cuộc trò chuyện mới"):
            # Save the current conversation only if it hasn't been saved before
            if not conversation_saved and st.session_state.current_conversation["messages"]:
                st.session_state.conversations.append(st.session_state.current_conversation)
                conversation_saved = True
            
            # Start a new conversation
            st.session_state.current_conversation = {"initial_question": "", "messages": []}
            st.experimental_rerun()





if __name__ == "__main__":
    main()
