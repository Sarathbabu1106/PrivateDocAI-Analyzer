import openvino_genai as ov_genai
from pypdf import PdfReader
import os
import re

class PrivateAIEngine:
    def __init__(self, model_path="models/phi35_ov_int4"):
        clean_path = os.path.abspath(model_path.strip("'\""))
        self.device = "CPU"  # Hardware stability for 8GB RAM
        self.pipe = ov_genai.LLMPipeline(clean_path, self.device)

    def extract_text_chunk(self, pdf_file, start_page, chunk_size=3):
        reader = PdfReader(pdf_file)
        text = ""
        end_page = min(start_page + chunk_size, len(reader.pages))
        
        for i in range(start_page, end_page):
            content = reader.pages[i].extract_text()
            if content:
                # Clean non-ASCII junk common in financial/technical PDFs
                content = re.sub(r'[^\x00-\x7F]+', ' ', content)
                text += content + " "
        return " ".join(text.split())[:3000]

    def get_summary(self, text, stream_callback, custom_prompt=None):
        if custom_prompt:
            prompt = f"<|user|>\n{custom_prompt}\n{text}<|end|>\n<|assistant|>\n"
        else:
            prompt = f"<|user|>\nSummarize this section concisely:\n{text}<|end|>\n<|assistant|>\n"
        
        def internal_callback(token):
            if stream_callback:
                return stream_callback(token)
            return False

        # max_new_tokens=400 allows for detailed key terms
        return self.pipe.generate(prompt, max_new_tokens=400, streamer=internal_callback)