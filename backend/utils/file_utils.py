from pathlib import Path

# Save to "documents" folder instead of "uploads"
DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_file(uploaded_file, filename):
    safe_path = DOCUMENTS_DIR / filename
    uploaded_file.save(safe_path)
    return safe_path
