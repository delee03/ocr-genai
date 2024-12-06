import streamlit as st
from PIL import Image
import boto3
import streamlit.components.v1 as components
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Đảm bảo đường dẫn đúng

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
KNOWLEDGE_BASE_ID = "QSDX9TVNUP"
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0" 

# AWS Bedrock Client
bedrock_client = boto3.client("bedrock-runtime")
bedrock_agent_client = boto3.client("bedrock-agent-runtime")

# Tạo giao diện HTML
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banking Chatbot</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gray-100">
    <main class="min-h-screen bg-gray-100">
        <div class="bg-white">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div class="text-center">
                    <h1 class="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                        Welcome to Banking Chatbot
                    </h1>
                    <p class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                        Resolve your banking issues quickly and easily with our AI-powered assistant.
                    </p>
                </div>
            </div>
        </div>

        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div class="bg-white shadow-xl rounded-lg overflow-hidden">
                <div class="bg-blue-500 px-4 py-5 border-b border-gray-200 sm:px-6">
                    <h3 class="text-lg leading-6 font-medium text-white">
                        Chat with our Banking Assistant
                    </h3>
                </div>
                <div class="bg-white px-4 py-5 sm:p-6">
                    <div class="border rounded-lg h-96 overflow-y-auto mb-4 p-4">
                        <div class="mb-2 text-right">
                            <span class="inline-block bg-blue-500 rounded-lg px-4 py-2 text-white">
                                How can I check my account balance?
                            </span>
                        </div>
                        <div class="mb-2 text-left">
                            <span class="inline-block bg-gray-200 rounded-lg px-4 py-2 text-gray-700">
                                To check your account balance, you can log into your mobile banking app or visit our website. Would you like me to guide you through the process?
                            </span>
                        </div>
                    </div>
                    <div class="mt-4">
                        <div class="flex rounded-md shadow-sm">
                            <input
                                type="text"
                                name="message"
                                id="message"
                                class="focus:ring-blue-500 focus:border-blue-500 flex-1 block w-full rounded-none rounded-l-md sm:text-sm border-gray-300"
                                placeholder="Type your message here..."
                            />
                            <button
                                type="button"
                                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"""


# Configure the Streamlit page settings
st.set_page_config(
    layout="wide",
    page_title="Transaction Assistance Chatbot",
    page_icon="💳"
)

def add_custom_css():
    """Add custom CSS to improve the UI."""
    st.markdown("""<style>
        .main { padding: 2rem; }
        .stButton>button { width: 100%; }
        .upload-text { text-align: center; padding: 2rem; border: 2px dashed #cccccc; border-radius: 5px; }
        .success-text { color: #0c5460; background-color: #d1ecf1; border-color: #bee5eb; padding: 1rem; border-radius: 5px; margin: 1rem 0; }
        .error-text { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; padding: 1rem; border-radius: 5px; margin: 1rem 0; }
        </style>""", unsafe_allow_html=True)

def validate_image(uploaded_file) -> tuple[bool, str]:
    """Validate the uploaded image file."""
    if uploaded_file is None:
        return False, "No file uploaded"
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Please upload {', '.join(ALLOWED_EXTENSIONS)} files"
    
    if uploaded_file.size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024}MB"
    
    return True, ""

def extract_text_from_image(image_file):
    """Function to extract text from an uploaded image using Tesseract OCR."""
    try:
        # Load image as a PIL image
        image = Image.open(image_file)
        
        # Use Tesseract to extract text from image
        extracted_text = pytesseract.image_to_string(image)

        if not extracted_text.strip():
            st.error("Cannot extract text from image.")
            return None
        return extracted_text
    except Exception as e:
        st.error(f"Error processing the image: {str(e)}")
        return None

def retrieve_and_generate(user_request, extracted_text=None, kb_id=KNOWLEDGE_BASE_ID):
    """Query the Knowledge Base via AWS Bedrock API."""
    # Tạo đầu vào cho API, kết hợp text từ input người dùng và OCR
    combined_input = user_request if user_request else ""
    if extracted_text:
        combined_input += f"\nExtracted Text: {extracted_text}"  # Thêm văn bản từ OCR (nếu có)

    # Prepare the payload for Retrieve and Generate API
    payload = {
        "text": combined_input,  # Chỉ cần truyền text vào
    }

    # Gọi API Retrieve and Generate
    try:
        response = bedrock_agent_client.retrieve_and_generate(
            input=payload,
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": MODEL_ARN
                }
            }
        )

        # Phân tích kết quả trả về
        output = response["output"]["text"]
        citations = response.get("citations", [])
        retrieved_references = [
            ref["retrievedReferences"] for ref in citations if "retrievedReferences" in ref
        ]
        return output, retrieved_references

    except Exception as e:
        st.error(f"Error calling Retrieve and Generate API: {str(e)}")
        return None, None
    
def render_chat_interface():
    """Tích hợp giao diện HTML vào Streamlit."""
    html_code = """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Banking Chatbot</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gray-100">
        <main class="min-h-screen bg-gray-100">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div class="bg-white shadow-xl rounded-lg overflow-hidden">
                    <div class="bg-blue-500 px-4 py-5 border-b border-gray-200 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-white">
                            Chat with our Banking Assistant
                        </h3>
                    </div>
                    <div class="bg-white px-4 py-5 sm:p-6">
                        <div class="border rounded-lg h-96 overflow-y-auto mb-4 p-4" id="chat-container">
                            <!-- Các tin nhắn sẽ được hiển thị ở đây -->
                        </div>
                        <div class="mt-4">
                            <div class="flex rounded-md shadow-sm">
                                <input
                                    type="text"
                                    id="message-input"
                                    class="focus:ring-blue-500 focus:border-blue-500 flex-1 block w-full rounded-none rounded-l-md sm:text-sm border-gray-300"
                                    placeholder="Type your message here..."
                                />
                                <button
                                    type="button"
                                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                    onclick="sendMessage()"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                        <div class="mt-4">
                            <div class="flex items-center justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                                <div class="space-y-1 text-center">
                                    <svg
                                        class="mx-auto h-12 w-12 text-gray-400"
                                        stroke="currentColor"
                                        fill="none"
                                        viewBox="0 0 48 48"
                                        aria-hidden="true"
                                    >
                                        <path
                                            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                                            stroke-width="2"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                        />
                                    </path>
                                </svg>
                                <div class="flex text-sm text-gray-600">
                                    <label
                                        for="file-upload"
                                        class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                                    >
                                        <span>Upload a file</span>
                                        <input id="file-upload" name="file-upload" type="file" class="sr-only" onchange="uploadFile()" />
                                    </label>
                                    <p class="pl-1">or drag and drop</p>
                                </div>
                                <p class="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script>
            // Gửi tin nhắn văn bản
    function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();

        if (message !== '') {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('mb-2', 'text-right');  // Thêm class để căn phải cho tin nhắn người dùng
            messageDiv.innerHTML = `
                <span class="inline-block bg-blue-500 rounded-lg px-4 py-2 text-white">
                    ${message}
                </span>
            `;
            chatContainer.appendChild(messageDiv);
            messageInput.value = '';  // Xóa input sau khi gửi
            chatContainer.scrollTop = chatContainer.scrollHeight;  // Tự động cuộn xuống cuối
        }
    }

    // Xử lý tải tệp hình ảnh
    function uploadFile() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const chatContainer = document.getElementById('chat-container');
            const imageDiv = document.createElement('div');
            imageDiv.classList.add('mb-2', 'text-right'); // Căn phải cho hình ảnh
            
            // Hiển thị hình ảnh với CSS tương tự tin nhắn văn bản
            imageDiv.innerHTML = `
                <span class="inline-block bg-blue-500 rounded-lg p-2">
                    <img src="${e.target.result}" class="max-w-xs rounded-lg shadow-lg" alt="Uploaded Image" />
                </span>
            `;
            chatContainer.appendChild(imageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight; // Tự động cuộn xuống cuối
        }
        reader.readAsDataURL(file); // Đọc tệp hình ảnh dưới dạng URL
    }
}


    // Hàm xử lý kết quả từ Tesseract hoặc Knowledge Base
    function displayResultFromBot(resultText) {
        const chatContainer = document.getElementById('chat-container');
        const botMessageDiv = document.createElement('div');
        botMessageDiv.classList.add('mb-2', 'text-left');  // Căn trái cho tin nhắn từ bot
        botMessageDiv.innerHTML = `
            <span class="inline-block bg-gray-200 rounded-lg px-4 py-2 text-gray-700">
                ${resultText}
            </span>
        `;
        chatContainer.appendChild(botMessageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;  // Tự động cuộn xuống cuối
    }
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=800, scrolling=True)

def main():
    # """Main function to run the app."""
    # st.title("Transaction Assistance Chatbot")
    # # File upload section
    # uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    # user_input = st.text_area("Enter your query:")

    # # Giao diện chat
    # render_chat_interface()

    # # Khởi tạo extracted_text là None trước
    # extracted_text = None

    # # Validate file if uploaded
    # if uploaded_file is not None:
    #     is_valid, error_message = validate_image(uploaded_file)
    #     if not is_valid:
    #         st.error(error_message)
    #     else:
    #         extracted_text = extract_text_from_image(uploaded_file)        
    #         if extracted_text:
    #             st.success("Text extracted from image successfully.")
    #             st.text_area("Extracted Text", extracted_text)

    # # Query button
    # if st.button("Submit"):
    #     # Nếu cả hai user_input và extracted_text đều trống, thông báo lỗi
    #     if not user_input and not extracted_text:
    #         st.error("Please provide either a query or an image.")
    #     else:
    #         # Gọi hàm retrieve_and_generate, truyền None nếu không có text từ người dùng hoặc ảnh
    #         response, references = retrieve_and_generate(user_input or None, extracted_text)
    #         if response:
    #             st.write("Response: ", response)
    #             if references:
    #                 st.write("References: ", references)
    st.title("Banking Chatbot")
    
    # Giao diện chat
    render_chat_interface()
    
    # # Tính năng Upload File
    # uploaded_file = st.file_uploader("Upload your image here", type=["jpg", "jpeg", "png"])
    
    # if uploaded_file is not None:
    #     # Xử lý ảnh bằng OCR
    #     image = Image.open(uploaded_file)
    #     extracted_text = pytesseract.image_to_string(image)
    #     st.text_area("Extracted Text", extracted_text, height=200)

    # # Nhập liệu tin nhắn và gửi
    # user_message = st.text_input("Enter your message:")
    # if st.button("Send"):
    #     if user_message:
    #         st.success(f"Message sent: {user_message}")
    #     else:
    #         st.error("Please enter a message.")

if __name__ == "__main__":
    main()
