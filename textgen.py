import streamlit as st
import openai

st.title("Mì AI - Tích hợp ChatGPT vào ứng dụng Python")

# Load API key from apikey.txt file
with open("apikey.txt", "r") as f:
    openai.api_key = f.readline().strip()

# Function to call OpenAI API / ChatGPT
def get_response_from_chatgpt(user_question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": user_question}
        ]
    )

    print(response)  # In ra phản hồi để xem cấu trúc

    response_text = response.choices[0]["message"]["content"]  # Trích xuất nội dung từ phản hồi
    return response_text



# Main function to control the interface
def main():
    user_question = st.text_input("Nhập câu hỏi vào đây:")
    if st.button("Chat với em đi"):
        response_text = get_response_from_chatgpt(user_question)
        st.write(f"Câu trả lời: {response_text}")

if __name__ == "__main__":
    main()
