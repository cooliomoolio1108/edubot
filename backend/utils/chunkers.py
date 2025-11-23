import os
import fitz
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.messages import AIMessage

from storage import bucket
from services.gcp_services import view_file
from rag.services.openai_service import llm_stream


class PDFChunker:
    """
    Extracts both text and image captions from a PDF for vector embedding.
    - Text is chunked using RecursiveCharacterTextSplitter.
    - Images are uploaded to GCP and captioned using llm_stream (GPT-4o vision).
    """

    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_pdf(self, doc, file_doc):
        all_chunks = []
        file_id = str(file_doc.get("_id", ""))
        file_path = file_doc.get("path", "")
        course_id = file_doc.get("course_id", "")
        file_name = file_doc.get("file_name", "untitled.pdf")

        for page_num, page in enumerate(doc, start=1):
            # ── 1️⃣ TEXT EXTRACTION ──────────────────────────────────────────────
            try:
                text = page.get_text("text")
                if text.strip():
                    splits = self.splitter.split_text(text)
                    for i, chunk in enumerate(splits):
                        all_chunks.append(
                            Document(
                                page_content=chunk,
                                metadata={
                                    "source": file_path,
                                    "file_id": file_id,
                                    "file_name": file_name,
                                    "course_id": course_id,
                                    "page": page_num,
                                    "chunk_index": i,
                                    "type": "text",
                                },
                            )
                        )
            except Exception as e:
                print(f"⚠️ Failed text extraction on page {page_num}: {e}")
                continue

            # ── 2️⃣ IMAGE EXTRACTION & CAPTIONING ───────────────────────────────
            images = page.get_images(full=True)
            if not images:
                continue

            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    # save temp PNG
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        pix.save(tmp.name)
                        temp_path = tmp.name

                    # upload to same GCP bucket
                    blob_name = f"pdf_images/{file_id}_p{page_num}_i{img_index}.png"
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(temp_path)

                    # generate signed URL via existing util
                    image_url = view_file(blob_name).get("url")

                    # caption the image using llm_stream (GPT-4o)
                    caption_prompt = (
                        "Describe this image concisely in one or two sentences "
                        "for use in study or retrieval."
                    )
                    caption = self.caption_image(image_url, caption_prompt)

                    all_chunks.append(
                        Document(
                            page_content=f"[Image Caption] {caption}",
                            metadata={
                                "source": file_path,
                                "file_id": file_id,
                                "file_name": file_name,
                                "course_id": course_id,
                                "page": page_num,
                                "chunk_index": img_index,
                                "type": "image",
                                "image_url": image_url,
                            },
                        )
                    )

                except Exception as e:
                    print(f"⚠️ Skipped image {img_index} on page {page_num}: {e}")
                    continue

        print(f"✅ Total {len(all_chunks)} chunks (text + image captions).")
        return all_chunks

    def caption_image(self, image_url: str, question: str) -> str:
        """
        Use Azure GPT-4o (via llm_stream) to caption an image from its GCP URL.
        Robust against different llm_stream return shapes.
        """
        try:
            messages = [
                SystemMessage(
                    content="You are a vision model that summarizes diagrams and figures concisely."
                ),
                HumanMessage(
                    content=[
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                ),
            ]
            response = llm_stream.invoke(messages)

            caption = ""

            if isinstance(response, AIMessage):
                # ✅ Standard LangChain response
                if isinstance(response.content, str):
                    caption = response.content.strip()
                elif isinstance(response.content, list):
                    caption = " ".join(
                        part.get("text", "")
                        for part in response.content
                        if isinstance(part, dict)
                    ).strip()

            elif isinstance(response, dict):
                caption = (
                    response.get("content")
                    or response.get("text")
                    or response.get("message", "")
                )

            elif hasattr(response, "content"):
                caption = getattr(response, "content", "").strip()

            if not caption:
                print(f"⚠️ llm_stream returned unexpected format: {type(response)}")
                caption = "Uncaptioned image"

            return caption

        except Exception as e:
            print(f"⚠️ Captioning error: {e}")
            return "Uncaptioned image"

def _extract_text_from_llm_response(resp) -> str:
        """Best-effort normalization for various llm_stream return shapes."""
        # 1) Already a string
        if isinstance(resp, str):
            return resp.strip()

        # 2) SDK-like object with .choices
        if hasattr(resp, "choices"):
            try:
                choice = resp.choices[0]
                # OpenAI-python style: choice.message.content
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    c = choice.message.content
                    if isinstance(c, list):
                        # multimodal content parts
                        parts = []
                        for p in c:
                            if isinstance(p, dict) and p.get("type") == "text":
                                parts.append(p.get("text", ""))
                        return " ".join(parts).strip()
                    return (c or "").strip()
                # Streaming delta style
                if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                    return (choice.delta.content or "").strip()
            except Exception:
                pass

        # 3) Dict shapes (most common for custom wrappers)
        if isinstance(resp, dict):
            # Plain content/text field
            if "content" in resp and isinstance(resp["content"], str):
                return resp["content"].strip()
            if "text" in resp and isinstance(resp["text"], str):
                return resp["text"].strip()

            # OpenAI REST JSON: {"choices":[{"message":{"content": ...}}]}
            choices = resp.get("choices")
            if isinstance(choices, list) and choices:
                ch = choices[0]
                if isinstance(ch, dict):
                    msg = ch.get("message")
                    if isinstance(msg, dict):
                        c = msg.get("content")
                        if isinstance(c, list):
                            parts = []
                            for p in c:
                                if isinstance(p, dict) and p.get("type") == "text":
                                    parts.append(p.get("text", ""))
                            return " ".join(parts).strip()
                        if isinstance(c, str):
                            return c.strip()
                    # Some wrappers stream deltas even when not streaming
                    delta = ch.get("delta")
                    if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                        return delta["content"].strip()

            # Anthropic-like / generic shapes
            outputs = resp.get("outputs")
            if isinstance(outputs, list) and outputs:
                out0 = outputs[0]
                if isinstance(out0, dict):
                    txt = out0.get("text") or out0.get("content")
                    if isinstance(txt, str):
                        return txt.strip()

        # 4) List of chunks or events
        if isinstance(resp, list):
            parts = []
            for item in resp:
                parts.append(_extract_text_from_llm_response(item))
            return " ".join(p for p in parts if p).strip()

        # Fallback
        return ""