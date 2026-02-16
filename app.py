import streamlit as st
import queue, threading, time
from engine import PrivateAIEngine
from pypdf import PdfReader
from PIL import Image
import pytesseract
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io
from datetime import datetime

# --- REQUIRED: TESSERACT CONFIGURATION ---
# This path matches the 'All Users' installation from the UB Mannheim installer
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="Privacy AI Pro", page_icon="🛡️", layout="wide")

@st.cache_resource
def init_engine():
    return PrivateAIEngine()

def create_pdf_report(summary_text, doc_info=""):
    """Generate PDF report from summary without changing app flow"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Privacy AI Pro - Analysis Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)
    
    # Metadata
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if doc_info:
        pdf.cell(0, 10, doc_info, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    # Summary content
    pdf.set_font("Helvetica", "", 11)
    # Handle unicode characters by replacing problematic ones
    clean_text = summary_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, clean_text)
    
    # Return PDF as bytes (fixed for modern fpdf2)
    return bytes(pdf.output())

def main():
    st.title("🛡️ Privacy AI: Intelligent Multi-Modal Assistant")
    engine = init_engine()

    # --- SESSION STATE MANAGEMENT ---
    if "final_summary" not in st.session_state:
        st.session_state.final_summary = ""
    if "full_document_text" not in st.session_state:
        st.session_state.full_document_text = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    with st.sidebar:
        st.header("Input Configuration")
        # Disable inputs while AI is working to protect 8GB RAM
        input_mode = st.radio("Choose Input Type:", 
                              ["PDF Document", "Paste Text/Email", "Image/Screenshot"],
                              disabled=st.session_state.is_processing)
        
        st.divider()
        if st.button("🗑️ Clear All Data", disabled=st.session_state.is_processing):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- INPUT HANDLERS ---
    raw_text_to_analyze = ""
    pdf_obj = None

    if input_mode == "PDF Document":
        pdf_obj = st.file_uploader("Upload PDF", type="pdf")
        if pdf_obj:
            reader = PdfReader(pdf_obj)
            st.info(f"📄 PDF detected with {len(reader.pages)} pages.")

    elif input_mode == "Paste Text/Email":
        raw_text_to_analyze = st.text_area("Paste text here:", height=300)

    elif input_mode == "Image/Screenshot":
        image_file = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])
        if image_file:
            img = Image.open(image_file)
            st.image(img, caption="Source Image", width=500)
            if st.button("Extract Text from Image", disabled=st.session_state.is_processing):
                with st.spinner("🔍 Scanning for text..."):
                    try:
                        extracted = pytesseract.image_to_string(img)
                        if extracted.strip():
                            st.session_state.full_document_text = extracted
                            st.success("Text extracted successfully!")
                        else:
                            st.warning("No text found in image.")
                    except Exception as e:
                        st.error(f"OCR Error: Ensure Tesseract is installed at C:\\Program Files\\Tesseract-OCR")

    # --- ANALYSIS SETTINGS & EXECUTION ---
    can_analyze = (input_mode == "PDF Document" and pdf_obj) or \
                  (input_mode == "Paste Text/Email" and raw_text_to_analyze) or \
                  (input_mode == "Image/Screenshot" and st.session_state.full_document_text)

    if can_analyze:
        st.divider()
        st.subheader("Analysis Settings")
        
        analysis_depth = st.radio(
            "Select Analysis Depth:",
            ["Quick Summary (3 pages)", "Deep Scan (full doc)"],
            disabled=st.session_state.is_processing
        )

        if st.button("🚀 Run AI Analysis", type="primary", disabled=st.session_state.is_processing):
            st.session_state.is_processing = True
            st.session_state.final_summary = ""
            st.session_state.chat_history = []
            
            # Temporary container for loading UI (Alerts/Progress Bar)
            loading_container = st.container()
            with loading_container:
                status_area = st.empty()
                progress_bar = st.progress(0)
            
            output_area = st.empty()
            token_queue = queue.Queue()

            def analysis_worker(depth, input_val, mode_type):
                collected_text = ""
                def q_cb(t):
                    token_queue.put(t)
                    return False

                try:
                    if mode_type == "PDF Document":
                        reader = PdfReader(input_val)
                        total = len(reader.pages)
                        if "Deep" in depth:
                            all_summaries = []
                            for i in range(0, total, 3):
                                end_p = min(i+3, total)
                                token_queue.put(f"__STATUS__Analyzing PDF pages {i+1} to {end_p}...")
                                chunk = engine.extract_text_chunk(input_val, i)
                                collected_text += chunk + " "
                                all_summaries.append(engine.get_summary(chunk, None))
                                token_queue.put(f"__PROGRESS__{min((i+3)/total, 1.0)}")
                            
                            token_queue.put("__CLEAR_UI__") # Hides the loading alerts
                            engine.get_summary("\n".join(all_summaries), q_cb, 
                                               custom_prompt="Synthesize these into a master report:")
                        else:
                            token_queue.put("__STATUS__Performing Quick Scan...")
                            chunk = engine.extract_text_chunk(input_val, 0)
                            collected_text = chunk
                            token_queue.put("__CLEAR_UI__")
                            engine.get_summary(chunk, q_cb)
                    
                    elif mode_type == "Paste Text/Email":
                        token_queue.put("__STATUS__Processing pasted text...")
                        collected_text = input_val
                        token_queue.put("__CLEAR_UI__")
                        engine.get_summary(input_val, q_cb)
                    
                    elif mode_type == "Image/Screenshot":
                        token_queue.put("__STATUS__Analyzing image context...")
                        collected_text = st.session_state.full_document_text
                        token_queue.put("__CLEAR_UI__")
                        engine.get_summary(collected_text, q_cb)

                    st.session_state.full_document_text = collected_text
                except Exception as e:
                    token_queue.put(f"__ERROR__{str(e)}")
                finally:
                    token_queue.put("__COMPLETE__")

            ctx = get_script_run_ctx()
            worker_args = (analysis_depth, pdf_obj if input_mode == "PDF Document" else raw_text_to_analyze, input_mode)
            thread = threading.Thread(target=analysis_worker, args=worker_args)
            add_script_run_ctx(thread)
            thread.start()

            res = ""
            while thread.is_alive() or not token_queue.empty():
                try:
                    msg = token_queue.get(timeout=0.1)
                    if isinstance(msg, str):
                        if msg.startswith("__STATUS__"):
                            status_area.info(msg.replace("__STATUS__", ""))
                        elif msg.startswith("__PROGRESS__"):
                            progress_bar.progress(float(msg.replace("__PROGRESS__", "")))
                        elif msg == "__CLEAR_UI__":
                            loading_container.empty() # Removes bars so summary can stream clearly
                        elif msg == "__COMPLETE__":
                            st.session_state.final_summary = res
                            st.session_state.is_processing = False
                            break
                        elif msg.startswith("__ERROR__"):
                            st.error(msg.replace("__ERROR__", ""))
                            st.session_state.is_processing = False
                        else:
                            res += msg
                            output_area.markdown(res + "▌")
                except queue.Empty: continue
            output_area.markdown(res)
            st.rerun()

    # --- RESULTS & INTERACTIVE Q&A ---
    if st.session_state.final_summary:
        st.divider()
        st.subheader("📋 Document Summary")
        st.markdown(st.session_state.final_summary)
        
        # PDF Download Button (NEW - doesn't affect existing flow)
        col1, col2 = st.columns([6, 1])
        with col2:
            pdf_bytes = create_pdf_report(st.session_state.final_summary)
            st.download_button(
                label="📥 PDF",
                data=pdf_bytes,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                help="Download summary as PDF"
            )

        st.subheader("❓ Interactive Q&A")
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

        # Prevent dual-entry by disabling input during thinking
        input_hint = "Ask a follow-up..." if not st.session_state.is_processing else "Processing response..."
        user_q = st.chat_input(input_hint, disabled=st.session_state.is_processing)
        
        if user_q:
            st.session_state.is_processing = True
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            st.rerun()

    # Worker for the Chat Q&A
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner(" 🔍 Searching context..."):
                # Safety context limit for 8GB RAM
                context = st.session_state.full_document_text[:3000]
                user_q = st.session_state.chat_history[-1]["content"]
                ans = engine.get_summary("", None, custom_prompt=f"Context: {context}\n\nQuestion: {user_q}")
                st.markdown(ans)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.session_state.is_processing = False
                st.rerun()

if __name__ == "__main__":
    main()