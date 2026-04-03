import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from ultralytics import YOLO

from aim_logic import calculate_aim_vector, apply_smooth_and_move

class YoloTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Valorant AI - Aim Assist Tester")
        self.root.geometry("520x560")
        self.root.resizable(False, False)

        self.model_path = ""
        self.video_path = ""

        tk.Label(root, text="YOLO FOV & AIM TESTER", font=("Arial", 16, "bold"), fg="#FF4655").pack(pady=15)

        frame_top = tk.Frame(root)
        frame_top.pack(fill="x", padx=20)
        
        self.btn_model = tk.Button(frame_top, text="1. Chọn Model (.pt)", command=self.load_model, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=18)
        self.btn_model.grid(row=0, column=0, pady=5)
        self.lbl_model = tk.Label(frame_top, text="Chưa chọn...", fg="gray")
        self.lbl_model.grid(row=0, column=1, padx=10, sticky="w")

        self.btn_video = tk.Button(frame_top, text="2. Chọn Video (.mp4)", command=self.load_video, font=("Arial", 10, "bold"), bg="#2B2D31", fg="white", width=18)
        self.btn_video.grid(row=1, column=0, pady=5)
        self.lbl_video = tk.Label(frame_top, text="Chưa chọn...", fg="gray")
        self.lbl_video.grid(row=1, column=1, padx=10, sticky="w")

        # --- CÀI ĐẶT THÔNG SỐ (CONF, FOV, SMOOTH) ---
        frame_settings = tk.Frame(root)
        frame_settings.pack(fill="x", padx=20, pady=15)
        
        tk.Label(frame_settings, text="Độ tự tin (Conf):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.conf_slider = tk.Scale(frame_settings, from_=0.1, to=0.9, resolution=0.05, orient="horizontal", length=250)
        self.conf_slider.set(0.4)
        self.conf_slider.grid(row=0, column=1, padx=10)

        tk.Label(frame_settings, text="Bán kính FOV (px):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.fov_slider = tk.Scale(frame_settings, from_=50, to=500, resolution=10, orient="horizontal", length=250)
        self.fov_slider.set(150)
        self.fov_slider.grid(row=1, column=1, padx=10)

        # Thanh trượt độ mượt
        tk.Label(frame_settings, text="Độ mượt (Smooth):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.smooth_slider = tk.Scale(frame_settings, from_=0.01, to=1.0, resolution=0.01, orient="horizontal", length=250)
        self.smooth_slider.set(0.2) # Mặc định 0.2 (20% tốc độ thực)
        self.smooth_slider.grid(row=2, column=1, padx=10)

        # --- TÙY CHỌN NGUY HIỂM: DI CHUỘT THẬT ---
        self.mouse_var = tk.BooleanVar(value=False)
        self.chk_mouse = tk.Checkbutton(root, text="[NGUY HIỂM] Kích hoạt rê chuột thực tế (win32api)", variable=self.mouse_var, font=("Arial", 10, "bold"), fg="red")
        self.chk_mouse.pack(pady=5)

        self.save_var = tk.BooleanVar(value=False)
        self.chk_save = tk.Checkbutton(root, text="Lưu lại video kết quả", variable=self.save_var, font=("Arial", 10))
        self.chk_save.pack()

        # --- NÚT START ---
        self.btn_start = tk.Button(root, text="BẮT ĐẦU TEST", command=self.run_inference, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.btn_start.pack(pady=15, fill="x", padx=50)
        tk.Label(root, text="* Bấm phím 'q' trên màn hình video để thoát", fg="gray", font=("Arial", 9, "italic")).pack()

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
            model = YOLO(self.model_path)
            model.model.names = {0: 'head', 1: 'enemy'}
            
            conf_value = float(self.conf_slider.get())
            is_save = self.save_var.get()
            
            cap = cv2.VideoCapture(self.video_path)
            out = None
            if is_save:
                os.makedirs("runs/detect", exist_ok=True)
                w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                out = cv2.VideoWriter('runs/detect/aim_test.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break 
                
                # Lấy thông số Real-time từ thanh trượt
                current_fov = int(self.fov_slider.get())
                current_smooth = float(self.smooth_slider.get())
                enable_mouse = self.mouse_var.get()
                
                height, width, _ = frame.shape
                center_x, center_y = width // 2, height // 2

                results = model(frame, conf=conf_value, iou=0.45, verbose=False)[0]

                # Vẽ FOV và Tâm ngắm
                cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), (0, 255, 0), 2)
                cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), (0, 255, 0), 2)
                cv2.circle(frame, (center_x, center_y), current_fov, (200, 200, 200), 1)

                for box in results.boxes:
                    cls = int(box.cls[0].cpu().numpy())
                    if cls == 0:
                        xyxy = box.xyxy[0].cpu().numpy()
                        
                        # Tính khoảng cách FOV
                        in_fov, tx, ty, dx, dy = calculate_aim_vector(xyxy, center_x, center_y, current_fov)
                        
                        cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 0, 255), 2)
                        
                        if in_fov:
                            # XỬ LÝ MƯỢT VÀ RÊ CHUỘT 
                            move_x, move_y = apply_smooth_and_move(dx, dy, current_smooth, enable_mouse)
                            
                            # Vẽ đường ngắm gốc 
                            cv2.line(frame, (center_x, center_y), (tx, ty), (0, 255, 255), 1)
                            
                            # Hiển thị thông số trên màn hình
                            cv2.putText(frame, f"RAW: ({dx}, {dy})", (tx + 10, ty - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                            cv2.putText(frame, f"MOUSE: ({move_x}, {move_y})", (tx + 10, ty + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                cv2.imshow("Valorant AI - Smooth Aim", frame)
                if out: out.write(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            if out: out.release()
            cv2.destroyAllWindows()
            messagebox.showinfo("Hoàn tất", "Test thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
        finally:
            self.btn_start.config(text="BẮT ĐẦU TEST", state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoloTesterApp(root)
    root.mainloop()