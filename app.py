import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os

st.set_page_config(page_title="PDF Cover & Watermark Tool", layout="centered")
st.title("PDF Cover & Watermark Tool")

# Upload multiple PDFs
uploaded_pdfs = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

# Assets paths
ASSETS_DIR = "assets"
FRONT_COVER = os.path.join(ASSETS_DIR, "front_cover.pdf")
BACK_COVER = os.path.join(ASSETS_DIR, "back_cover.pdf")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")


def create_watermark(page_width, page_height, logo_img):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFillAlpha(0.1)

    logo_width = page_width * 0.3
    ratio = logo_img.height / logo_img.width
    logo_height = logo_width * ratio

    x = (page_width - logo_width) / 2
    y = (page_height - logo_height) / 2

    c.drawImage(
        ImageReader(logo_img),
        x, y,
        width=logo_width,
        height=logo_height,
        mask="auto"
    )

    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def add_watermark(page, logo_img):
    watermark = create_watermark(
        float(page.mediabox.width),
        float(page.mediabox.height),
        logo_img
    )
    page.merge_page(watermark)
    return page


if uploaded_pdfs:
    if not all(map(os.path.exists, [FRONT_COVER, BACK_COVER, LOGO_PATH])):
        st.error("Required files missing in assets folder.")
        st.stop()

    logo_image = Image.open(LOGO_PATH)

    st.divider()
    st.subheader("Processed Files")

    for idx, pdf_file in enumerate(uploaded_pdfs, start=1):
        with st.container(border=True):
            st.markdown(f"### 📄 {pdf_file.name}")

            writer = PdfWriter()

            # Front cover (no watermark)
            for page in PdfReader(FRONT_COVER).pages:
                writer.add_page(page)

            # Main PDF (with watermark)
            for page in PdfReader(pdf_file).pages:
                writer.add_page(add_watermark(page, logo_image))

            # Back cover (no watermark)
            for page in PdfReader(BACK_COVER).pages:
                writer.add_page(page)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            # Filename: original + _CS
            base_name, ext = os.path.splitext(pdf_file.name)
            final_filename = f"{base_name}_CS{ext}"

            st.download_button(
                label="⬇️ Download PDF",
                data=output,
                file_name=final_filename,
                mime="application/pdf",
                use_container_width=True
            )
else:
    st.info("Upload one or more PDFs to proceed.")
