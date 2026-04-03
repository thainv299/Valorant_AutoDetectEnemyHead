import math
def calculate_aim_vector(box, center_x, center_y, fov_radius):
    x_min, y_min, x_max, y_max = box
    
    # Tính tâm của Bounding Box (Đầu địch)
    target_x = int((x_min + x_max) / 2)
    target_y = int((y_min + y_max) / 2)
    
    # Tính khoảng cách Pytago
    distance = math.sqrt((target_x - center_x)**2 + (target_y - center_y)**2)
    
    # Kiểm tra FOV
    if distance <= fov_radius:
        # Nếu nằm trong vòng tròn FOV -> Trả về True và khoảng cách cần vẩy chuột
        dx = target_x - center_x
        dy = target_y - center_y
        return True, target_x, target_y, dx, dy
    else:
        # Nằm ngoài FOV -> Bỏ qua
        return False, target_x, target_y, 0, 0