#!/usr/bin/env python3
import PyPDF2

# Extract text from PDFs showing UNK to find the actual codes
pdf_files = [
    'WSDOT Airfields/BanderaState.pdf',
    'WSDOT Airfields/DorothyScott.pdf',
    'WSDOT Airfields/LakeChelan.pdf'
]

for pdf_path in pdf_files:
    print(f"\n{'=' * 80}")
    print(f"Extracted text from {pdf_path}:")
    print('=' * 80)
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            print(text[:500])  # First 500 chars to see the code
    except Exception as e:
        print(f"Error: {e}")
