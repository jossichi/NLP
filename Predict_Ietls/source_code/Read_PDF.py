import PyPDF2
import pyttsx3

filepath = r'pdf_document\Web Application Security Standards and Practices.pdf'

# Initialize the text-to-speech engine
speaker = pyttsx3.init()

# Open the PDF file using PdfReader instead of PdfFileReader
pdfReader = PyPDF2.PdfReader(open(filepath, 'rb'))

# Read and speak the text from each page
for page_num in range(len(pdfReader.pages)):
    text = pdfReader.pages[page_num].extract_text()
    speaker.say(text)

# Wait for the speech to finish
speaker.runAndWait()

# Stop the text-to-speech engine
speaker.stop()
