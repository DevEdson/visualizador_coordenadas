import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import random

class PDFViewer:
    def __init__(self, root):
        self.rainbow_colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#0000FF", "#4B0082", "#EE82EE"]

        self.root = root
        self.root.title("Visualizador de PDF")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.open_button = tk.Button(root, text="Abrir PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT)

        self.prev_button = tk.Button(root, text="Anterior", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(root, text="Próxima", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(root, text="Exportar Coordenadas", command=self.export_coords)
        self.export_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Limpar Marcações", command=self.clear_marks)
        self.clear_button.pack(side=tk.LEFT)

        self.coord_label = tk.Label(root, text="Coordenadas: (largura, altura)")
        self.coord_label.pack(side=tk.RIGHT)

        self.info_label = tk.Label(root, text="Informações da Página: ")
        self.info_label.pack(side=tk.RIGHT)

        self.y_entry = tk.Entry(root, width=6)
        self.y_entry.pack(side=tk.RIGHT)
        self.y_label = tk.Label(root, text="Y:")
        self.y_label.pack(side=tk.RIGHT)

        self.x_entry = tk.Entry(root, width=6)
        self.x_entry.pack(side=tk.RIGHT)
        self.x_label = tk.Label(root, text="X:")
        self.x_label.pack(side=tk.RIGHT)

   

        self.sig_width_entry = tk.Entry(root, width=5)
        self.sig_width_entry.insert(0, "50")
        self.sig_width_entry.pack(side=tk.RIGHT)
        self.sig_width_label = tk.Label(root, text="Largura (mm):")
        self.sig_width_label.pack(side=tk.RIGHT)

        self.sig_height_entry = tk.Entry(root, width=5)
        self.sig_height_entry.insert(0, "20")
        self.sig_height_entry.pack(side=tk.RIGHT)
        self.sig_height_label = tk.Label(root, text="Altura (mm):")
        self.sig_height_label.pack(side=tk.RIGHT)

        self.go_button = tk.Button(root, text="Ir para Coordenadas", command=self.go_to_coordinates)
        self.go_button.pack(side=tk.RIGHT)

        self.doc = None
        self.page_num = 0
        self.marked_coords = []
        self.drawn_items = []  # Armazena IDs das marcações

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.show_page()

    def show_page(self):
        if self.doc:
            self.clear_marks()
            page = self.doc.load_page(self.page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)

            self.canvas.config(width=pix.width, height=pix.height)
            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
            self.canvas.image = img_tk

            self.canvas.bind("<Motion>", lambda event: self.show_coordinates(event, page))
            self.canvas.bind("<Button-1>", self.mark_position)

            width, height = page.rect.width, page.rect.height
            orientation = "Retrato" if height > width else "Paisagem"
            width_mm = width * 25.4 / 72
            height_mm = height * 25.4 / 72
            paper_size = f"{width_mm:.2f} x {height_mm:.2f} mm"
            self.info_label.config(text=f"Informações da Página: {orientation}, Tamanho: {paper_size}")

    def show_coordinates(self, event, page):
        x, y = event.x, event.y
        y_pdf = self.canvas.winfo_height() - y
        x_mm = x * 25.4 / 72
        y_mm = y_pdf * 25.4 / 72
        self.coord_label.config(text=f"Coordenadas: (largura x: {x_mm:.2f} mm, altura y: {y_mm:.2f} mm)")

    def prev_page(self):
        if self.doc and self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def next_page(self):
        if self.doc and self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def mark_position(self, event):
        x, y = event.x, event.y
        y_pdf = self.canvas.winfo_height() - y
        x_mm = x * 25.4 / 72
        y_mm = y_pdf * 25.4 / 72
        self.marked_coords.append((x_mm, y_mm))
        circle_id = self.canvas.create_oval(x-5, y-5, x+5, y+5, outline="blue", width=2)
        self.drawn_items.append(circle_id)

    def go_to_coordinates(self):
        try:
            x_mm = float(self.x_entry.get())
            y_mm = float(self.y_entry.get())
            sig_width_mm = float(self.sig_width_entry.get())
            sig_height_mm = float(self.sig_height_entry.get())

            x_pt = x_mm * 72 / 25.4
            y_pt = y_mm * 72 / 25.4
            width_pt = sig_width_mm * 72 / 25.4
            height_pt = sig_height_mm * 72 / 25.4

            y_tk = self.canvas.winfo_height() - y_pt

            x1 = x_pt
            y1 = y_tk - height_pt
            x2 = x_pt + width_pt
            y2 = y_tk

            color = random.choice(self.rainbow_colors)
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

            self.drawn_items.append(rect_id)
        except ValueError:
            print("Por favor, insira valores numéricos válidos.")

    def export_coords(self):
        if not self.marked_coords:
            print("Nenhuma coordenada marcada.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["X (mm)", "Y (mm)"])
                writer.writerows(self.marked_coords)
            print("Coordenadas exportadas para", file_path)

    def clear_marks(self):
        for item_id in self.drawn_items:
            self.canvas.delete(item_id)
        self.drawn_items.clear()
        self.marked_coords.clear()

root = tk.Tk()
viewer = PDFViewer(root)
root.mainloop()
