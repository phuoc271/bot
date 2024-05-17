import streamlit as st
import PyPDF2
import openai
import os

from transformers import GPT2Tokenizer


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokens = tokenizer.encode("Your long text here")

if len(tokens) > 16385:
    print("Văn bản quá dài, cần rút ngắn.")

st.title("Chatbot đọc và trả lời từ tệp PDF bằng Streamlit")

# Load API key from apikey.txt file
with open("apikey.txt", "r") as f:
    openai.api_key = f.readline().strip()

# Function to read PDF content
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

# Function to call OpenAI API / ChatGPT
def get_response_from_chatgpt(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    print(response)  # Print response structure for inspection

    response_text = response.choices[0]["message"]["content"]  # Extract content from response
    return response_text


# Main function to control the interface
def main():
    user_input = st.text_input("Nhập câu hỏi của bạn vào đây:")
    file = st.file_uploader("Chọn một tệp PDF", type="pdf")

    if file is not None:
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(file.read())
        
        pdf_text = read_pdf("temp.pdf")
        os.remove("temp.pdf")  # Remove the temporary file after reading
        
        st.write("Nội dung PDF:")
        st.write(pdf_text)

        if st.button("Hỏi chatbot"):
            user_input += " " + pdf_text  # Combine user input with PDF text
            response_text = get_response_from_chatgpt(user_input)
            st.write(f"Câu trả lời từ chatbot: {response_text}")

if __name__== "__main__":
    main()