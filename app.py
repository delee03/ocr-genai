#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import base64
import io
import streamlit as st
from PIL import Image
import claude3_boto3_ocr as llm_app
from typing import Optional
import time

# Constants
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

def set_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        layout="wide",
        page_title="Document Understanding System",
        page_icon="📄"
    )

def add_custom_css():
    """Add custom CSS to improve the UI"""
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
    """
    Validate the uploaded image file
    Returns: (is_valid: bool, error_message: str)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Please upload {', '.join(ALLOWED_EXTENSIONS)}"
    
    if uploaded_file.size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE/1024/1024}MB"
    
    return True, ""

def process_image(image: Image.Image, max_size: tuple[int, int] = (800, 800)) -> Image.Image:
    """Resize and process the image if needed"""
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size)
    return image

def display_image_info(image: Image.Image):
    """Display image information in a formatted way"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Width", f"{image.size[0]}px")
    with col2:
        st.metric("Height", f"{image.size[1]}px")
    with col3:
        st.metric("Format", image.format)

def main():
    try:
        chain = llm_app.build_chain()
    except Exception as e:
        st.error(f"Error initializing the application: {str(e)}")
        return

    set_page_config()
    add_custom_css()

    # Header section
    st.title("📄 Document Understanding System")
    st.markdown("""
        This application helps you extract and analyze text from images using OCR technology.
        Upload your document to get started!
    """)

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            help="Minimum confidence score for text detection"
        )
        show_debug_info = st.checkbox("Show Debug Information", value=False)

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=ALLOWED_EXTENSIONS,
            help=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

        if uploaded_file is not None:
            is_valid, error_message = validate_image(uploaded_file)
            
            if not is_valid:
                st.error(error_message)
                return

            try:
                image = Image.open(uploaded_file)
                image = process_image(image)
                st.image(image, caption=uploaded_file.name, use_column_width=True)
                
                if show_debug_info:
                    display_image_info(image)

                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format=image.format)
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                return

    with col2:
        st.subheader("📑 Extracted Results")
        
        if uploaded_file is not None:
            with st.spinner("Processing document..."):
                try:
                    # Add progress bar for better UX
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # Run OCR
                    text = llm_app.run_chain(chain, base64_image)
                    
                    # Display results
                    st.success("Document processed successfully!")
                    
                    # Create tabs for different views
                    tab1, tab2 = st.tabs(["Extracted Text", "Analysis"])
                    
                    with tab1:
                        st.markdown("### 📝 Extracted Text")
                        st.markdown(text)
                        
                        # Add copy button
                        if st.button("📋 Copy to Clipboard"):
                            st.write("Text copied to clipboard!")
                            st.session_state["clipboard"] = text
                    
                    with tab2:
                        st.markdown("### 📊 Document Analysis")
                        # Add some basic text analysis
                        word_count = len(text.split())
                        char_count = len(text)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Word Count", word_count)
                        with col2:
                            st.metric("Character Count", char_count)

                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
                    if show_debug_info:
                        st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ using Streamlit and Claude</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()