from ultralytics import YOLO

def main():
    model = YOLO("models/yolo26n.pt") 

    results = model.train(
        data="đường_dẫn_tới_file_data.yaml_của_bạn",
        epochs=150,               
        imgsz=640,                
        batch=16,                 
        device=0,                 
        workers=4,                
        project="Valorant_AI",    
        name="yolo26n_head_v1",   
        patience=30,          

        # --- DATA AUGMENTATION ---
        
        # Giữ nguyên màu viền đỏ/vàng/tím của địch. Chỉnh quá sẽ làm mất đặc trưng này.
        hsv_h=0.015,  # Thay đổi dải màu rất ít
        hsv_s=0.45,    # Tăng độ đậm màu để viền kẻ địch nổi bật hơn
        hsv_v=0.4,    # Đổi độ sáng tối để mô hình quen với các map tối (như Abyss, Split)
        
        # 2. Biến đổi hình học
        degrees=0.0,  # Không xoay ảnh (Agent trong Valorant luôn đứng thẳng, không đi lộn lộn)
        translate=0.1,# Dịch chuyển ảnh nhẹ (10%)
        scale=0.35,    # Zoom in/Zoom out (Giúp nhận diện đầu agent từ cực xa đến ngay trước mặt)
        shear=0.0,    # Không bóp méo hình (Góc nhìn trong game là cố định)
        perspective=0.0, 
        
        # 3. Lật ảnh
        flipud=0.0,   # Tuyệt đối KHÔNG lật dọc (agent không đi bằng đầu)
        fliplr=0.5,   # Có 50% cơ hội lật ngang (Vì địch có thể thò đầu từ góc trái hoặc phải)
        
        # 4. Kỹ thuật nâng cao cho vật thể nhỏ (Small Object)
        mosaic=1.0,   # Luôn bật (100%). Ép 4 ảnh vào 1. Giúp mô hình bắt vật thể nhỏ cực tốt.
        mixup=0.0,    # Tắt Mixup (Chống bóng mờ, làm nhiễu viền màu của agent)
        copy_paste = 0.3,
        erasing=0.2   # Random xóa 1 phần ảnh (20%). Mô phỏng việc agent bị che sau thùng hàng (wallbang)
    )

if __name__ == '__main__':
    main()