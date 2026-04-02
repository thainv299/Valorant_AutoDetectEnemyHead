import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ultralytics import YOLO

class YoloTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valorant AI - Model Tester")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.model_path = ""
        self.video_path = ""

        # --- TIÊU ĐỀ ---
        tk.Label(root, text="YOLO MODEL TESTER", font=("Arial", 16, "bold"), fg="#FF4655").pack(pady=15)

        # --- CHỌN MODEL ---
        frame_model = tk.Frame(root)
        frame_model.pack(fill="x", padx=20, pady=5)
        
        self.btn_model = tk.Button(frame_model, text="1. Chọn Model (.pt)", command=self.load_model, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=20)
        self.btn_model.pack(side="left")
        
        self.lbl_model = tk.Label(frame_model, text="Chưa chọn model...", fg="gray", wraplength=250, justify="left")
        self.lbl_model.pack(side="left", padx=10)

        # --- CHỌN VIDEO ---
        frame_video = tk.Frame(root)
        frame_video.pack(fill="x", padx=20, pady=15)
        
        self.btn_video = tk.Button(frame_video, text="2. Chọn Video (.mp4)", command=self.load_video, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=20)
        self.btn_video.pack(side="left")
        
        self.lbl_video = tk.Label(frame_video, text="Chưa chọn video...", fg="gray", wraplength=250, justify="left")
        self.lbl_video.pack(side="left", padx=10)

        # --- CÀI ĐẶT ĐỘ TỰ TIN (CONFIDENCE) ---
        frame_conf = tk.Frame(root)
        frame_conf.pack(fill="x", padx=20, pady=10)
        
        tk.Label(frame_conf, text="Độ tự tin (Confidence):", font=("Arial", 10, "bold")).pack(side="left")
        
        self.conf_slider = tk.Scale(frame_conf, from_=0.1, to=0.9, resolution=0.05, orient="horizontal", length=200)
        self.conf_slider.set(0.4)  # Mặc định là 0.4
        self.conf_slider.pack(side="right", padx=10)

        # --- TÙY CHỌN LƯU VIDEO ---
        self.save_var = tk.BooleanVar(value=False)
        self.chk_save = tk.Checkbutton(root, text="Lưu lại video kết quả (vào thư mục runs/detect/)", variable=self.save_var, font=("Arial", 10))
        self.chk_save.pack(pady=5)

        # --- NÚT START ---
        self.btn_start = tk.Button(root, text="BẮT ĐẦU NHẬN DIỆN", command=self.run_inference, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_start.pack(pady=20, fill="x", padx=50)

        tk.Label(root, text="* Mẹo: Bấm phím 'q' để dừng xem video sớm", fg="gray", font=("Arial", 9, "italic")).pack()

    def load_model(self):
        path = filedialog.askopenfilename(title="Chọn file weights của YOLO", filetypes=[("PyTorch Model", "*.pt")])
        if path:
            self.model_path = path
            self.lbl_model.config(text=os.path.basename(path), fg="blue")
            self.check_ready()

    def load_video(self):
        path = filedialog.askopenfilename(title="Chọn video gameplay", filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if path:
            self.video_path = path
            self.lbl_video.config(text=os.path.basename(path), fg="blue")
            self.check_ready()

    def check_ready(self):
        if self.model_path and self.video_path:
            self.btn_start.config(state=tk.NORMAL)

    def run_inference(self):
        # Ẩn nút start để tránh bấm đúp
        self.btn_start.config(text="ĐANG CHẠY...", state=tk.DISABLED)
        self.root.update()

        try:
            # 1. Load model
            model = YOLO(self.model_path)
            
            # 2. Lấy thông số từ UI
            conf_value = float(self.conf_slider.get())
            is_save = self.save_var.get()

            # 3. Chạy dự đoán
            messagebox.showinfo("Thông báo", "Bấm OK để bắt đầu.\nCửa sổ video sẽ hiện lên ngay sau đây.\nBấm phím 'q' trên bàn phím để thoát video.")
            
            model.predict(
                source=self.video_path,
                show=True,         # Hiển thị cửa sổ xem trực tiếp
                save=is_save,      # Lưu video hay không
                conf=conf_value,   # Lọc độ tự tin
                iou=0.45           # Chống vẽ đè nhiều box
            )

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi chạy model:\n{str(e)}")
        finally:
            # Khôi phục nút start
            self.btn_start.config(text="BẮT ĐẦU NHẬN DIỆN", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoloTesterApp(root)
    root.mainloop()