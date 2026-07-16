from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Tải cấu hình biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Hỗ trợ phân quyền truy cập Cross-Origin

# Khởi tạo API Key từ file .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Đoạn System Instruction đã tối ưu hóa nghiêm ngặt và viết hay
system_instruction = (
    "Bạn là một chuyên viên tư vấn nội bộ và bán hàng chuyên nghiệp của công ty. "
    "Nhiệm vụ của bạn là trả lời các câu hỏi dựa TRÊN DUY NHẤT nguồn dữ liệu (database/context) được cung cấp. "
    
    "\n--- PHÂN LOẠI CÂU HỎI BẮT BUỘC ---"
    "\n- ĐỐI VỚI CÂU CHÀO HỎI / XÃ GIAO: Nếu người dùng chào hỏi (ví dụ: 'chào bạn', 'hello', 'hi'), cảm ơn, hoặc hỏi các câu xã giao thông thường không liên quan đến sản phẩm/luật lệ công ty, bạn hãy trả lời một cách thân thiện, vui vẻ và lịch sự ngắn gọn. TUYỆT ĐỐI KHÔNG nhắc nhở họ tải file trong trường hợp này."
    "\n- ĐỐI VỚI CÂU HỎI TƯ VẤN SẢN PHẨM/LUẬT LỆ:"
    "\n  + Nếu KHÔNG CÓ dữ liệu được cung cấp (context trống rỗng): Bạn TUYỆT ĐỐI KHÔNG ĐƯỢC giải thích, định nghĩa hay cung cấp bất kỳ kiến thức chung nào từ Internet (không được tự nói về các tầng hương gỗ, hương hoa, quy định chung...). Bạn CHỈ ĐƯỢC PHÉP trả lời duy nhất câu sau: 'Hiện tại tôi chưa nhận được tài liệu hướng dẫn hoặc danh sách sản phẩm nào từ bạn. Bạn vui lòng tải file PDF/JSON lên ở thanh bên (Sidebar) để tôi có thể hỗ trợ tư vấn chính xác nhất nhé!'"
    "\n  + Nếu CÓ dữ liệu: Tiến hành tư vấn bình thường theo đúng tài liệu."
    
    "\n--- NGUYÊN TẮC HOẠT ĐỘNG ---"
    "\n1. KHÔNG LẤY THÔNG TIN NGOÀI: Tuyệt đối không sử dụng kiến thức bên ngoài dữ liệu được cung cấp để tự bịa ra thông tin sản phẩm hay quy định. "
    "Nếu thông tin tư vấn không có trong file, hãy lịch sự từ chối: "
    "'Xin lỗi, thông tin này hiện nằm ngoài phạm vi tài liệu hướng dẫn của tôi. Bạn có cần hỗ trợ gì khác không?'"
    
    "\n2. TƯ VẤN ĐẦY ĐỦ VÀ TRỰC QUAN: Khi khách hàng hỏi về sản phẩm, hãy cung cấp đầy đủ các thông tin hữu ích có sẵn trong tài liệu như: tên sản phẩm, các tầng mùi hương, đặc tính nổi bật, giá bán và công dụng an toàn cho da. Tránh viết quá ngắn gọn làm mất đi các chi tiết quan trọng của sản phẩm."
    
    "\n3. ĐỊNH DẠNG LINK MẪU CHUẨN: Bắt buộc đính kèm link sản phẩm dạng [Tên sản phẩm](url) ngay sau phần mô tả hoặc liệt kê ở cuối câu trả lời nếu trong dữ liệu có cung cấp link đó. Không được tự ý chế link."
    
    "\n4. TRÌNH BÀY ĐẸP MẮT: Sử dụng định dạng danh sách (1., 2., 3. hoặc các dấu đầu dòng) để phân tách rõ ràng từng sản phẩm giúp người dùng dễ đọc giống như một chuyên viên chuyên nghiệp."
)

# Hàm gọi API Groq (Llama 3.3)
def call_groq(prompt_message, context_text=""):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_prompt = f"Dữ liệu tham khảo (Database/Context):\n{context_text}\n\nCâu hỏi khách hàng: {prompt_message}" if context_text else prompt_message
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": full_prompt}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Hàm gọi API Gemini (Đã nâng cấp lên Gemini 3.1 Flash)
def call_gemini(prompt_message, context_text=""):
    # Đã lên đời Gemini 3.1 chuẩn chỉ theo ý bạn!
    model_name = "gemini-3.1-flash-lite"  
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    full_prompt = f"Dữ liệu tham khảo (Database/Context):\n{context_text}\n\nCâu hỏi khách hàng: {prompt_message}" if context_text else prompt_message
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": system_instruction}
            ]
        },
        "generationConfig": {
            "temperature": 0.3
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    context = data.get("context", "")
    model_choice = data.get("model", "Tự động (Auto)")
    
    if not message:
        return jsonify({"response": "Bạn chưa nhập câu hỏi."}), 400

    # TH 1: Ép chạy duy nhất Groq
    if model_choice == "Groq (Llama 3.3)":
        try:
            ai_response = call_groq(message, context)
            return jsonify({"response": ai_response})
        except Exception as e:
            return jsonify({"response": f"Lỗi khi kết nối với Groq: {str(e)}"}), 500

    # TH 2: Ép chạy duy nhất Gemini
    elif model_choice == "Gemini (2.0 Flash)":
        try:
            ai_response = call_gemini(message, context)
            return jsonify({"response": ai_response})
        except Exception as e:
            return jsonify({"response": f"Lỗi khi kết nối với Gemini: {str(e)}"}), 500

    # TH 3: Chế độ Tự động (Auto) - Cực kỳ an toàn, lỗi bên này nhảy sang bên kia
    else:
        try:
            # Ưu tiên gọi Groq trước cho nhanh
            ai_response = call_groq(message, context)
            return jsonify({"response": ai_response})
        except Exception as groq_error:
            print(f"Groq dính lỗi: {groq_error}. Tự động chuyển kênh sơ cua sang Gemini...")
            try:
                # Nếu Groq sập hoặc hết lượt dùng (Rate Limit), chạy Gemini dự phòng
                ai_response = call_gemini(message, context)
                return jsonify({"response": ai_response})
            except Exception as gemini_error:
                return jsonify({
                    "response": f"Cả hai hệ thống AI đều đang bận hoặc quá tải. (Lỗi Groq: {groq_error} | Lỗi Gemini: {gemini_error})"
                }), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)