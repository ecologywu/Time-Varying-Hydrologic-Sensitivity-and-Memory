"""Extract first-page text from each reference PDF for citation metadata and content."""
import os
import fitz

REF_DIR = r"C:\Users\dell\Desktop\水文响应模式的漂移References"
OUT = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data\refs_extracted.txt"

files = sorted(f for f in os.listdir(REF_DIR) if f.lower().endswith(".pdf"))
chunks = []
for f in files:
    try:
        doc = fitz.open(os.path.join(REF_DIR, f))
        text = ""
        for i in range(min(2, len(doc))):  # first 2 pages
            text += doc[i].get_text()
        doc.close()
        text = " ".join(text.split())
        chunks.append("=" * 80 + "\nFILE: " + f + "\n" + "=" * 80 + "\n" + text[:4200] + "\n")
    except Exception as e:
        chunks.append("=" * 80 + "\nFILE: " + f + "\nERROR: " + str(e) + "\n")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(chunks))
print("Extracted", len(files), "PDFs ->", OUT)
