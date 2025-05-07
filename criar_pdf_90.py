from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.translate(100, 100)  # Mova a origem para facilitar a rotação
    c.rotate(90)  # Rotacione o canvas em 90 graus
    c.drawString(0, 0, "texte interno")  # Adicione o texto
    c.save()

create_pdf("documento_rotacionado.pdf")