
import os
from converter import CloudConvertService
from dotenv import load_dotenv

load_dotenv()

def test_conversion():
    service = CloudConvertService()
    if not service.client:
        print("CloudConvert client not initialized. Skipping test.")
        return

    # Create a dummy docx file if it doesn't exist
    import docx
    doc = docx.Document()
    doc.add_paragraph("Test conversion to PDF")
    test_docx = "test_conversion.docx"
    doc.save(test_docx)
    
    output_dir = "converted_pdfs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    try:
        pdf_path = service.convert_to_pdf(test_docx, output_dir)
        print(f"Conversion successful: {pdf_path}")
        if os.path.exists(pdf_path):
            print("PDF file exists on disk.")
        else:
            print("PDF file NOT found on disk.")
    except Exception as e:
        print(f"Conversion failed: {e}")
    finally:
        if os.path.exists(test_docx):
            os.remove(test_docx)

if __name__ == "__main__":
    test_conversion()
