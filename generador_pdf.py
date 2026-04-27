from fpdf import FPDF
from datetime import datetime

class InformeScopeAI(FPDF):
    def header(self):
        # Capçalera professional
        self.set_font('Arial', 'B', 15)
        self.set_text_color(37, 99, 235) # Blau ScopeAI
        self.cell(0, 10, 'SCOPE AI ENTERPRISE - INFORME TÈCNIC', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128)
        self.cell(0, 10, f'Generat el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        # Peu de pàgina amb numeració
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Pàgina {self.page_no()} - Document generat per IA d\'Enginyeria', 0, 0, 'C')

def crear_pdf_professional(text_ia, usuari):
    pdf = InformeScopeAI()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Afegim les dades de l'usuari
    pdf.set_fill_color(240, 244, 248)
    pdf.cell(0, 10, f"Inspector: {usuari}", 0, 1, 'L', fill=True)
    pdf.ln(5)

    # Netegem el text de caràcters estranys per evitar errors al PDF
    clean_txt = text_ia.encode('latin-1', 'replace').decode('latin-1')
    
    # Cos de l'informe
    pdf.set_text_color(0)
    pdf.multi_cell(0, 7, txt=clean_txt)
    
    return pdf.output(dest='S').encode('latin-1')