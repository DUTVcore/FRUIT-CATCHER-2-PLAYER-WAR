# =========================================================
# FILE: game.py
# MO TA:
# File chinh cua game Fruit Catcher
# Quan ly toan bo logic, hien thi va vong lap game
# =========================================================

import pygame
import random
import os
import math
from settings import *

# =========================================================
# KHOI TAO PYGAME
# =========================================================
pygame.init()
pygame.mixer.init()

# =========================================================
# HAM TAO ANH PLACEHOLDER
# Dung khi thieu hoac loi file anh
# =========================================================
def create_placeholder(color, text, size=(40, 40)):
    """
    Tao anh tron don gian co chu o giua
    Dung khi khong load duoc asset that
    """
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.circle(
        surf, color,
        (size[0] // 2, size[1] // 2),
        size[0] // 2
    )
    font = pygame.font.SysFont(None, 20)
    txt = font.render(text, True, (255, 255, 255))
    surf.blit(txt, txt.get_rect(center=(size[0] // 2, size[1] // 2)))
    return surf

# =========================================================
# HAM LOAD ANH AN TOAN
# Neu loi hoac thieu file -> dung placeholder
# =========================================================
def safe_load_image(folder, filename, size, fallback_color=(200, 200, 200)):
    """
    Load anh tu thu muc asset
    Neu that bai thi tra ve anh placeholder
    """
    path = get_path(folder, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    except (pygame.error, FileNotFoundError):
        return create_placeholder(fallback_color, "?", size)

# =========================================================
# CLASS FLOATING TEXT
# Hien thi chu noi bay len va bien mat
# =========================================================
class FloatingText(pygame.sprite.Sprite):
    """
    Sprite chu noi (Level up, +1, Blocked, ...)
    """
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

# =========================================================
# CLASS PARTICLE
# Hieu ung hat no khi bat vat pham
# =========================================================
class Particle(pygame.sprite.Sprite):
    """
    Hieu ung hat vo nho bay ra ngau nhien
    """
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(4, 8)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.uniform(-4, 4)
        self.vel_y = random.uniform(-4, 4)
        self.life = random.randint(20, 40)
        self.gravity = 0.2

    def update(self):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()

# =========================================================
# CLASS GAME
# Quan ly toan bo game
# =========================================================
class Game:
    def __init__(self):
        # Tao cua so game
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption(GAME_CAPTION)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.header_font = pygame.font.SysFont(None, 60)

        # Load tai nguyen
        self.load_resources()

        # Bien quan ly chung
        self.highest_score = 0
        self.floating_texts = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        self.return_to_menu = True
        self.is_mute = False
        self.screen_shake = 0

        self.game_mode = 1
        self.reset_game(1)

    # =====================================================
    # LOAD TAT CA TAI NGUYEN
    # =====================================================
    def load_resources(self):
        # -------------------------
        # 1. AM THANH
        # -------------------------
        self.music_loaded = False
        self.bomb_sound = None
        self.score_sound = None
        self.lost_life_sound = None

        try:
            pygame.mixer.music.load(
                get_path("sounds", "game_song.mp3")
            )
            self.music_loaded = True
        except:
            pass

        def load_snd(name):
            p = get_path("sounds", name)
            return pygame.mixer.Sound(p) if os.path.exists(p) else None

        self.bomb_sound = load_snd("bomb.mp3")
        self.score_sound = load_snd("coin.mp3")
        self.lost_life_sound = load_snd("lost_life.mp3")

        # -------------------------
        # 2. HINH ANH
        # -------------------------
        base_bucket = safe_load_image(
            "imgs", IMG_FILES["bucket"], (50, 50)
        )

        self.bucket_p1_img = base_bucket.copy()
        self.bucket_p1_img.fill(
            COLOR_P1 if "COLOR_P1" in globals() else (255, 0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        self.bucket_p2_img = base_bucket.copy()
        self.bucket_p2_img.fill(
            COLOR_P2 if "COLOR_P2" in globals() else (0, 255, 255),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        self.bomb_img = safe_load_image(
            "imgs", IMG_FILES["bomb"], (40, 40), (0, 0, 0)
        )
        self.heart_img = safe_load_image(
            "imgs", IMG_FILES["heart"], (25, 25), (255, 0, 0)
        )
        self.return_img = safe_load_image(
            "imgs", IMG_FILES["return"], (30, 30)
        )
        self.volume_img = safe_load_image(
            "imgs", IMG_FILES["volume"], (30, 30)
        )
        self.mute_img = safe_load_image(
            "imgs", IMG_FILES["mute"], (30, 30)
        )
        self.logo_img = safe_load_image(
            "imgs", IMG_FILES["logo"], (100, 100)
        )

        self.boss_img = safe_load_image(
            "imgs", "boss_monkey.png", (80, 80), (100, 0, 0)
        )

        # -------------------------
        # 3. TRAI CAY VA ITEM
        # -------------------------
        self.fruit_data = []
        for f_name in FRUIT_FILES:
            img = safe_load_image("imgs", f_name, (40, 40))
            f_type = "normal"
            if "banana" in f_name:
                f_type = "heal"
            elif "apple" in f_name:
                f_type = "shield"
            self.fruit_data.append({
                "img": img,
                "type": f_type
            })

        self.item_magnet_img = safe_load_image(
            "imgs", "item_magnet.png", (40, 40)
        )
        self.item_freeze_img = safe_load_image(
            "imgs", "item_freeze.png", (40, 40)
        )
        self.item_poison_img = safe_load_image(
            "imgs", "item_poison.png", (40, 40)
        )
        self.item_tnt_img = safe_load_image(
            "imgs", "item_tnt.png", (40, 40)
        )

        # -------------------------
        # 4. BACKGROUND
        # -------------------------
        self.backgrounds = []
        for filename, fallback_color in BG_CONFIG:
            bg = safe_load_image(
                "imgs", filename,
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                fallback_color
            )
            self.backgrounds.append(bg)

    # =====================================================
    # RESET TRANG THAI GAME
    # =====================================================
    def reset_game(self, mode=1):
        self.game_mode = mode
        self.created_fruits = []
        self.last_fruit_time = 0
        self.floating_texts.empty()
        self.particles.empty()
        self.screen_shake = 0

        # -------- PLAYER 1 --------
        self.p1_score = 0
        self.p1_lives = 3
        self.p1_x = SCREEN_WIDTH // 2
        self.p1_dead = False
        self.p1_shield = False
        self.p1_magnet = False
        self.p1_confused = False
        self.p1_velocity = 0

        # -------- PLAYER 2 --------
        self.p2_score = 0
        self.p2_lives = 3
        self.p2_x = SCREEN_WIDTH // 2 - 100
        self.p2_dead = (mode == 1)
        self.p2_shield = False
        self.p2_magnet = False
        self.p2_confused = False
        self.p2_velocity = 0

        self.game_over = False
        self.level = 1

        self.base_speed = 3.0
        self.base_interval = 1000
        self.fruit_speed = self.base_speed
        self.fruit_interval = self.base_interval
        self.max_lives = 5

        self.freeze_active = False
        self.boss_active = False
        self.boss_hp = 0
        self.boss_x = SCREEN_WIDTH // 2
        self.boss_dir = 1

    # =====================================================
    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            p = Particle(x, y, color)
            self.particles.add(p)

    def trigger_shake(self, intensity=10):
        self.screen_shake = intensity

    def level_up(self):
        highest_current = max(self.p1_score, self.p2_score)
        new_level = (highest_current // 10) + 1
        
        if new_level > self.level:
            self.level = new_level
            increase_factor = 1.10
            self.fruit_speed = self.base_speed * (increase_factor ** (self.level - 1))
            if self.fruit_speed > 20: self.fruit_speed = 20
            self.fruit_interval = max(self.base_interval * (0.95 ** (self.level - 1)), 250)

            self.floating_texts.add(FloatingText(f"LEVEL {self.level}!", SCREEN_WIDTH//2, 200, WHITE, self.header_font))

            # --- BOSS LOGIC MỚI: Mỗi 4 Level (Chu kỳ 4 mùa) ---
            if self.level % 4 == 0:
                self.boss_active = True
                # Boss trâu hơn theo cấp độ (Máu cơ bản 30 + 5 mỗi level)
                self.boss_hp = 30 + (self.level * 5)
                self.floating_texts.add(FloatingText("BOSS FIGHT!", SCREEN_WIDTH//2, 250, RED, self.header_font))
            else:
                self.boss_active = False

    def draw_background(self):
        current_bg_index = (self.level - 1) % 4
        self.screen.blit(self.backgrounds[current_bg_index], (0, 0))

    def get_season(self):
        return (self.level - 1) % 4 

    def move_buckets(self):
        keys = pygame.key.get_pressed()
        speed = 8 
        season = self.get_season()
        
        # --- P1 ---
        if not self.p1_dead:
            move_dir = 0
            k_left = keys[pygame.K_RIGHT] if self.p1_confused else keys[pygame.K_LEFT]
            k_right = keys[pygame.K_LEFT] if self.p1_confused else keys[pygame.K_RIGHT]

            if k_left: move_dir = -1
            elif k_right: move_dir = 1
            
            if season == 3: # Winter
                accel = 0.5; friction = 0.9
                if move_dir != 0: self.p1_velocity += move_dir * accel
                else: self.p1_velocity *= friction
                self.p1_velocity = max(-10, min(10, self.p1_velocity))
                self.p1_x += self.p1_velocity
            else:
                self.p1_x += move_dir * speed

            self.p1_x = max(0, min(SCREEN_WIDTH - 50, self.p1_x))

        # --- P2 ---
        if self.game_mode == 2 and not self.p2_dead:
            move_dir = 0
            k_a = keys[pygame.K_d] if self.p2_confused else keys[pygame.K_a]
            k_d = keys[pygame.K_a] if self.p2_confused else keys[pygame.K_d]

            if k_a: move_dir = -1
            elif k_d: move_dir = 1

            if season == 3: # Winter
                accel = 0.5; friction = 0.9
                if move_dir != 0: self.p2_velocity += move_dir * accel
                else: self.p2_velocity *= friction
                self.p2_velocity = max(-10, min(10, self.p2_velocity))
                self.p2_x += self.p2_velocity
            else:
                self.p2_x += move_dir * speed

            self.p2_x = max(0, min(SCREEN_WIDTH - 50, self.p2_x))

    def handle_catch(self, player_id, item_type, x, y):
        is_p1 = (player_id == 1)
        
        if item_type == "bomb" or item_type == "boss_bomb":
            has_shield = self.p1_shield if is_p1 else self.p2_shield
            if has_shield:
                self.floating_texts.add(FloatingText("Blocked!", x, y, CYAN if is_p1 else MAGENTA, self.font))
                self.spawn_particles(x, y, (200, 200, 255)) 
                if self.score_sound: self.score_sound.play()
            else:
                if self.bomb_sound: self.bomb_sound.play()
                self.floating_texts.add(FloatingText("-1 Heart", x, y, RED, self.font))
                self.trigger_shake(15) 
                self.spawn_particles(x, y, (255, 50, 50), 20)
                if is_p1: self.p1_lives -= 1
                else: self.p2_lives -= 1
        else:
            if self.score_sound: self.score_sound.play()
            if is_p1: self.p1_score += 1
            else: self.p2_score += 1
            self.level_up()
            self.spawn_particles(x, y, (255, 255, 0))

            if item_type == "heal":
                lives = self.p1_lives if is_p1 else self.p2_lives
                if lives < self.max_lives:
                    self.floating_texts.add(FloatingText("+1 Heart", x, y, (255,100,200), self.font))
                    if is_p1: self.p1_lives += 1
                    else: self.p2_lives += 1
                else:
                    self.floating_texts.add(FloatingText("Full HP", x, y, WHITE, self.font))

            elif item_type == "shield":
                duration = 4000 
                self.floating_texts.add(FloatingText("Shield ON!", x, y, CYAN if is_p1 else MAGENTA, self.font))
                if is_p1: self.p1_shield = True; self.p1_shield_time = pygame.time.get_ticks() + duration
                else: self.p2_shield = True; self.p2_shield_time = pygame.time.get_ticks() + duration
            
            elif item_type == "magnet":
                duration = 5000
                self.floating_texts.add(FloatingText("Magnet!", x, y, (128, 0, 128), self.font))
                if is_p1: self.p1_magnet = True; self.p1_magnet_time = pygame.time.get_ticks() + duration
                else: self.p2_magnet = True; self.p2_magnet_time = pygame.time.get_ticks() + duration

            elif item_type == "freeze":
                duration = 5000
                self.floating_texts.add(FloatingText("Freeze!", x, y, (0, 191, 255), self.font))
                self.freeze_active = True
                self.freeze_end_time = pygame.time.get_ticks() + duration

            elif item_type == "poison":
                duration = 3000
                self.floating_texts.add(FloatingText("Confused!", x, y, (0, 100, 0), self.font))
                target_p1 = not is_p1 if self.game_mode == 2 else True 
                
                if target_p1: 
                    self.p1_confused = True; self.p1_confused_time = pygame.time.get_ticks() + duration
                    if self.game_mode == 2: self.floating_texts.add(FloatingText("P1 Dizzy!", self.p1_x, 400, (0,255,0), self.font))
                else: 
                    self.p2_confused = True; self.p2_confused_time = pygame.time.get_ticks() + duration
                    self.floating_texts.add(FloatingText("P2 Dizzy!", self.p2_x, 400, (0,255,0), self.font))

            elif item_type == "tnt":
                self.floating_texts.add(FloatingText("BOOM!", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, (255, 165, 0), self.header_font))
                self.trigger_shake(20)
                self.created_fruits.clear()
                self.spawn_particles(x, y, (255, 100, 0), 30)

            else:
                color = (255,255,0) if is_p1 else (0,255,255)
                self.floating_texts.add(FloatingText("+1", x, y, color, self.font))

    def create_and_check_fruits(self):
        now = pygame.time.get_ticks()
        season = self.get_season()

        current_speed_mult = 1.0
        if self.freeze_active:
            if now < self.freeze_end_time: current_speed_mult = 0.2 
            else: self.freeze_active = False

        if season == 1: current_speed_mult *= 1.3

        spawn_rate = self.fruit_interval
        if self.boss_active: spawn_rate = 400 

        if now - self.last_fruit_time >= spawn_rate:
            is_bomb = False; chosen_img = None; chosen_type = "normal"
            roll = random.random()
            
            if self.boss_active:
                # --- BOSS BOMBS INCREASE LOGIC ---
                # Tỉ lệ bom gốc là 55%. Mỗi lần gặp boss (mỗi 4 level), tăng thêm 5%
                # Min 90% (Để còn 10% cơ hội rơi vật phẩm cứu trợ)
                bomb_chance = min(0.90, 0.55 + (self.level // 4) * 0.05)
                
                if roll < bomb_chance: 
                    is_bomb = True; chosen_type = "boss_bomb"; chosen_img = self.bomb_img
                else:
                    # Vật phẩm hỗ trợ
                    chosen_type = "heal"; chosen_img = self.heart_img 
                    for f in self.fruit_data: 
                        if f["type"] == "heal": chosen_img = f["img"]; break
                start_x = self.boss_x
            else:
                if roll < 0.02: chosen_type = "magnet"; chosen_img = self.item_magnet_img
                elif roll < 0.04: chosen_type = "freeze"; chosen_img = self.item_freeze_img
                elif roll < 0.06: chosen_type = "tnt"; chosen_img = self.item_tnt_img
                elif roll < 0.08: chosen_type = "poison"; chosen_img = self.item_poison_img
                elif roll < 0.25: is_bomb = True; chosen_type = "bomb"; chosen_img = self.bomb_img
                else:
                    data = random.choice(self.fruit_data)
                    chosen_img = data["img"]; chosen_type = data["type"]
                start_x = random.randint(0, SCREEN_WIDTH - 40)

            fruit = {
                "x": float(start_x),
                "y": -40.0 if not self.boss_active else 50.0, 
                "img": chosen_img,
                "type": chosen_type
            }
            self.created_fruits.append(fruit)
            self.last_fruit_time = now
        
        rect_p1 = pygame.Rect(self.p1_x, 450, 50, 50)
        rect_p2 = pygame.Rect(self.p2_x, 450, 50, 50)

        for f in self.created_fruits[:]:
            if not self.created_fruits and f not in self.created_fruits: break

            magnet_p1 = self.p1_magnet and not self.p1_dead
            magnet_p2 = self.p2_magnet and self.game_mode == 2 and not self.p2_dead
            
            if (magnet_p1 or magnet_p2) and f["type"] not in ["bomb", "boss_bomb", "poison"]:
                target_x = self.p1_x
                if magnet_p2:
                    if not magnet_p1: target_x = self.p2_x
                    else: 
                        if abs(f["x"] - self.p2_x) < abs(f["x"] - self.p1_x): target_x = self.p2_x
                f["x"] += (target_x - f["x"]) * 0.05 

            if season == 2 and not self.boss_active:
                f["x"] += math.sin(f["y"] * 0.02) * 2 

            f["y"] += self.fruit_speed * current_speed_mult
            
            self.screen.blit(f["img"], (int(f["x"]), int(f["y"])))
            f_rect = pygame.Rect(int(f["x"]), int(f["y"]), 40, 40)
            caught = False
            
            if not self.p1_dead and rect_p1.colliderect(f_rect):
                self.handle_catch(1, f["type"], f["x"], f["y"])
                caught = True
            elif self.game_mode == 2 and not self.p2_dead and rect_p2.colliderect(f_rect):
                self.handle_catch(2, f["type"], f["x"], f["y"])
                caught = True

            if caught:
                if f in self.created_fruits: self.created_fruits.remove(f)
                continue

            if f["y"] > SCREEN_HEIGHT:
                if f in self.created_fruits: self.created_fruits.remove(f)
                if self.game_mode == 1:
                    is_bad = f["type"] in ["bomb", "boss_bomb", "poison", "tnt"]
                    if not is_bad:
                        if self.lost_life_sound: self.lost_life_sound.play()
                        self.p1_lives -= 1
                        self.floating_texts.add(FloatingText("Miss!", f["x"], 480, RED, self.font))

    def update_boss(self):
        if not self.boss_active: return
        self.boss_x += 3 * self.boss_dir
        if self.boss_x > SCREEN_WIDTH - 80 or self.boss_x < 0: self.boss_dir *= -1
        self.screen.blit(self.boss_img, (self.boss_x, 10))
        self.boss_hp -= 0.05
        if self.boss_hp <= 0:
            self.boss_active = False
            self.spawn_particles(self.boss_x + 40, 50, (255, 255, 255), 50)
            self.floating_texts.add(FloatingText("BOSS DEFEATED!", SCREEN_WIDTH//2, 250, (255, 215, 0), self.header_font))

    def check_status(self):
        if self.p1_lives <= 0: self.p1_dead = True
        if self.p2_lives <= 0: self.p2_dead = True
        
        now = pygame.time.get_ticks()
        
        if self.p1_shield and now > self.p1_shield_time: self.p1_shield = False
        if self.p2_shield and now > self.p2_shield_time: self.p2_shield = False
        if self.p1_magnet and now > self.p1_magnet_time: self.p1_magnet = False
        if self.p2_magnet and now > self.p2_magnet_time: self.p2_magnet = False
        if self.p1_confused and now > self.p1_confused_time: self.p1_confused = False
        if self.p2_confused and now > self.p2_confused_time: self.p2_confused = False

        if self.game_mode == 1:
            if self.p1_dead: self.game_over = True
        else:
            if self.p1_dead or self.p2_dead:
                self.game_over = True

    def display_hud(self):
        if self.game_mode == 1:
            score_txt = f"Score: {self.p1_score} | Level: {self.level}"
            self.screen.blit(self.font.render(score_txt, True, BLACK), (12,12))
            self.screen.blit(self.font.render(score_txt, True, WHITE), (10,10))
            for i in range(self.p1_lives):
                self.screen.blit(self.heart_img, (10 + i*30, 40))
        else:
            c2 = COLOR_P2 if 'COLOR_P2' in globals() else CYAN
            p2_txt = f"P2 (WASD): {self.p2_score}"
            self.screen.blit(self.font.render(p2_txt, True, BLACK), (12, 12))
            self.screen.blit(self.font.render(p2_txt, True, c2), (10, 10))
            if not self.p2_dead:
                for i in range(self.p2_lives):
                    self.screen.blit(self.heart_img, (10 + i*30, 40))
            else:
                self.screen.blit(self.font.render("DEAD", True, RED), (10, 40))

            c1 = COLOR_P1 if 'COLOR_P1' in globals() else (255, 255, 0)
            p1_txt = f"P1 (Arrows): {self.p1_score}"
            txt_surf = self.font.render(p1_txt, True, c1)
            w = txt_surf.get_width()
            self.screen.blit(self.font.render(p1_txt, True, BLACK), (SCREEN_WIDTH - w - 48, 12))
            self.screen.blit(txt_surf, (SCREEN_WIDTH - w - 50, 10))
            if not self.p1_dead:
                for i in range(self.p1_lives):
                    self.screen.blit(self.heart_img, (SCREEN_WIDTH - 40 - i*30, 40))
            else:
                 self.screen.blit(self.font.render("DEAD", True, RED), (SCREEN_WIDTH - 80, 40))

            lvl = self.font.render(f"LVL {self.level}", True, WHITE)
            self.screen.blit(lvl, (SCREEN_WIDTH//2 - 20, 10))
        
        if self.freeze_active:
             self.screen.blit(self.item_freeze_img, (SCREEN_WIDTH//2 - 20, 40))

        self.screen.blit(self.return_img, (660, 10))
        return pygame.Rect(660, 10, 30, 30)

    def display_game_over(self):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200); s.fill(BLACK)
        self.screen.blit(s, (0,0))

        self.screen.blit(self.header_font.render("GAME OVER", True, WHITE), (220, 50))
        
        if self.game_mode == 1:
            score_txt = f"Score: {self.p1_score}"
            if self.p1_score > self.highest_score: self.highest_score = self.p1_score
            high_txt = f"High Score: {self.highest_score}"
            
            self.screen.blit(self.font.render(score_txt, True, WHITE), (300, 150))
            self.screen.blit(self.font.render(high_txt, True, WHITE), (280, 200))
        else:
            p1_res = f"Player 1: {self.p1_score}"
            p2_res = f"Player 2: {self.p2_score}"
            c1 = COLOR_P1 if 'COLOR_P1' in globals() else (255, 255, 0)
            c2 = COLOR_P2 if 'COLOR_P2' in globals() else CYAN

            if self.p1_dead and not self.p2_dead:
                winner = "PLAYER 2 WINS!"; win_col = c2
            elif self.p2_dead and not self.p1_dead:
                winner = "PLAYER 1 WINS!"; win_col = c1
            else:
                if self.p1_score > self.p2_score: winner = "PLAYER 1 WINS!"; win_col = c1
                elif self.p2_score > self.p1_score: winner = "PLAYER 2 WINS!"; win_col = c2
                else: winner = "DRAW!"; win_col = WHITE
                
            self.screen.blit(self.header_font.render(winner, True, win_col), (180, 130))
            self.screen.blit(self.font.render(p1_res, True, c1), (200, 200))
            self.screen.blit(self.font.render(p2_res, True, c2), (400, 200))

        res_rect = pygame.Rect(300, 300, 100, 50)
        pygame.draw.rect(self.screen, BLUE_BTN, res_rect)
        self.screen.blit(self.font.render("Restart", True, WHITE), (315, 315))
        
        quit_rect = pygame.Rect(300, 370, 100, 50)
        pygame.draw.rect(self.screen, BLUE_BTN, quit_rect)
        self.screen.blit(self.font.render("Quit", True, WHITE), (328, 385))
        
        self.screen.blit(self.return_img, (660, 10))
        return res_rect, quit_rect, pygame.Rect(660, 10, 30, 30)

    def show_start_screen(self):
        while True:
            self.draw_background()
            self.screen.blit(self.logo_img, (10, SCREEN_HEIGHT - 110))
            title = self.header_font.render("FRUIT CATCHER", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH//2 - 150, 80))

            btn_1p = pygame.Rect(250, 200, 200, 50)
            pygame.draw.rect(self.screen, BLUE_BTN, btn_1p, border_radius=10)
            self.screen.blit(self.font.render("1 Player", True, WHITE), (305, 215))

            btn_2p = pygame.Rect(250, 270, 200, 50)
            pygame.draw.rect(self.screen, (255, 140, 0), btn_2p, border_radius=10)
            self.screen.blit(self.font.render("2 Players", True, WHITE), (300, 285))

            btn_rules = pygame.Rect(250, 340, 200, 50)
            pygame.draw.rect(self.screen, (100, 100, 100), btn_rules, border_radius=10)
            self.screen.blit(self.font.render("Rules", True, WHITE), (320, 355))

            vol_rect = pygame.Rect(650, 10, 30, 30)
            if not self.is_mute: self.screen.blit(self.volume_img, (650, 10))
            else: self.screen.blit(self.mute_img, (650, 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_1p.collidepoint(event.pos): return 1
                    if btn_2p.collidepoint(event.pos): return 2
                    if btn_rules.collidepoint(event.pos): self.show_rules_screen()
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
            self.screen.blit(self.header_font.render("Rules", True, WHITE), (270, 30))
            
            for i, rule in enumerate(RULES_TEXT):
                self.screen.blit(self.font.render(rule, True, WHITE), (50, 100 + i*35))
                
            back_rect = pygame.Rect(300, 420, 100, 50)
            pygame.draw.rect(self.screen, BLUE_BTN, back_rect)
            self.screen.blit(self.font.render("Back", True, WHITE), (322, 432))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos): return
            pygame.display.update()

    def run(self):
        if not self.is_mute and self.music_loaded:
            pygame.mixer.music.play(-1)
        
        while True:
            if self.return_to_menu:
                selected_mode = self.show_start_screen() 
                self.reset_game(selected_mode)
                self.return_to_menu = False
            
            elif not self.game_over:
                self.draw_background()
                self.update_boss()

                if not self.p1_dead:
                    shake_x = self.p1_x + (random.randint(-5,5) if self.screen_shake>0 else 0)
                    shake_y = 450 + (random.randint(-5,5) if self.screen_shake>0 else 0)
                    self.screen.blit(self.bucket_p1_img, (shake_x, shake_y))
                    if self.p1_shield:
                        c1_shield = COLOR_P2 if 'COLOR_P2' in globals() else CYAN
                        pygame.draw.circle(self.screen, c1_shield, (int(shake_x + 25), int(shake_y + 25)), 40, 3)
                    if self.p1_magnet:
                         pygame.draw.circle(self.screen, (128, 0, 128), (int(shake_x + 25), int(shake_y + 25)), 45, 1)

                if self.game_mode == 2 and not self.p2_dead:
                    shake_x = self.p2_x + (random.randint(-5,5) if self.screen_shake>0 else 0)
                    shake_y = 450 + (random.randint(-5,5) if self.screen_shake>0 else 0)
                    self.screen.blit(self.bucket_p2_img, (shake_x, shake_y))
                    if self.p2_shield:
                        c2_shield = COLOR_P1 if 'COLOR_P1' in globals() else MAGENTA
                        pygame.draw.circle(self.screen, c2_shield, (int(shake_x + 25), int(shake_y + 25)), 40, 3)
                    if self.p2_magnet:
                         pygame.draw.circle(self.screen, (128, 0, 128), (int(shake_x + 25), int(shake_y + 25)), 45, 1)
                
                if self.screen_shake > 0: self.screen_shake -= 1

                self.move_buckets()
                self.create_and_check_fruits()
                self.check_status()
                
                self.particles.update()
                self.particles.draw(self.screen)
                self.floating_texts.update()
                self.floating_texts.draw(self.screen)
                
                rtm_rect = self.display_hud()
                
                if pygame.mouse.get_pressed()[0]:
                    if rtm_rect.collidepoint(pygame.mouse.get_pos()):
                        self.return_to_menu = True

            else:
                res, qui, rtm = self.display_game_over()
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if res.collidepoint(pos): self.reset_game(self.game_mode)
                    if qui.collidepoint(pos): pygame.quit(); quit()
                    if rtm.collidepoint(pos): self.return_to_menu = True

            self.clock.tick(60) 
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); quit()

if __name__ == "__main__":
    game = Game()
    game.run()