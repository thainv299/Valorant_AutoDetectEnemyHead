import math
import win32api
import win32con

def calculate_aim_vector(box, center_x, center_y, fov_radius):
    x_min, y_min, x_max, y_max = box
    
    target_x = int((x_min + x_max) / 2)
    target_y = int((y_min + y_max) / 2)
    
    distance = math.sqrt((target_x - center_x)**2 + (target_y - center_y)**2)
    
    if distance <= fov_radius:
        dx = target_x - center_x
        dy = target_y - center_y
        return True, target_x, target_y, dx, dy
    else:
        return False, target_x, target_y, 0, 0

def apply_smooth_and_move(dx, dy, smooth_factor, enable_mouse):
    # Áp dụng hệ số làm mượt (VD: dx=100, smooth=0.2 -> chỉ di chuyển 20px)
    move_x = dx * smooth_factor
    move_y = dy * smooth_factor
    
    # Thực thi di chuột (Nếu người dùng cho phép trên UI)
    if enable_mouse:
        # win32con.MOUSEEVENTF_MOVE ra lệnh cho Windows di chuyển chuột tương đối
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(move_x), int(move_y), 0, 0)
        
    return int(move_x), int(move_y)