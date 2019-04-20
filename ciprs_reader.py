import sys
from ciprs.reader import PDFToTextReader


if __name__ == "__main__":
    reader = PDFToTextReader(sys.argv[1])
    reader.parse()
    print(reader.json())
