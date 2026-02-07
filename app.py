import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os

st.set_page_config(page_title="PDF Cover & Watermark Tool", layout="centered")
st.title("PDF Cover & Watermark Tool")

# Upload main PDF
main_pdf = st.file_uploader("Upload Main PDF", type=["pdf"])

# Optional output name
output_name = st.text_input(
    "Output file name (optional, without .pdf)",
    placeholder="Output PDF name (e.g., 'document')"
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
    aspect_ratio = logo_img.height / logo_img.width
    logo_height = logo_width * aspect_ratio

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


if main_pdf:
    if not all(map(os.path.exists, [FRONT_COVER, BACK_COVER, LOGO_PATH])):
        st.error("Required files missing in assets folder.")
        st.stop()

    writer = PdfWriter()
    logo_image = Image.open(LOGO_PATH)

    # Front cover (no watermark)
    for page in PdfReader(FRONT_COVER).pages:
        writer.add_page(page)

    # Main PDF (with watermark)
    for page in PdfReader(main_pdf).pages:
        writer.add_page(add_watermark(page, logo_image))

    # Back cover (no watermark)
    for page in PdfReader(BACK_COVER).pages:
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    st.success("PDF processed successfully")

    # Filename decision logic
    final_filename = (
        f"{output_name}.pdf" if output_name.strip() else main_pdf.name
    )

    st.download_button(
        label="Download PDF",
        data=output,
        file_name=final_filename,
        mime="application/pdf"
    )
else:
    st.info("Upload a PDF to proceed.")
