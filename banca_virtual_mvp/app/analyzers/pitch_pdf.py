import fitz  # PyMuPDF

def extract_pdf_outline(pdf_bytes: bytes):
    """Extracts simple heuristics: number of pages and first lines per page."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = doc.page_count
    preview = []
    for i in range(min(pages, 10)):  # sample up to 10 pages
        page = doc.load_page(i)
        text = page.get_text("text").strip().splitlines()
        preview.append({
            "page": i+1,
            "first_line": text[0] if text else ""
        })
    return {"pages": pages, "preview": preview}

COMMON_SECTIONS = ["Problema", "Solução", "Produto", "Mercado", "Modelo de Negócio", "Go-to-Market", "Concorrência", "Tração", "Equipe", "Roadmap", "Use of Funds"]

def simple_section_score(text: str):
    """Count occurrences of common section keywords to rate structure presence (very rough)."""
    t = text.lower()
    hits = 0
    for s in COMMON_SECTIONS:
        if s.lower() in t:
            hits += 1
    return hits / max(1, len(COMMON_SECTIONS))
