from pypdf import PdfReader

reader = PdfReader("../college_student_queries.pdf")
print("college_student_queries.pdf page count:", len(reader.pages))
for p_idx, page in enumerate(reader.pages):
    text = page.extract_text()
    if not text:
        continue
    print(f"\n--- Page {p_idx+1} ---")
    lines = text.split("\n")
    for l_idx, line in enumerate(lines):
        if any(word in line.lower() for word in ["mark", "assess", "weight"]):
            print(f"Line {l_idx+1}: {line}")
