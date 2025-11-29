from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Research Integrity Project - Documentation', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, label, 0, 1, 'L', 1)
        self.ln(4)

    def sanitize_text(self, text):
        replacements = {
            '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-',
            '\u2026': '...', '\u2022': '-',
            '\u00a0': ' '
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        
        # Final fallback: encode to latin-1, replace errors with ?
        return text.encode('latin-1', 'replace').decode('latin-1')

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        # Basic markdown parsing
        for line in body.split('\n'):
            line = self.sanitize_text(line.strip())
            if not line:
                self.ln(2)
                continue
            
            if line.startswith('# '):
                self.ln(5)
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, line.replace('# ', ''), 0, 1)
                self.set_font('Arial', '', 11)
            elif line.startswith('## '):
                self.ln(4)
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, line.replace('## ', ''), 0, 1)
                self.set_font('Arial', '', 11)
            elif line.startswith('### '):
                self.ln(3)
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, line.replace('### ', ''), 0, 1)
                self.set_font('Arial', '', 11)
            elif line.startswith('- '):
                self.cell(10)
                self.cell(0, 5, chr(149) + ' ' + line.replace('- ', ''), 0, 1)
            elif line.startswith('```'):
                continue # Skip code block markers for now, or handle differently
            else:
                self.multi_cell(0, 5, line)
        self.ln()

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    
    files = ["README.md", "DEVELOPER_GUIDE.md"]
    
    for filename in files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove mermaid diagrams for PDF text compatibility
                content = content.replace("```mermaid", "[Mermaid Diagram Omitted in PDF]")
                
                pdf.chapter_title(f"Section: {filename}")
                pdf.chapter_body(content)
                pdf.add_page()

    output_file = "Research_Integrity_Project_Guide.pdf"
    pdf.output(output_file)
    print(f"PDF created: {output_file}")

if __name__ == "__main__":
    create_pdf()
