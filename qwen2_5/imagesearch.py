import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageGalleryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Галерея изображений")
        self.root.geometry("800x600")
        
        toolbar = tk.Frame(root, bd=1, relief=tk.RAISED, bg="#f0f0f0")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        btn_search = tk.Button(toolbar, text="📁 Выбрать папку", command=self.load_folder)
        btn_search.pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_exit = tk.Button(toolbar, text="🚪 Выход", command=root.quit)
        btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.canvas = tk.Canvas(root)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_refs = []

    def get_image_files(self, folder):
        exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        return [f for f in os.listdir(folder) if f.lower().endswith(exts)]

    def sort_by_weight(self, folder_path, image_files):
        image_files.sort(
            key=lambda f: os.path.getsize(os.path.join(folder_path, f)), 
            reverse=True
        )
        return image_files

    def load_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()
        
        images = self.get_image_files(folder_path)
        sorted_images = self.sort_by_weight(folder_path, images)
        
        columns = 5
        row = 0
        col = 0
        
        for image_name in sorted_images:
            img_path = os.path.join(folder_path, image_name)
            size_mb = os.path.getsize(img_path) / (1024 * 1024)
            
            try:
                img = Image.open(img_path)
                img.thumbnail((120, 120))
                photo = ImageTk.PhotoImage(img)
                self.image_refs.append(photo)
                
                card = tk.Frame(self.scrollable_frame, bd=2, relief=tk.GROOVE, width=140, height=170)
                card.grid(row=row, column=col, padx=10, pady=10)
                card.grid_propagate(False)
                
                lbl_img = tk.Label(card, image=photo)
                lbl_img.pack(pady=5)
                
                short_name = image_name if len(image_name) <= 15 else image_name[:12] + "..."
                
                lbl_text = tk.Label(card, text=f"{short_name}\n{size_mb:.2f} MB", font=("Arial", 9))
                lbl_text.pack()
                
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
                    
            except Exception as e:
                print(f"Не удалось загрузить {image_name}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGalleryApp(root)
    root.mainloop()