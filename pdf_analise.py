import fitz  # PyMuPDF

def find_text_coordinates(pdf_path, search_text):
    # Abrir o documento PDF
    doc = fitz.open(pdf_path)
    
    # Iterar sobre as páginas do PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Procurar o texto específico na página
        text_instances = page.search_for(search_text)
        
        # Verificar se o texto foi encontrado
        if text_instances:
            print(f'Texto "{search_text}" encontrado na página {page_num + 1}:')
            for inst in text_instances:
                x0, y0, x1, y1 = inst  # Coordenadas da caixa delimitadora do texto
                print(f"Coordenadas: ({x0}, {y0}) -> ({x1}, {y1})")
        else:
            print(f'Texto "{search_text}" não encontrado na página {page_num + 1}.')

# Usando a função para procurar o texto "Assinatura Digital"
pdf_file = "C:\\Users\\edson.barbosa\\Desktop\\chamados\\signer\\10862132\\applicationErrorConvertido.pdf"  # Substitua pelo caminho do seu PDF
find_text_coordinates(pdf_file, "Assinatura Digital")
