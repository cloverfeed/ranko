from PyPDF2 import PdfFileReader


def extract_title(filename):
    try:
        with open(filename, 'rb') as f:
            p = PdfFileReader(f)
            info = p.getDocumentInfo()
            title = info['/Title']
    except IOError:
        title = None
    return title
