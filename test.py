import streamlit as st
import openai
import fitz  # PyMuPDF
import os

st.title("ChatAI")

# Load API key from apikey.txt file
with open("apikey.txt", "r") as f:
    openai.api_key = f.readline().strip()
    
# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to estimate the number of tokens in the text
def estimate_tokens(text):
    # Simple token estimation assuming an average of 4 characters per token and spaces
    return len(text) // 4

# Function to trim text to fit within token limit
def trim_text_to_token_limit(text, max_tokens):
    words = text.split()
    current_tokens = 0
    trimmed_text = []

    for word in words:
        current_tokens += estimate_tokens(word) + 1
        if current_tokens > max_tokens:
            break
        trimmed_text.append(word)

    return ' '.join(trimmed_text)

# Function to call OpenAI API / ChatGPT
def get_response_from_chatgpt(user_question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Trả lời chính xác trong tệp pdf đã đưa"},
            {"role": "user", "content": user_question}
        ]
    )

    print(response)  # In ra phản hồi để xem cấu trúc

    response_text = response.choices[0]["message"]["content"]  # Trích xuất nội dung từ phản hồi
    return response_text



# Main function to control the interface
def main():
    data_dir = "data"  # Đường dẫn tới thư mục chứa các tệp PDF
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]

    if pdf_files:
        selected_pdf = st.selectbox("Chọn tệp PDF để đọc", pdf_files)
        pdf_path = os.path.join(data_dir, selected_pdf)

        pdf_text = extract_text_from_pdf(pdf_path)
        
        user_question = st.text_input("Nhập câu hỏi vào đây:")
        estimated_user_question_tokens = estimate_tokens(user_question)
        
        max_allowed_tokens = 16384  # Model limit
        buffer_tokens = 1000  # Tokens reserved for the response and system message
        available_tokens_for_pdf = max_allowed_tokens - buffer_tokens - estimated_user_question_tokens
        
        # Trim PDF content to fit within the available tokens
        if available_tokens_for_pdf > 0:
            trimmed_pdf_text = trim_text_to_token_limit(pdf_text, available_tokens_for_pdf)
        else:
            trimmed_pdf_text = "Câu hỏi quá dài, không đủ dung lượng cho nội dung PDF."
        
        st.text_area("Nội dung PDF:", trimmed_pdf_text, height=300)
        
        if st.button("Chat"):
            # Include trimmed PDF text in the user question context
            user_question_with_pdf = f"Nội dung PDF:\n{trimmed_pdf_text}\n\nCâu hỏi: {user_question}"
        
            response_text = get_response_from_chatgpt(user_question)
            st.write(f"Câu trả lời: {response_text}")
            
    else:
        st.write("Không có tệp PDF nào trong thư mục.")
        
if __name__ == "__main__":
    main()
