
import fitz  # PyMuPDF 
import tkinter as tk
from tkinter import filedialog, messagebox
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

        self.import_button = tk.Button(root, text="Importar CSV", command=self.import_coords)
        self.import_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(root, text="Exportar Coordenadas", command=self.export_coords)
        self.export_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Limpar Marcações", command=self.clear_marks)
        self.clear_button.pack(side=tk.LEFT)

        self.coord_label = tk.Label(root, text="Coordenadas: (largura, altura)")
        self.coord_label.pack(side=tk.RIGHT)

        self.info_label = tk.Label(root, text="Informações da Página: ")
        self.info_label.pack(side=tk.RIGHT)

        self.y_entry = tk.Entry(root, width=7)
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

        self.sig_height_entry = tk.Entry(root, width=4)
        self.sig_height_entry.insert(0, "20")
        self.sig_height_entry.pack(side=tk.RIGHT)
        self.sig_height_label = tk.Label(root, text="Altura (mm):")
        self.sig_height_label.pack(side=tk.RIGHT)

        self.go_button = tk.Button(root, text="Ir para Coordenadas", command=self.go_to_coordinates)
        self.go_button.pack(side=tk.RIGHT)

        for widget in [self.open_button, self.prev_button, self.next_button, self.import_button,
                       self.export_button, self.clear_button, self.sig_height_entry,
                       self.sig_width_entry, self.x_entry, self.y_entry, self.go_button]:
            widget.configure(takefocus=True)

        self.doc = None
        self.page_num = 0
        self.marked_coords = {}
        self.drawn_items = {}
        self.img_width = 0
        self.img_height = 0

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.show_page()

    def show_page(self):
        if self.doc:
            page = self.doc.load_page(self.page_num)
            pix = page.get_pixmap()
            self.img_width, self.img_height = pix.width, pix.height

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)

            self.canvas.config(width=pix.width, height=pix.height)
            self.canvas.delete("all")
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

            self.redraw_marks()

    def show_coordinates(self, event, page):
        x, y = event.x, event.y
        y_pdf = self.img_height - y
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
        y_pdf = self.img_height - y
        x_mm = x * 25.4 / 72
        y_mm = y_pdf * 25.4 / 72

        self.marked_coords.setdefault(self.page_num, []).append((x_mm, y_mm))
        self.redraw_marks()

    def redraw_marks(self):
        self.canvas.delete("all")
        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.canvas.image = img_tk

        self.drawn_items[self.page_num] = []

        try:
            sig_width_mm = float(self.sig_width_entry.get())
            sig_height_mm = float(self.sig_height_entry.get())
        except ValueError:
            sig_width_mm = 50
            sig_height_mm = 20

        width_pt = sig_width_mm * 72 / 25.4
        height_pt = sig_height_mm * 72 / 25.4

        for x_mm, y_mm in self.marked_coords.get(self.page_num, []):
            x_pt = x_mm * 72 / 25.4
            y_pt = y_mm * 72 / 25.4
            y_tk = self.img_height - y_pt

            x1 = x_pt
            y1 = y_tk - height_pt
            x2 = x_pt + width_pt
            y2 = y_tk

            color = random.choice(self.rainbow_colors)
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
            self.drawn_items[self.page_num].append(rect_id)

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

            y_tk = self.img_height - y_pt

            x1 = x_pt
            y1 = y_tk - height_pt
            x2 = x_pt + width_pt
            y2 = y_tk

            color = random.choice(self.rainbow_colors)
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

            self.drawn_items.setdefault(self.page_num, []).append(rect_id)
            self.marked_coords.setdefault(self.page_num, []).append((x_mm, y_mm))
        except ValueError:
            print("Por favor, insira valores numéricos válidos.")

    def export_coords(self):
        all_coords = []
        for coords in self.marked_coords.values():
            all_coords.extend(coords)
        if not all_coords:
            print("Nenhuma coordenada marcada.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["X (mm)", "Y (mm)"])
                writer.writerows(all_coords)
            print("Coordenadas exportadas para", file_path)

    def import_coords(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            with open(file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    try:
                        x_mm = float(row["SignaturePositionX"])
                        y_mm = float(row["SignaturePositionY"])
                        w_mm = float(row.get("SignatureWidth", self.sig_width_entry.get()))
                        h_mm = float(row.get("SignatureHeight", self.sig_height_entry.get()))

                        x_pt = x_mm * 72 / 25.4
                        y_pt = y_mm * 72 / 25.4
                        w_pt = w_mm * 72 / 25.4
                        h_pt = h_mm * 72 / 25.4

                        y_tk = self.img_height - y_pt

                        x1 = x_pt
                        y1 = y_tk - h_pt
                        x2 = x_pt + w_pt
                        y2 = y_tk

                        color = random.choice(self.rainbow_colors)
                        rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)

                        self.drawn_items.setdefault(self.page_num, []).append(rect_id)
                        self.marked_coords.setdefault(self.page_num, []).append((x_mm, y_mm))
                        count += 1
                    except Exception as e:
                        print(f"Erro ao processar linha {row}: {e}")
            messagebox.showinfo("Importado", f"{count} coordenadas com retângulos importadas com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar CSV: {e}")

    def clear_marks(self):
        for item_id in self.drawn_items.get(self.page_num, []):
            self.canvas.delete(item_id)
        self.drawn_items[self.page_num] = []
        self.marked_coords[self.page_num] = []

# Início da aplicação
root = tk.Tk()
viewer = PDFViewer(root)
root.mainloop()
