import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class PDFChunker:
    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_pdf(self, doc, file_doc):
        all_chunks = []

        for page_num, page in enumerate(doc, start=1):  # 1-based page numbers
            text = page.get_text("text")
            if not text.strip():
                continue

            # Split this page into chunks
            splits = self.splitter.split_text(text)

            for i, chunk in enumerate(splits):
                all_chunks.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "file_id": str(file_doc["_id"]),
                            "file_name": file_doc["file_name"],
                            "course_id": file_doc["course_id"],
                            "page": page_num,
                            "chunk_index": i
                        }
                    )
                )
        print("All chunks:", all_chunks)
        return all_chunks
