import PyPDF2

pdf_path = "Washington Airfield PDFs/SequimValley.pdf"
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

print("SequimValley.pdf content:")
print("="*60)
print(text)
print("="*60)
