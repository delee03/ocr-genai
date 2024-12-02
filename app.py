import base64
import io
import streamlit as st
import time
from PIL import Image
import boto3
import json
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

def main():
    """Main function to run the app."""
    st.title("Transaction Assistance Chatbot")

    # # File upload section
    # uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    # user_input = st.text_area("Enter your query:")

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
    #     if not user_input and not extracted_text:
    #         st.error("Please provide either a query or an image.")
    #     else:
    #         # Gọi hàm retrieve_and_generate, nếu không có ảnh thì chỉ gửi user_input
    #         response, references = retrieve_and_generate(user_input or None, extracted_text or None)
    #         if response:
    #             st.write("Response: ", response)
    #             if references:
    #                 st.write("References: ", references)

  

    # File upload section
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    user_input = st.text_area("Enter your query:")

    # Khởi tạo extracted_text là None trước
    extracted_text = None

    # Validate file if uploaded
    if uploaded_file is not None:
        is_valid, error_message = validate_image(uploaded_file)
        if not is_valid:
            st.error(error_message)
        else:
            extracted_text = extract_text_from_image(uploaded_file)        
            if extracted_text:
                st.success("Text extracted from image successfully.")
                st.text_area("Extracted Text", extracted_text)

    # Query button
    if st.button("Submit"):
        # Nếu cả hai user_input và extracted_text đều trống, thông báo lỗi
        if not user_input and not extracted_text:
            st.error("Please provide either a query or an image.")
        else:
            # Gọi hàm retrieve_and_generate, truyền None nếu không có text từ người dùng hoặc ảnh
            response, references = retrieve_and_generate(user_input or None, extracted_text)
            if response:
                st.write("Response: ", response)
                if references:
                    st.write("References: ", references)

if __name__ == "__main__":
    main()
