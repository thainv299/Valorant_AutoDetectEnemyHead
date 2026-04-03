# File: main.py
import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from ultralytics import YOLO

from aim_logic import calculate_aim_vector

class YoloTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valorant AI - Aim Assist Tester")
        self.root.geometry("500x480") 
        self.root.resizable(False, False)

        self.model_path = ""
        self.video_path = ""

        # --- TIÊU ĐỀ ---
        tk.Label(root, text="YOLO FOV & AIM TESTER", font=("Arial", 16, "bold"), fg="#FF4655").pack(pady=15)

        # --- CHỌN MODEL & VIDEO ---
        frame_top = tk.Frame(root)
        frame_top.pack(fill="x", padx=20)
        
        self.btn_model = tk.Button(frame_top, text="1. Chọn Model (.pt)", command=self.load_model, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=18)
        self.btn_model.grid(row=0, column=0, pady=5)
        self.lbl_model = tk.Label(frame_top, text="Chưa chọn model...", fg="gray")
        self.lbl_model.grid(row=0, column=1, padx=10, sticky="w")

        self.btn_video = tk.Button(frame_top, text="2. Chọn Video (.mp4)", command=self.load_video, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=18)
        self.btn_video.grid(row=1, column=0, pady=5)
        self.lbl_video = tk.Label(frame_top, text="Chưa chọn video...", fg="gray")
        self.lbl_video.grid(row=1, column=1, padx=10, sticky="w")

        # --- CÀI ĐẶT THÔNG SỐ (CONFIDENCE & FOV) ---
        frame_settings = tk.Frame(root)
        frame_settings.pack(fill="x", padx=20, pady=15)
        
        # Thanh Confidence
        tk.Label(frame_settings, text="Độ tự tin (Conf):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.conf_slider = tk.Scale(frame_settings, from_=0.1, to=0.9, resolution=0.05, orient="horizontal", length=250)
        self.conf_slider.set(0.4)
        self.conf_slider.grid(row=0, column=1, padx=10)

        # Thanh Bán kính FOV
        tk.Label(frame_settings, text="Bán kính FOV (px):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.fov_slider = tk.Scale(frame_settings, from_=50, to=500, resolution=10, orient="horizontal", length=250)
        self.fov_slider.set(150) # Mặc định FOV 150 pixel
        self.fov_slider.grid(row=1, column=1, padx=10)

        # --- TÙY CHỌN LƯU VIDEO ---
        self.save_var = tk.BooleanVar(value=False)
        self.chk_save = tk.Checkbutton(root, text="Lưu lại video kết quả (runs/detect/)", variable=self.save_var, font=("Arial", 10))
        self.chk_save.pack(pady=5)

        # --- NÚT START ---
        self.btn_start = tk.Button(root, text="BẮT ĐẦU TEST FOV", command=self.run_inference, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_start.pack(pady=10, fill="x", padx=50)
        tk.Label(root, text="* Mẹo: Bấm phím 'q' trên màn hình video để thoát", fg="gray", font=("Arial", 9, "italic")).pack()

    def load_model(self):
        path = filedialog.askopenfilename(filetypes=[("PyTorch Model", "*.pt")])
        if path:
            self.model_path = path
            self.lbl_model.config(text=os.path.basename(path), fg="blue")
            self.check_ready()

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv")])
        if path:
            self.video_path = path
            self.lbl_video.config(text=os.path.basename(path), fg="blue")
            self.check_ready()

    def check_ready(self):
        if self.model_path and self.video_path:
            self.btn_start.config(state=tk.NORMAL)

    def run_inference(self):
        self.btn_start.config(text="ĐANG CHẠY...", state=tk.DISABLED)
        self.root.update()

        try:
            # Load model & Sửa lỗi tên class bị tráo
            model = YOLO(self.model_path)
            model.model.names = {0: 'head', 1: 'enemy'}
            
            conf_value = float(self.conf_slider.get())
            is_save = self.save_var.get()
            
            # Khởi tạo OpenCV đọc video
            cap = cv2.VideoCapture(self.video_path)
            
            # Setup VideoWriter nếu người dùng muốn lưu video
            out = None
            if is_save:
                os.makedirs("runs/detect", exist_ok=True)
                width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                out = cv2.VideoWriter('runs/detect/fov_test_result.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            # VÒNG LẶP XỬ LÝ TỪNG KHUNG HÌNH (FRAME BY FRAME)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break 
                
                # Cập nhật liên tục FOV từ thanh trượt (để có thể kéo thanh trượt lúc đang chạy)
                current_fov = int(self.fov_slider.get())
                
                # Tính toán tọa độ tâm của màn hình video
                h, w, _ = frame.shape
                center_x, center_y = w // 2, h // 2

                # Chạy nhận diện YOLO
                results = model(frame, conf=conf_value, iou=0.45, verbose=False)[0]
                
                # Vẽ Tâm ngắm (Dấu cộng màu xanh lá)
                cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), (0, 255, 0), 2)
                cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), (0, 255, 0), 2)
                
                # Vẽ Vòng tròn FOV (Màu xám nhạt)
                cv2.circle(frame, (center_x, center_y), current_fov, (200, 200, 200), 1)

                # Xử lý từng vật thể nhận diện được
                for box in results.boxes:
                    cls = int(box.cls[0].cpu().numpy())
                    
                    # CHỈ XỬ LÝ NẾU LÀ CLASS HEAD (ID 0)
                    if cls == 0:
                        # Lấy tọa độ
                        xyxy = box.xyxy[0].cpu().numpy()
                        
                        in_fov, tx, ty, dx, dy = calculate_aim_vector(xyxy, center_x, center_y, current_fov)
                        
                        # Vẽ Bounding Box quanh cái đầu (Màu Đỏ)
                        cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 0, 255), 2)
                        
                        # Hiệu ứng: NẾU ĐỊCH VÀO TRONG FOV
                        if in_fov:
                            # Vẽ đường ngắm (Vector) từ tâm màn hình đến đầu địch (Màu Vàng)
                            cv2.line(frame, (center_x, center_y), (tx, ty), (0, 255, 255), 2)
                            # Hiển thị chữ LOCKED 
                            cv2.putText(frame, f"LOCKED! (dx:{dx}, dy:{dy})", (tx + 20, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Hiển thị kết quả
                cv2.imshow("Valorant FOV Tester", frame)
                if out:
                    out.write(frame)

                # Cho phép OpenCV cập nhật màn hình và chờ phím 'q' để thoát
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            if out: out.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Hoàn tất", "Đã chạy xong video!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi:\n{str(e)}")
        finally:
            self.btn_start.config(text="BẮT ĐẦU TEST FOV", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoloTesterApp(root)
    root.mainloop()