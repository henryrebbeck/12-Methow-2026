import PyPDF2

pdf_path = "Washington Airfield PDFs/Tietonstate.pdf"
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

print("Tietonstate.pdf content:")
print("="*60)
print(text)
print("="*60)
