import pygame
import random
import math
import numpy as np

# 1. إعدادات النافذة واللعبة
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chicken Invaders - 15 Levels Edition")
clock = pygame.time.Clock()

# --- دالة توليد الأصوات الديناميكية (تتغير مع كل مستوى) ---
def generate_sound(freq, duration=0.1, sound_type="laser"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    if sound_type == "laser":
        freq_decay = np.linspace(freq, freq * 0.3, n_samples)
        wave = np.sin(2 * np.pi * freq_decay * t)
    elif sound_type == "explosion":
        wave = np.random.uniform(-1, 1, n_samples) * np.exp(-t * 15)
    elif sound_type == "powerup":
        freq_rise = np.linspace(freq, freq * 2, n_samples)
        wave = np.sin(2 * np.pi * freq_rise * t)
    else:
        wave = np.sin(2 * np.pi * freq * t)
        
    audio = (wave * 32767).astype(np.int16)
    audio_stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(audio_stereo)

# الألوان الأساسية
BLACK = (15, 15, 30)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)
GREEN = (50, 220, 80)
ORANGE = (255, 140, 0)

# لوحات ألوان متعددة للمستويات الـ 15 (تتغير تلقائياً)
LEVEL_THEMES = [
    ((15, 15, 35),   (50, 150, 255), (240, 240, 240), (255, 255, 200), (255, 220, 0)),   # L1
    ((20, 10, 40),   (0, 220, 200),  (255, 200, 200), (255, 180, 180), (0, 255, 150)),   # L2
    ((30, 15, 20),   (255, 100, 100),(255, 230, 150), (255, 255, 100), (255, 50, 50)),   # L3
    ((10, 30, 20),   (100, 255, 100),(200, 255, 200), (180, 255, 180), (50, 255, 255)),  # L4
    ((35, 20, 10),   (255, 165, 0),  (255, 215, 0),   (255, 235, 150), (255, 100, 0)),   # L5
    ((25, 25, 50),   (180, 100, 255),(220, 180, 255), (230, 200, 255), (200, 0, 255)),   # L6
    ((40, 10, 30),   (255, 20, 147), (255, 182, 193), (255, 192, 203), (255, 0, 128)),   # L7
    ((10, 40, 40),   (0, 255, 255),  (175, 238, 238), (220, 255, 255), (0, 200, 255)),   # L8
    ((30, 30, 10),   (200, 200, 50), (240, 230, 140), (255, 250, 205), (255, 255, 50)),  # L9
    ((40, 20, 0),    (255, 69, 0),   (255, 160, 122), (255, 218, 185), (255, 140, 0)),  # L10
    ((20, 20, 20),   (190, 190, 190),(220, 220, 220), (245, 245, 245), (255, 255, 255)), # L11
    ((15, 35, 15),   (50, 205, 50),  (152, 251, 152), (240, 255, 240), (127, 255, 0)),  # L12
    ((30, 0, 50),    (138, 43, 226), (216, 191, 216), (230, 230, 250), (186, 85, 211)),  # L13
    ((50, 25, 0),    (218, 165, 32), (255, 228, 181), (255, 248, 220), (255, 215, 0)),  # L14
    ((50, 0, 0),     (255, 0, 0),    (255, 99, 71),   (255, 160, 122), (255, 0, 255))   # L15
]

# 2. فئة المركبة (اللاعب)
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 70
        self.speed = 7
        self.weapon_level = 1
        self.score = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 30:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 30:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 50:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - 40:
            self.y += self.speed

    def draw(self, surface, level):
        theme = LEVEL_THEMES[(level - 1) % len(LEVEL_THEMES)]
        ship_color = theme[1]
        
        wing_span = 20 + (level % 5) * 3
        points = [
            (self.x, self.y - 25),
            (self.x - wing_span, self.y + 15),
            (self.x - 10, self.y + 10),
            (self.x + 10, self.y + 10),
            (self.x + wing_span, self.y + 15)
        ]
        pygame.draw.polygon(surface, ship_color, points)
        cockpit_color = WHITE if level % 2 == 1 else YELLOW
        pygame.draw.circle(surface, cockpit_color, (int(self.x), int(self.y - 5)), 7 + (level % 3))

    def shoot(self, level):
        theme = LEVEL_THEMES[(level - 1) % len(LEVEL_THEMES)]
        laser_color = theme[4]
        bullets = []
        
        if self.weapon_level == 1:
            bullets.append(Bullet(self.x, self.y - 25, 0, laser_color))
        elif self.weapon_level == 2:
            bullets.append(Bullet(self.x - 10, self.y - 20, 0, laser_color))
            bullets.append(Bullet(self.x + 10, self.y - 20, 0, laser_color))
        else:
            bullets.append(Bullet(self.x, self.y - 25, 0, laser_color))
            bullets.append(Bullet(self.x - 12, self.y - 15, -2, laser_color))
            bullets.append(Bullet(self.x + 12, self.y - 15, 2, laser_color))
        return bullets

# 3. فئة الطلقات
class Bullet:
    def __init__(self, x, y, dx=0, color=YELLOW):
        self.x = x
        self.y = y
        self.dx = dx
        self.speed = 10
        self.color = color

    def move(self):
        self.y -= self.speed
        self.x += self.dx

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x - 3, self.y, 6, 15))

# 4. فئة الفراخ (الأعداء)
class Chicken:
    def __init__(self, level):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-150, -40)
        self.speed_x = random.choice([-2, 2]) + (-1 if level > 7 else 1)
        self.speed_y = 1 + (level * 0.1)
        self.radius = 20
        self.level = level

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= 30 or self.x >= WIDTH - 30:
            self.speed_x *= -1

    def draw(self, surface):
        theme = LEVEL_THEMES[(self.level - 1) % len(LEVEL_THEMES)]
        body_color = theme[2]
        
        pygame.draw.ellipse(surface, body_color, (self.x - 20, self.y - 15, 40, 30))
        pygame.draw.circle(surface, body_color, (int(self.x), int(self.y - 15)), 12)
        pygame.draw.polygon(surface, RED, [(self.x - 4, self.y - 25), (self.x, self.y - 30), (self.x + 4, self.y - 25)])
        pygame.draw.polygon(surface, ORANGE, [(self.x - 4, self.y - 12), (self.x, self.y - 6), (self.x + 4, self.y - 12)])
        pygame.draw.circle(surface, BLACK, (int(self.x - 4), int(self.y - 17)), 2)
        pygame.draw.circle(surface, BLACK, (int(self.x + 4), int(self.y - 17)), 2)

# 5. فئة البيض (هجمات الفراخ)
class Egg:
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.speed = 4 + (level * 0.2)
        self.level = level

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        theme = LEVEL_THEMES[(self.level - 1) % len(LEVEL_THEMES)]
        egg_color = theme[3]
        pygame.draw.ellipse(surface, egg_color, (self.x - 5, self.y, 10, 14))

# 6. فئة الترقية (Power-up)
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2.5

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), 10)
        font = pygame.font.SysFont("Arial", 12, bold=True)
        text = font.render("P", True, WHITE)
        surface.blit(text, (self.x - 4, self.y - 7))

# --- شاشة الفوز وإعادة اللعب ---
def show_victory_screen(final_score):
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    sub_font = pygame.font.SysFont("Arial", 28, bold=True)
    info_font = pygame.font.SysFont("Arial", 22)
    
    waiting = True
    while waiting:
        screen.fill((10, 10, 25))
        
        title_text = title_font.render("VICTORY! YOU BEAT ALL LEVELS!", True, YELLOW)
        score_text = sub_font.render(f"Final Score: {final_score}", True, WHITE)
        restart_text = info_font.render("Press 'R' to Restart or 'Q' to Quit", True, GREEN)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3 - 30))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 70))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # إعادة اللعب
                if event.key == pygame.K_q:
                    return False # الخروج

# 7. الحلقة الرئيسية للعبة
def main():
    player = Player()
    current_level = 1
    max_levels = 15
    
    bullets = []
    eggs = []
    powerups = []
    
    chickens_to_kill = 15 + (current_level * 5)
    chickens_killed = 0
    eggs_hit_in_level = 0
    
    chickens = [Chicken(current_level) for _ in range(6 + current_level // 2)]

    font = pygame.font.SysFont("Arial", 22, bold=True)
    running = True
    shoot_cooldown = 0
    level_transition = False

    while running:
        clock.tick(60)
        
        bg_color = LEVEL_THEMES[(current_level - 1) % len(LEVEL_THEMES)][0]
        screen.fill(bg_color)

        laser_freq = 400 + (current_level * 50)
        explosion_freq = 150 + (current_level * 20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # --- حالة الانتقال بين المستويات (صعود المركبة تلقائياً) ---
        if level_transition:
            player.y -= 8
            player.draw(screen, current_level)
            
            if player.y < -50:
                current_level += 1
                
                # عند إكمال الـ 15 مستوى بالكامل
                if current_level > max_levels:
                    restart = show_victory_screen(player.score)
                    if restart:
                        # إعادة ضبط اللعبة بالكامل
                        current_level = 1
                        player = Player()
                        bullets.clear()
                        eggs.clear()
                        powerups.clear()
                        chickens_killed = 0
                        eggs_hit_in_level = 0
                        chickens_to_kill = 15 + (current_level * 5)
                        chickens = [Chicken(current_level) for _ in range(6 + current_level // 2)]
                        level_transition = False
                        continue
                    else:
                        running = False
                        break
                
                player.x = WIDTH // 2
                player.y = HEIGHT - 70
                bullets.clear()
                eggs.clear()
                powerups.clear()
                chickens_killed = 0
                eggs_hit_in_level = 0
                chickens_to_kill = 15 + (current_level * 5)
                chickens = [Chicken(current_level) for _ in range(6 + current_level // 2)]
                level_transition = False

            pygame.display.flip()
            continue

        player.move(keys)

        # الإطلاق عند الضغط على Space
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            bullets.extend(player.shoot(current_level))
            shoot_cooldown = 10
            generate_sound(laser_freq, 0.08, "laser").play()

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        # تحديث حركة الطلقات
        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0 and bullet in bullets:
                bullets.remove(bullet)

        # تحديث حركة الفراخ وإسقاط البيض
        for chicken in chickens[:]:
            chicken.move()

            if random.random() < (0.006 + current_level * 0.001):
                eggs.append(Egg(chicken.x, chicken.y, current_level))

            if chicken.y > HEIGHT + 20:
                chicken.y = random.randint(-100, -40)
                chicken.x = random.randint(50, WIDTH - 50)

        # تحديث البيض
        for egg in eggs[:]:
            egg.move()
            if egg.y > HEIGHT and egg in eggs:
                eggs.remove(egg)

        # تحديث الترقيات
        for p in powerups[:]:
            p.move()
            if p.y > HEIGHT and p in powerups:
                powerups.remove(p)

        # --- تصادم الطلقات مع الفراخ ---
        for bullet in bullets[:]:
            for chicken in chickens[:]:
                dist = math.hypot(bullet.x - chicken.x, bullet.y - chicken.y)
                if dist < chicken.radius + 5:
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if chicken in chickens:
                        chickens.remove(chicken)
                    
                    player.score += 1
                    chickens_killed += 1

                    generate_sound(explosion_freq, 0.12, "explosion").play()

                    if random.random() < 0.20:
                        powerups.append(PowerUp(chicken.x, chicken.y))

                    if chickens_killed + len(chickens) < chickens_to_kill:
                        chickens.append(Chicken(current_level))
                    break

        if chickens_killed >= chickens_to_kill and len(chickens) == 0:
            level_transition = True

        # --- تصادم البيض مع اللاعب ---
        for egg in eggs[:]:
            dist = math.hypot(egg.x - player.x, egg.y - player.y)
            if dist < 20:
                if egg in eggs:
                    eggs.remove(egg)
                
                eggs_hit_in_level += 1
                player.weapon_level = max(1, player.weapon_level - 1)
                
                generate_sound(200, 0.15, "explosion").play()

                if eggs_hit_in_level >= 5:
                    eggs_hit_in_level = 0
                    chickens_killed = 0
                    bullets.clear()
                    eggs.clear()
                    powerups.clear()
                    player.x = WIDTH // 2
                    player.y = HEIGHT - 70
                    chickens = [Chicken(current_level) for _ in range(6 + current_level // 2)]

        # --- تصادم الترقيات مع اللاعب ---
        for p in powerups[:]:
            dist = math.hypot(p.x - player.x, p.y - player.y)
            if dist < 25:
                if p in powerups:
                    powerups.remove(p)
                player.weapon_level = min(3, player.weapon_level + 1)
                generate_sound(600, 0.2, "powerup").play()

        # --- الرسم ---
        player.draw(screen, current_level)

        for bullet in bullets:
            bullet.draw(screen)

        for chicken in chickens:
            chicken.draw(screen)

        for egg in eggs:
            egg.draw(screen)

        for p in powerups:
            p.draw(screen)

        score_text = font.render(f"Score: {player.score}", True, WHITE)
        level_text = font.render(f"Level: {current_level}/{max_levels}", True, YELLOW)
        eggs_text = font.render(f"Eggs Hit: {eggs_hit_in_level}/5", True, RED)
        weapon_text = font.render(f"Weapon Lvl: {player.weapon_level}", True, GREEN)

        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 35))
        screen.blit(eggs_text, (10, 60))
        screen.blit(weapon_text, (WIDTH - 170, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()