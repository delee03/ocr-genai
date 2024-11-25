# OCR-GenAI

A powerful OCR (Optical Character Recognition) system powered by Claude 3, implemented with both direct Boto3 and LangChain approaches.

## Project Structure

```
.
├── app.py                    # Main application entry point
├── claude3_boto3_ocr.py      # Boto3 implementation
├── claude3_langchain_ocr.py  # LangChain implementation
└── requirements.txt          # Project dependencies
```

## Features

- Dual implementation (Boto3 and LangChain)
- High-accuracy text extraction
- Multi-language support
- Table structure recognition
- Layout preservation
- Image preprocessing
- Format conversion
- Batch processing

## Prerequisites

- Python 3.12+
- AWS Account with Bedrock access
- Claude 3 model access
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/OCR-GenAI.git
cd OCR-GenAI
```

2. Create virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the root directory:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
MODEL_NAME=claude-3-sonnet-20240229
```

## Usage

### Using Boto3 Implementation

```python
from claude3_boto3_ocr import extract_text

# Extract text from image
text = extract_text(
    image_path="path/to/image.jpg",
    language="english",
    preserve_layout=True
)
```

### Using LangChain Implementation

```python
from claude3_langchain_ocr import process_document

# Process document with LangChain
result = process_document(
    document_path="path/to/document.pdf",
    extraction_type="structured",
    include_tables=True
)
```

### Running the Application

```bash
python app.py --input path/to/file --output path/to/result --method boto3
```

## Supported Formats

Input:
- Images: JPG, PNG, TIFF, BMP
- Documents: PDF, DOCX
- Scanned documents
- Screenshots

Output:
- Plain text
- JSON
- Structured XML
- Markdown
- CSV (for tables)

## Features in Detail

### 1. Text Recognition
- Character accuracy >99%
- Multi-language support
- Font variety handling
- Special character recognition

### 2. Layout Analysis
- Table detection
- Column recognition
- List formatting
- Page segmentation
- Margin preservation

### 3. Image Preprocessing
- Noise reduction
- Contrast enhancement
- Skew correction
- Resolution optimization

## Best Practices

1. Image Preparation
- Minimum 300 DPI
- Good contrast
- Clear lighting
- Minimal noise

2. Processing Guidelines
- Batch similar documents
- Use appropriate format
- Enable layout preservation
- Validate output

## Performance Optimization

- Batch processing
- Image compression
- Cache results
- Parallel processing
- Resource management

## Error Handling

Common issues and solutions:
- Poor image quality
- Format incompatibility
- API rate limits
- Memory constraints
- Processing timeout

## Security

- Input validation
- File sanitization
- Access control
- Data encryption
- Secure storage

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.