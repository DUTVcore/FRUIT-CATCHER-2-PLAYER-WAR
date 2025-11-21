import pygame
import random
import os
from settings import *

# [MỚI] Thêm màu cho khiên (nếu settings.py chưa có)
CYAN = (0, 255, 255)

# --- KHỞI TẠO ---
pygame.init()
pygame.mixer.init()

# --- HÀM TẢI ẢNH AN TOÀN ---
def safe_load_image(folder, filename, size, fallback_color=(200, 200, 200)):
    path = get_path(folder, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    except (pygame.error, FileNotFoundError):
        print(f"[Warning] Khong tim thay '{filename}'. Dung mau thay the.")
        surface = pygame.Surface(size)
        surface.fill(fallback_color)
        return surface

# --- CLASS HIỆU ỨNG CHỮ ---
class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color, font):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.life = 60 
        self.velocity = -1

    def update(self):
        self.rect.y += self.velocity
        self.life -= 1
        if self.life <= 0:
            self.kill()

# --- CLASS GAME CHÍNH ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_CAPTION)
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.header_font = pygame.font.SysFont(None, 72)
        
        self.load_resources()
        
        self.highest_score = 0
        self.floating_texts = pygame.sprite.Group()
        self.return_to_menu = True
        self.is_mute = False
        
        self.reset_game()

    def load_resources(self):
        # 1. Âm thanh
        self.music_loaded = False 
        self.bomb_sound = None
        self.score_sound = None
        self.lost_life_sound = None
        
        try:
            song_path = get_path("sounds", "game_song.mp3")
            pygame.mixer.music.load(song_path)
            self.music_loaded = True
        except Exception as e:
            print(f"Khong tai duoc nhac nen: {e}")
            self.music_loaded = False

        try:
            if os.path.exists(get_path("sounds", "bomb.mp3")):
                self.bomb_sound = pygame.mixer.Sound(get_path("sounds", "bomb.mp3"))
            if os.path.exists(get_path("sounds", "coin.mp3")):
                self.score_sound = pygame.mixer.Sound(get_path("sounds", "coin.mp3"))
            if os.path.exists(get_path("sounds", "lost_life.mp3")):
                self.lost_life_sound = pygame.mixer.Sound(get_path("sounds", "lost_life.mp3"))
        except Exception as e:
            print(f"Loi tai hieu ung am thanh: {e}")

        # 2. Hình ảnh cơ bản
        self.bucket_img = safe_load_image("imgs", IMG_FILES["bucket"], (50, 50), (0,0,255))
        self.bomb_img = safe_load_image("imgs", IMG_FILES["bomb"], (40, 40), (0,0,0))
        self.heart_img = safe_load_image("imgs", IMG_FILES["heart"], (30, 30), (255,0,0))
        self.return_img = safe_load_image("imgs", IMG_FILES["return"], (30, 30), (100,100,100))
        self.volume_img = safe_load_image("imgs", IMG_FILES["volume"], (30, 30), (200,200,0))
        self.mute_img = safe_load_image("imgs", IMG_FILES["mute"], (30, 30), (200,0,0))
        self.logo_img = safe_load_image("imgs", IMG_FILES["logo"], (100, 100), WHITE)

        # [MỚI] 3. Tải và phân loại trái cây (Quan trọng)
        # Thay vì chỉ lưu ảnh, ta lưu cả 'type' để biết nó là quả gì
        self.fruit_data = [] 
        for f_name in FRUIT_FILES:
            img = safe_load_image("imgs", f_name, (40, 40), (0, 255, 0))
            
            # Phân loại dựa vào tên file
            f_type = "normal"
            if "banana" in f_name: 
                f_type = "heal"     # Chuối hồi máu
            elif "apple" in f_name: 
                f_type = "shield"   # Táo bật khiên
            
            self.fruit_data.append({"img": img, "type": f_type})

        # 4. Backgrounds
        self.backgrounds = []
        for filename, fallback_color in BG_CONFIG:
            bg = safe_load_image("imgs", filename, (SCREEN_WIDTH, SCREEN_HEIGHT), fallback_color)
            self.backgrounds.append(bg)

    def reset_game(self):
        self.created_fruits = []    
        self.last_fruit_time = 0
        self.bucket_x = SCREEN_WIDTH // 2 - 25
        self.score = 0
        
        # [MỚI] Cập nhật hệ thống mạng sống
        self.max_lives = 5      # Tối đa 5 mạng
        self.lives = 3          # Bắt đầu với 3 mạng
        
        # [MỚI] Hệ thống khiên
        self.shield_active = False
        self.shield_end_time = 0

        self.game_over = False  
        self.level = 1          
        self.fruit_interval = 1000 
        self.fruit_speed = 1
        self.floating_texts.empty()
        self.current_bg_index = 0

    def level_up(self):
        new_level = (self.score // 10) + 1
        if new_level > self.level:
            self.level = new_level
            self.fruit_speed = min(1 + (self.level - 1) * 0.5, 8.0) # Tăng max speed lên xíu
            new_interval = 1000 - (self.level - 1) * 50
            self.fruit_interval = max(new_interval, 300)

    def draw_background(self):
        self.current_bg_index = (self.score // 10) % 4
        self.screen.blit(self.backgrounds[self.current_bg_index], (0, 0))

    # [GIỮ NGUYÊN] show_start_screen và show_rules_screen (Tôi rút gọn để code không quá dài)
    def show_start_screen(self):
        while True:
            self.draw_background()
            self.screen.blit(self.logo_img, (10, SCREEN_HEIGHT - 110))
            shadow = self.header_font.render(GAME_CAPTION, True, BLACK)
            self.screen.blit(shadow, (198, 103))
            title = self.header_font.render(GAME_CAPTION, True, WHITE)
            self.screen.blit(title, (195, 100))
            start_rect = pygame.Rect(300, 220, 100, 50)
            pygame.draw.rect(self.screen, BLUE_BTN, start_rect)
            self.screen.blit(self.font.render("Start", True, WHITE), (322, 233))
            rules_rect = pygame.Rect(300, 290, 100, 50)
            pygame.draw.rect(self.screen, BLUE_BTN, rules_rect)
            self.screen.blit(self.font.render("Rules", True, WHITE), (317, 303))
            vol_rect = pygame.Rect(650, 10, 30, 30)
            if not self.is_mute: self.screen.blit(self.volume_img, (650, 10))
            else: self.screen.blit(self.mute_img, (650, 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos): return True
                    if rules_rect.collidepoint(event.pos): self.show_rules_screen()
                    if vol_rect.collidepoint(event.pos):
                        self.is_mute = not self.is_mute
                        if self.is_mute: pygame.mixer.music.stop()
                        elif self.music_loaded: pygame.mixer.music.play(-1)
            pygame.display.update()

    def show_rules_screen(self):
        while True:
            self.draw_background()
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(180); s.fill(BLACK)
            self.screen.blit(s, (0,0))
            self.screen.blit(self.header_font.render("Rules", True, WHITE), (270, 50))
            for i, rule in enumerate(RULES_TEXT):
                self.screen.blit(self.font.render(rule, True, WHITE), (50, 150 + i*40))
            back_rect = pygame.Rect(300, 400, 100, 50)
            pygame.draw.rect(self.screen, BLUE_BTN, back_rect)
            self.screen.blit(self.font.render("Back", True, WHITE), (322, 412))
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos): return
            pygame.display.update()

    def move_bucket(self):
        keys = pygame.key.get_pressed()
        speed = 10 
        if keys[pygame.K_LEFT] and self.bucket_x > 0:
            self.bucket_x -= speed
        if keys[pygame.K_RIGHT] and self.bucket_x < SCREEN_WIDTH - 50:
            self.bucket_x += speed

    def create_fruits(self):
        now = pygame.time.get_ticks()
        if now - self.last_fruit_time >= self.fruit_interval:
            is_bomb = random.random() < 0.2
            
            # [MỚI] Chọn loại trái cây từ danh sách data đã tạo
            chosen_fruit = random.choice(self.fruit_data)
            
            fruit = {
                "x": random.randint(0, SCREEN_WIDTH - 40),
                "y": -40,
                "img": self.bomb_img if is_bomb else chosen_fruit["img"],
                "type": "bomb" if is_bomb else chosen_fruit["type"] # Lưu loại (bomb/heal/shield/normal)
            }
            self.created_fruits.append(fruit)
            self.last_fruit_time = now
        
        bucket_rect = pygame.Rect(self.bucket_x, 450, 50, 50)
        
        for f in self.created_fruits[:]:
            f["y"] += self.fruit_speed
            self.screen.blit(f["img"], (f["x"], f["y"]))
            
            f_rect = pygame.Rect(f["x"], f["y"], 40, 40)
            
            # [MỚI] XỬ LÝ VA CHẠM NÂNG CAO
            if bucket_rect.colliderect(f_rect):
                # 1. Nếu là BOM
                if f["type"] == "bomb":
                    if self.shield_active:
                        # Nếu có khiên: Không mất mạng
                        self.floating_texts.add(FloatingText("Blocked!", f["x"], f["y"], CYAN, self.font))
                        if self.score_sound: self.score_sound.play() # Sound effect đỡ đòn (tạm dùng sound coin)
                    else:
                        # Không có khiên: Mất mạng
                        if self.bomb_sound: self.bomb_sound.play()
                        self.lives -= 1
                        self.floating_texts.add(FloatingText("-1 Heart", f["x"], f["y"], (255,0,0), self.font))
                
                # 2. Nếu là TRÁI CÂY
                else:
                    if self.score_sound: self.score_sound.play()
                    self.score += 1
                    self.level_up()
                    
                    # Logic Hồi máu (Banana)
                    if f["type"] == "heal":
                        if self.lives < self.max_lives:
                            self.lives += 1
                            self.floating_texts.add(FloatingText("+1 Heart", f["x"], f["y"], (255,100,200), self.font))
                        else:
                            self.floating_texts.add(FloatingText("Max Hearts", f["x"], f["y"], (200,200,200), self.font))
                    
                    # Logic Khiên (Apple)
                    elif f["type"] == "shield":
                        self.shield_active = True
                        self.shield_end_time = pygame.time.get_ticks() + 3000 # 3000ms = 3 giây
                        self.floating_texts.add(FloatingText("Shield ON!", f["x"], f["y"], CYAN, self.font))
                    
                    else:
                        # Trái cây thường
                        self.floating_texts.add(FloatingText("+1", f["x"], f["y"], (255,255,0), self.font))

                self.created_fruits.remove(f)

            elif f["y"] > SCREEN_HEIGHT:
                self.created_fruits.remove(f)
                if f["type"] != "bomb":
                    if self.lost_life_sound: self.lost_life_sound.play()
                    self.lives -= 1
                    self.floating_texts.add(FloatingText("Miss!", f["x"], 480, (255,0,0), self.font))
            
            if self.lives <= 0: self.game_over = True

    def display_hud(self):
        score_txt = f"Score: {self.score} | Level: {self.level}"
        self.screen.blit(self.font.render(score_txt, True, BLACK), (12,12))
        self.screen.blit(self.font.render(score_txt, True, WHITE), (10,10))
        
        # [MỚI] Hiển thị mạng sống (vòng lặp vẽ heart img)
        for i in range(self.lives):
            self.screen.blit(self.heart_img, (10 + i*35, 50))
            
        self.screen.blit(self.return_img, (660, 10))
        return pygame.Rect(660, 10, 30, 30)

    def display_game_over(self):
        self.screen.blit(self.header_font.render("Game Over", True, WHITE), (225, 100))
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE), (300, 180))
        self.screen.blit(self.font.render(f"High Score: {self.highest_score}", True, WHITE), (260, 230))
        res_rect = pygame.Rect(300, 300, 100, 50)
        pygame.draw.rect(self.screen, BLUE_BTN, res_rect)
        self.screen.blit(self.font.render("Restart", True, WHITE), (310, 310))
        quit_rect = pygame.Rect(300, 370, 100, 50)
        pygame.draw.rect(self.screen, BLUE_BTN, quit_rect)
        self.screen.blit(self.font.render("Quit", True, WHITE), (322, 380))
        self.screen.blit(self.return_img, (660, 10))
        return res_rect, quit_rect, pygame.Rect(660, 10, 30, 30)

    def run(self):
        if not self.is_mute and self.music_loaded:
            pygame.mixer.music.play(-1)
        
        while True:
            self.draw_background()
            
            # [MỚI] KIỂM TRA THỜI GIAN KHIÊN
            if self.shield_active:
                current_time = pygame.time.get_ticks()
                if current_time > self.shield_end_time:
                    self.shield_active = False
                    self.floating_texts.add(FloatingText("Shield OFF", self.bucket_x, 430, (200,200,200), self.font))

            if self.return_to_menu:
                if self.show_start_screen():
                    self.reset_game()
                    self.return_to_menu = False
            
            elif not self.game_over:
                if self.score > self.highest_score: self.highest_score = self.score
                
                # Vẽ xô hứng
                self.screen.blit(self.bucket_img, (self.bucket_x, 450))
                
                # [MỚI] VẼ KHIÊN NẾU ĐANG KÍCH HOẠT (Vòng tròn quanh xô)
                if self.shield_active:
                    pygame.draw.circle(self.screen, CYAN, (self.bucket_x + 25, 475), 40, 3) # Vòng tròn rỗng độ dày 3

                self.move_bucket()
                self.create_fruits()
                self.floating_texts.update()
                self.floating_texts.draw(self.screen)
                
                rtm_rect = self.display_hud()
                if pygame.mouse.get_pressed()[0] and rtm_rect.collidepoint(pygame.mouse.get_pos()):
                    self.return_to_menu = True

            else:
                res, qui, rtm = self.display_game_over()
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if res.collidepoint(pos): self.reset_game()
                    if qui.collidepoint(pos): pygame.quit(); quit()
                    if rtm.collidepoint(pos): self.return_to_menu = True

            self.clock.tick(120)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); quit()

if __name__ == "__main__":
    game = Game()
    game.run()