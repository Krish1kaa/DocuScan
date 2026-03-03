"""
DocuScan OCR — EasyOCR Edition
Supports: English + Tamil

Install:
    pip install -r requirements.txt

Run:
    python ocr_app.py
"""

import gradio as gr
from PIL import Image
import os, re, time, json
import numpy as np

# ── EasyOCR loader (once per session) ────────────────────────────────────────
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        print("Loading EasyOCR (English + Tamil)…")
        _reader = easyocr.Reader(["en", "ta"], gpu=False, verbose=False, recog_network="standard")
        print("EasyOCR ready.")
    return _reader

# ── OCR ───────────────────────────────────────────────────────────────────────
def run_ocr(pil_img: Image.Image) -> str:
    reader = get_reader()
    arr = np.array(pil_img.convert("RGB"))
    results = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(results)

# ── PDF → images ──────────────────────────────────────────────────────────────
def pdf_to_images(path: str):
    from pdf2image import convert_from_path
    return convert_from_path(path, dpi=200)

# ── Information extraction ────────────────────────────────────────────────────
def extract_info(text: str) -> str:
    info = {}

    dates = re.findall(
        r"(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"
        r"|(?:\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})"
        r"|(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})",
        text, re.IGNORECASE
    )
    if dates:
        info["📅 Dates"] = ", ".join(dict.fromkeys(dates))

    emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    if emails:
        info["📧 Emails"] = ", ".join(dict.fromkeys(emails))

    phones = [p.strip() for p in re.findall(r"(?:\+?\d[\d\s\-\(\)]{7,}\d)", text)
              if len(re.sub(r"\D", "", p)) >= 7]
    if phones:
        info["📞 Phone Numbers"] = ", ".join(dict.fromkeys(phones))

    urls = re.findall(r"https?://[^\s]+|www\.[^\s]+", text)
    if urls:
        info["🔗 URLs"] = ", ".join(dict.fromkeys(urls))

    amounts = re.findall(r"(?:USD|EUR|GBP|INR|₹|\$|€|£)\s?[\d,]+(?:\.\d{1,2})?", text)
    if amounts:
        info["💰 Amounts"] = ", ".join(dict.fromkeys(amounts))

    totals = re.findall(r"(?:total|grand total|amount due|balance)[^\n]*", text, re.IGNORECASE)
    if totals:
        info["🧾 Totals"] = " | ".join(t.strip() for t in totals[:3])

    ref_m = re.search(
        r"(?:invoice|ref|reference|order|receipt)\s*(?:no\.?|#|number)?\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        text, re.IGNORECASE
    )
    if ref_m:
        info["🔖 Reference #"] = ref_m.group(1).strip()

    name_m = re.search(
        r"(?:name|to|from|issued to|bill to|dear)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        text, re.IGNORECASE
    )
    if name_m:
        info["👤 Name"] = name_m.group(1).strip()

    info["📊 Word count"]      = str(len(text.split()))
    info["📊 Character count"] = str(len(text))

    # Return as formatted text instead of JSON to avoid gradio bug
    return "\n".join(f"{k}: {v}" for k, v in info.items())

# ── Main ──────────────────────────────────────────────────────────────────────
def process_document(file, show_raw: bool):
    if file is None:
        return "⚠️ Please upload a file first.", "", ""

    ext   = os.path.splitext(file.name)[-1].lower()
    log   = []
    pages = []

    try:
        t0 = time.time()

        if ext == ".pdf":
            log.append("📄 Converting PDF to images…")
            pages = pdf_to_images(file.name)
            log.append(f"   ✅ {len(pages)} page(s) found.")
        elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"):
            pages = [Image.open(file.name)]
            log.append("🖼️ Image loaded.")
        else:
            return f"❌ Unsupported file type: {ext}", "", ""

        all_text = []
        for i, page in enumerate(pages, 1):
            log.append(f"🔍 Processing page {i}/{len(pages)}…")
            text = run_ocr(page)
            all_text.append(f"─── Page {i} ───\n{text}")

        full_text = "\n\n".join(all_text)
        elapsed   = time.time() - t0
        log.append(f"⏱️ Completed in {elapsed:.1f}s")

        extracted = extract_info(full_text)
        log.append("✅ Extraction complete.")

        raw = full_text if show_raw else "(enable 'Show raw text' to display)"
        return "\n".join(log), extracted, raw

    except Exception as e:
        import traceback
        return f"❌ Error:\n{traceback.format_exc()}", "", ""

# ── UI ────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
body, .gradio-container {
    font-family: 'Syne', sans-serif !important;
    background: #0a0a0f !important;
    color: #e8e6ff !important;
}
.gradio-container { max-width: 960px !important; }
#title-block {
    background: linear-gradient(135deg, #1a0a2e 0%, #0d1117 60%, #0a1628 100%);
    border: 1px solid #2a1f5e;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.card {
    background: #111122 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
}
button.primary {
    background: linear-gradient(90deg, #6c47ff, #a855f7) !important;
    border: none !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
button.primary:hover { background: linear-gradient(90deg, #7c5cff, #be6af7) !important; }
.label-wrap label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #8880cc !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
textarea, input[type=text] {
    background: #0d0d1a !important;
    border-color: #2a2a50 !important;
    color: #e8e6ff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}
"""

with gr.Blocks(css=CSS, title="DocuScan OCR") as demo:

    with gr.Column(elem_id="title-block"):
        gr.Markdown("# 🔬 DocuScan OCR")

    with gr.Row():
        with gr.Column(scale=1, elem_classes="card"):
            gr.Markdown("### 📂 Upload Document")
            file_input = gr.File(
                label="Upload (PDF, PNG, JPG, TIFF…)",
                file_types=[".pdf",".png",".jpg",".jpeg",".bmp",".tiff",".webp"],
            )
            show_raw = gr.Checkbox(label="Show raw OCR text", value=True)
            run_btn  = gr.Button("⚡ Extract Now", variant="primary", size="lg")

        with gr.Column(scale=2):
            gr.Markdown("### 📋 Processing Log")
            status_out = gr.Textbox(label="Status", lines=6, interactive=False,
                                    placeholder="Output will appear here…")
            gr.Markdown("### 🗂️ Extracted Information")
            info_out = gr.Textbox(label="Structured Fields", lines=10, interactive=False)

    gr.Markdown("### 📝 Raw OCR Text")
    raw_out = gr.Textbox(label="Full extracted text", lines=14, interactive=False)

    run_btn.click(
        fn=process_document,
        inputs=[file_input, show_raw],
        outputs=[status_out, info_out, raw_out],
    )

if __name__ == "__main__":
    demo.launch(share=True)