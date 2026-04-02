import os
import yaml
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class UltraYoloNormalizer:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Multi-Folder Normalizer (Train/Val/Test)")
        self.root.geometry("650x700")
        
        self.yaml_path = ""
        self.root_dir = ""
        self.old_classes = []
        self.entry_widgets = []

        # UI
        tk.Label(root, text="TOOL CHUẨN HÓA DATASET VALORANT", font=("Arial", 14, "bold")).pack(pady=10)

        self.btn_yaml = tk.Button(root, text="1. Chọn file data.yaml", command=self.load_yaml, bg="#FF9800", fg="white", font=("Arial", 10, "bold"))
        self.btn_yaml.pack(pady=5, padx=20, fill='x')

        self.btn_dir = tk.Button(root, text="2. Chọn thư mục gốc (Chứa train, val, test)", command=self.load_root_dir, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.btn_dir.pack(pady=5, padx=20, fill='x')

        self.info_label = tk.Label(root, text="Hãy chọn file YAML để bắt đầu", fg="blue")
        self.info_label.pack(pady=5)

        self.frame_scroll = tk.Frame(root)
        self.frame_scroll.pack(pady=10, fill='both', expand=True)
        
        self.canvas = tk.Canvas(self.frame_scroll)
        self.scrollbar = ttk.Scrollbar(self.frame_scroll, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.btn_save = tk.Button(root, text="3. BẮT ĐẦU CHUẨN HÓA TẤT CẢ", command=self.process, bg="#2196F3", fg="white", font=("Arial", 12, "bold"), state=tk.DISABLED)
        self.btn_save.pack(pady=20, padx=20, fill='x')

    def load_yaml(self):
        path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                names = data.get('names', [])
                self.old_classes = names if isinstance(names, list) else list(names.values())
            self.yaml_path = path
            self.btn_dir.config(state=tk.NORMAL)
            self.render_classes()

    def load_root_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.root_dir = path
            self.info_label.config(text=f"Thư mục gốc: {os.path.basename(path)}\n(Sẽ quét cả train, val, test)")
            self.btn_save.config(state=tk.NORMAL)

    def render_classes(self):
        for w in self.scrollable_frame.winfo_children(): w.destroy()
        self.entry_widgets = []
        tk.Label(self.scrollable_frame, text="Tên cũ trong YAML", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10)
        tk.Label(self.scrollable_frame, text="Tên mới mong muốn", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=10)
        
        for i, name in enumerate(self.old_classes):
            tk.Label(self.scrollable_frame, text=f"{i}: {name}", width=20, anchor="w").grid(row=i+1, column=0, padx=10, pady=2)
            ent = tk.Entry(self.scrollable_frame, width=25)
            ent.insert(0, name)
            ent.grid(row=i+1, column=1, padx=10, pady=2)
            self.entry_widgets.append(ent)

    def process(self):
        new_names = [e.get().strip() for e in self.entry_widgets]
        unique_names = []
        for n in new_names:
            if n not in unique_names: unique_names.append(n)
        
        mapping = {old_id: unique_names.index(name) for old_id, name in enumerate(new_names)}
        
        count = 0
        # os.walk quét qua mọi thư mục con (train, val, test...)
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".txt") and file != "classes.txt":
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    new_lines = []
                    changed = False
                    
                    for line in lines:
                        parts = line.split()
                        
                        # 1. Nếu là dòng trống hoặc dòng ghi chú (bắt đầu bằng #), bỏ qua việc xử lý nhưng vẫn giữ lại trong file
                        if not parts or parts[0].startswith('#'):
                            new_lines.append(line)
                            continue
                            
                        # 2. Bắt lỗi an toàn khi ép kiểu sang số nguyên
                        try:
                            old_id = int(parts[0])
                            # Nếu ID này nằm trong danh sách cần đổi
                            if old_id in mapping:
                                parts[0] = str(mapping[old_id])
                                new_lines.append(" ".join(parts) + "\n")
                                changed = True
                            else:
                                # Giữ nguyên dòng nếu không nằm trong diện cần đổi
                                new_lines.append(line) 
                        except ValueError:
                            # Nếu gặp ký tự lạ không thể chuyển thành số (ví dụ: chữ cái rác), bỏ qua lỗi và giữ nguyên dòng
                            new_lines.append(line)
                    
                    # Chỉ ghi đè lại file nếu có sự thay đổi thực sự
                    if changed:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        count += 1

        # Cập nhật lại file YAML
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            y_data = yaml.safe_load(f)
            
        y_data['nc'] = len(unique_names)
        y_data['names'] = unique_names
        
        with open(self.yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(y_data, f, sort_keys=False, allow_unicode=True)

        messagebox.showinfo("Xong!", f"Đã quét toàn bộ thư mục!\nSửa thành công {count} file nhãn, tự động bỏ qua các file chứa ký tự rác.")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltraYoloNormalizer(root)
    root.mainloop()