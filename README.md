# 🛡️ PrivateDocAI-Analyzer

A privacy-focused, offline AI document analysis assistant with multi-modal input support.

## Features

- 📄 **PDF Analysis**: Quick summary or deep scan of entire documents
- 📝 **Text Processing**: Analyze pasted text or emails
- 🖼️ **OCR Support**: Extract and analyze text from images/screenshots
- 💬 **Interactive Q&A**: Ask follow-up questions about analyzed documents
- 📥 **Export Reports**: Download summaries as PDF
- 🔒 **100% Offline**: All processing happens locally on your machine

## Requirements

- Python 3.8+
- 8GB RAM minimum
- Tesseract OCR installed
- OpenVINO-optimized model (Phi-3.5 INT4)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Sarathbabu1106/PrivateDocAI-Analyzer.git
cd PrivateDocAI-Analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR
**Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Install to `C:\Program Files\Tesseract-OCR\`

**macOS**:
```bash
brew install tesseract
```

**Linux**:
```bash
sudo apt install tesseract-ocr
```

### 4. Download the AI Model
Download the Phi-3.5 INT4 OpenVINO model and place it in:
```
PrivateDocAI-Analyzer/
  └── models/
      └── phi35_ov_int4/
```

## Usage

Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

1. **Upload** a PDF, paste text, or upload an image
2. **Select** analysis depth (Quick or Deep Scan)
3. **Run** AI analysis - watch real-time streaming results
4. **Ask** follow-up questions in the interactive Q&A
5. **Download** your summary as a PDF report

## Architecture

- **Frontend**: Streamlit web interface
- **AI Engine**: OpenVINO optimized Phi-3.5 (INT4 quantization)
- **OCR**: Tesseract for image text extraction
- **PDF Processing**: PyPDF for document parsing

## Privacy & Security

✅ **Fully Offline** - No API calls, no data leaves your machine  
✅ **Local Processing** - All AI inference runs on your CPU  
✅ **No Tracking** - Zero telemetry or analytics  

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8GB | 16GB |
| CPU | 4 cores | 8 cores |
| Storage | 5GB | 10GB |
| OS | Windows 10/11, macOS 10.15+, Ubuntu 20.04+ | - |

## Limitations

- CPU-only inference (slower than GPU)
- 3000 character context limit for Q&A
- Best for documents under 100 pages

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenVINO](https://github.com/openvinotoolkit/openvino.genai) for model optimization
- [Streamlit](https://streamlit.io/) for the web framework
- Microsoft Phi-3.5 model

## Screenshots
Main interface
<img width="1892" height="903" alt="Screenshot 2026-02-16 185038" src="https://github.com/user-attachments/assets/17dc9ded-8e8e-482b-bbd6-1995f9789e87" />

Analysis Results
<img width="1875" height="904" alt="Screenshot 2026-02-16 185419" src="https://github.com/user-attachments/assets/c4b55515-97fe-4810-a8b3-be492b6ec982" />

Follow-up Question
<img width="1854" height="879" alt="Screenshot 2026-02-16 185736" src="https://github.com/user-attachments/assets/1a6aa50b-76dd-4efc-8a86-b13e555cf653" />

Assistant Answer
<img width="1875" height="886" alt="Screenshot 2026-02-16 185920" src="https://github.com/user-attachments/assets/dfd176bb-250e-4e49-b3a6-fc373b74ab54" />




