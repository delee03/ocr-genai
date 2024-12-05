+------------------+      +-------------------+     +------------------------+
|   User (Actor)   | ---> | Streamlit Web UI  | ---> | Tesseract OCR (Python) |
+------------------+      +-------------------+     +------------------------+
                                  |                            |
                                  v                            v
                      +-------------------------+      +----------------------------+
                      |   Extracted Text from   | ---> |   Text Embedding (Titan    |
                      |   Image (OCR Processed)  |      |   Text Embeddings v2)      |
                      +-------------------------+      +----------------------------+
                                  |
                                  v
                     +-----------------------------+
                     |   Retrieve & Generate API   |
                     |   (AWS Bedrock: Anthropic   |
                     |   Claude 3.5, Knowledge     |
                     |   Base with OpenSearch)     |
                     +-----------------------------+
                                  |
                                  v
                       +-------------------------+
                       |    AWS OpenSearch        |
                       |    (Vector Search)       |
                       +-------------------------+
                                  |
                                  v
                       +-----------------------------+
                       |    Response to User (UI)   |
                       +-----------------------------+
