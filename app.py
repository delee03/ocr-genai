#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import base64
import io
import streamlit as st
from PIL import Image
import claude3_boto3_ocr as llm_app
import boto3
import json

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# AWS Bedrock and Knowledge Base configuration
KNOWLEDGE_BASE_NAME = "TransactionSupportKB"  # Knowledge Base name
bedrock_client = boto3.client("bedrock-runtime")


def set_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        layout="wide",
        page_title="Transaction Assistance Chatbot",
        page_icon="💳"
    )


def add_custom_css():
    """Add custom CSS to improve the UI."""
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .upload-text {
            text-align: center;
            padding: 2rem;
            border: 2px dashed #cccccc;
            border-radius: 5px;
        }
        .success-text {
            color: #0c5460;
            background-color: #d1ecf1;
            border-color: #bee5eb;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .error-text {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)


def validate_image(uploaded_file) -> tuple[bool, str]:
    """Validate the uploaded image file."""
    if uploaded_file is None:
        return False, "No file uploaded"
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Please upload {', '.join(ALLOWED_EXTENSIONS)}"
    if uploaded_file.size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE/1024/1024}MB"
    return True, ""


def extract_text_from_image(base64_image):
    """Call Claude OCR to extract text from image."""
    chain = llm_app.build_chain()
    return llm_app.run_chain(chain, base64_image)


def create_messages_payload(user_request):
    """
    Create a JSON payload for the Anthropic Claude model.
    """
    # Prepare the user query as part of the 'messages' array
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_request
                }
            ]
        }
    ]
    
    # Construct the payload
    payload = {
        "anthropic_version": "bedrock-2023-05-31",  # Mandatory version key
        "max_tokens": 1000,  # Maximum number of tokens in the response
        "messages": messages  # Array of message objects
    }
    return payload

def send_to_bedrock_anthropic_api(payload):
    """
    Send a request to AWS Bedrock using the Anthropic Claude model.
    """
    try:
        # Send the request to the Bedrock API
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Replace with your correct model ID
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)  # Properly formatted JSON payload
        )

        # Parse the raw response
        raw_response = response["body"].read().decode("utf-8")
        st.write("Raw Response from Anthropic Claude:", raw_response)  # Debugging log

        # Extract and return the completion text
        result = json.loads(raw_response)
        completions = result.get("completions", [])
        if not completions:
            return "No response generated. Check Knowledge Base alignment and query structure."
        return completions[0].get("data", {}).get("text", "No response text found.")
    except Exception as e:
        st.error(f"Error calling Bedrock API: {str(e)}")
        return f"Error: {str(e)}"


def main():
    set_page_config()
    add_custom_css()

    # Header section
    st.title("💳 Transaction Assistance Chatbot")
    st.markdown("Upload an image and provide additional details about your issue.")

    # Input Form
    with st.form("user_input_form"):
        uploaded_file = st.file_uploader("Upload an image (optional)", type=ALLOWED_EXTENSIONS)
        user_request = st.text_area("Describe your issue (e.g., I forgot my bank account password)", "")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not user_request.strip() and not uploaded_file:
            st.warning("Please upload an image or enter a text request.")
            return

        # Handle uploaded image
        base64_image = None
        extracted_text = None
        if uploaded_file:
            is_valid, error_message = validate_image(uploaded_file)
            if not is_valid:
                st.error(error_message)
                return
            try:
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format=image.format)
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
                extracted_text = extract_text_from_image(base64_image)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                st.write("Extracted Text:", extracted_text)
            except Exception as e:
                st.error(f"Error processing the image: {str(e)}")

        # Create payload and send to Bedrock
        payload = create_messages_payload(user_request)
        st.write("Payload sent to Knowledge Base:", payload)

        with st.spinner("Processing your request..."):
            try:
                answer = send_to_bedrock_anthropic_api(payload)
                st.success("Generated Answer:")
                st.write(answer)
            except RuntimeError as e:
                st.error(f"Error from Bedrock API: {str(e)}")


if __name__ == "__main__":
    main()
