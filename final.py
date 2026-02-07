import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
import zipfile

st.set_page_config(page_title="PDF Cover & Watermark Tool", layout="centered")
st.title("PDF Cover & Watermark Tool")

# Upload multiple PDFs
main_pdfs = st.file_uploader("Upload Main PDFs", type=["pdf"], accept_multiple_files=True)

# Optional output prefix
output_prefix = st.text_input(
    "Output filename prefix (optional)",
    placeholder="Example: college_simplified"
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

    c.drawImage(ImageReader(logo_img), x, y, width=logo_width, height=logo_height, mask="auto")
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


if main_pdfs:
    if not all(map(os.path.exists, [FRONT_COVER, BACK_COVER, LOGO_PATH])):
        st.error("❌ Required files missing in assets folder.")
        st.stop()

    if st.button("🚀 Process All PDFs"):
        logo_image = Image.open(LOGO_PATH)

        zip_buffer = io.BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_files = len(main_pdfs)

        for index, main_pdf in enumerate(main_pdfs):
            status_text.text(f"Processing: {main_pdf.name}")

            writer = PdfWriter()

            # Front cover
            for page in PdfReader(FRONT_COVER).pages:
                writer.add_page(page)

            # Main PDF (with watermark)
            for page in PdfReader(main_pdf).pages:
                writer.add_page(add_watermark(page, logo_image))

            # Back cover
            for page in PdfReader(BACK_COVER).pages:
                writer.add_page(page)

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            final_filename = (
                f"{output_prefix}_{main_pdf.name}" if output_prefix.strip() else main_pdf.name
            )

            zip_file.writestr(final_filename, output.read())

            progress_bar.progress((index + 1) / total_files)

        zip_file.close()
        zip_buffer.seek(0)

        status_text.text("✅ All files processed successfully!")
        st.success("All PDFs processed and zipped.")

        st.download_button(
            label="📦 Download All PDFs (ZIP)",
            data=zip_buffer,
            file_name="processed_pdfs.zip",
            mime="application/zip"
        )

else:
    st.info("Upload one or more PDFs to proceed.")
