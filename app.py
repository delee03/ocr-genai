#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import base64
import io
import streamlit as st
from PIL import Image
import boto3
import json

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
KNOWLEDGE_BASE_ID = "QSDX9TVNUP"  # Replace with your Knowledge Base ID
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0" 
#Knowledge Base Model arn of Foundation Model - Sonet 3.0

# AWS Bedrock Client
bedrock_client = boto3.client("bedrock-runtime")
bedrock_agent_client = boto3.client("bedrock-agent-runtime")  # For Retrieve and Generate

def set_page_config():
    """Configure the Streamlit page settings."""
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
        return False, f"Invalid file type. Please upload {', '.join(ALLOWED_EXTENSIONS)}"
    if uploaded_file.size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024}MB"
    return True, ""


def extract_text_from_image(base64_image):
    """Stub function to simulate OCR text extraction from an image."""
    # Replace with your actual OCR logic or API call.
    return "Extracted text from the uploaded image."


def retrieve_and_generate(user_request, kb_id):
    """
    Use Bedrock Retrieve and Generate API to get response based on the Knowledge Base.
    """
    try:
        response = bedrock_agent_client.retrieve_and_generate(
            input={"text": user_request},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": MODEL_ARN
                }
            }
        )

        # Parse the response to extract generated text and citations
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

        # Use extracted text or user input
        query = extracted_text or user_request

        # Retrieve and generate response
        with st.spinner("Processing your request..."):
            response_text, references = retrieve_and_generate(query, KNOWLEDGE_BASE_ID)
            if response_text:
                st.success("Generated Answer:")
                st.write(response_text)
                if references:
                    st.write("References:")
                    for ref in references:
                        st.write(ref)
            else:
                st.error("No response generated. Please check your input or Knowledge Base configuration.")


if __name__ == "__main__":
    main()
