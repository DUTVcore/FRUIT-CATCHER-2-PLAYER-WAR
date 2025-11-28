import os
import sys # <--- [MỚI] Cần thiết để kiểm tra môi trường PyInstaller

# --- CẤU HÌNH MÀN HÌNH ---
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
GAME_CAPTION = "Fruit Catcher"

# --- MÀU SẮC CƠ BẢN ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_BTN = (0, 128, 255)
CYAN = (0, 255, 255) # <--- [MỚI] Màu cho tính năng Shield

# -----------------------------------------------------------------
# --- ĐƯỜNG DẪN (ĐÃ SỬA CHO PYINSTALLER) ---
# [SỬA LỖI] Logic xác định thư mục gốc khi code đã được đóng gói
if getattr(sys, 'frozen', False):
    # Nếu đang chạy file .exe (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Nếu đang chạy file .py bình thường
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(folder, filename):
    return os.path.join(BASE_DIR, folder, filename)
# -----------------------------------------------------------------

# --- TÊN FILE ẢNH ---
IMG_FILES = {
    "bucket": "bucket.png",
    "bomb": "bomb.png",
    "heart": "heart.png",
    "return": "return_to_menu.png",
    "volume": "volume.png",
    "mute": "mute.png",
    "logo": "logo_bkdn.png"
}

FRUIT_FILES = ["apple.png", "banana.png", "watermelon.png", "strawberry.png"]

# --- CẤU HÌNH BACKGROUND 4 MÙA ---
# (Tên file, Màu dự phòng nếu lỗi)
BG_CONFIG = [
    ("bg_spring.png", (144, 238, 144)),  # Xuân (0-9 điểm)
    ("bg_summer.png", (255, 255, 224)),  # Hạ (10-19 điểm)
    ("bg_autumn.png", (255, 228, 181)),  # Thu (20-29 điểm)
    ("bg_winter.png", (224, 255, 255))  # Đông (30-39 điểm)
]

# --- LUẬT CHƠI ---
RULES_TEXT = [
    "1. Dung phim MUI TEN TRAI/PHAI de di chuyen.",
    "2. Hung trai cay de ghi diem.",
    "3. Tranh bom! Dung vao bom se mat mang.",
    "4. De rot trai cay cung se mat mang.",
    "5. Game ket thuc khi het 3 mang.",
]