import PyPDF2
import io

def extract_text_from_pdf(file_content):
    """
    Takes raw file bytes and returns the text inside the PDF
    """
    try:
        pdf_file=io.BytesIO(file_content)
        reader=PyPDF2.PdfReader(pdf_file)
        text=""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text+=content +"\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF :{e}")
        return ""
