# wizard_game.py

import pygame
import sys
import time

pygame.init()

# --- Основные настройки ---
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Righteous Wizard")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# --- Загрузка ассетов ---
backgrounds = [pygame.image.load(f"level{i}.png") for i in range(9)]
wizard_img = pygame.image.load("wizard.png")
wizard_cast_img = pygame.image.load("wizard_cast.png")
shield_img = pygame.image.load("shield.png")
fireball_img = pygame.image.load("fireball.png")
lightning_img = pygame.image.load("lightning.png")
frog_img = pygame.image.load("frog.png")
zombie_img = pygame.image.load("zombie.png")
skeleton_img = pygame.image.load("skeleton.png")
antiwizard_img = pygame.image.load("antiwizard.png")

fireball_sound = pygame.mixer.Sound("fireball.wav")
lightning_sound = pygame.mixer.Sound("lightning.wav")
shield_sound = pygame.mixer.Sound("shield.wav")

pygame.mixer.music.load("background.mp3")
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)

# --- Классы ---
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = fireball_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def update(self):
        self.rect.x += 15 * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Lightning(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = lightning_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.spawn_time = time.time()

    def update(self):
        self.rect.x += 20 * self.direction
        if time.time() - self.spawn_time > 5 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image, hp=1):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.death_time = None
        self.is_boss = False
        self.last_fire = 0
        self.shield_active = False
        self.shield_time = 0
        self.boss_phase = 0

    def update(self, player):
        if self.alive:
            if self.is_boss:
                self.boss_behavior(player)
            else:
                if player.rect.x > self.rect.x:
                    self.rect.x += 2
                else:
                    self.rect.x -= 2
        elif self.death_time and time.time() - self.death_time > 3:
            self.kill()

    def boss_behavior(self, player):
        now = time.time()
        
        if self.boss_phase == 1:
            if not self.shield_active:
                self.activate_shield()
                self.boss_phase = 2
        elif self.boss_phase == 2:
            if now - self.last_fire > 6:
                self.fire(player)
                self.last_fire = now

    def fire(self, player):
        direction = 1 if player.rect.x > self.rect.x else -1
        lightning = Lightning(self.rect.centerx + 30 * direction, self.rect.centery, direction)
        fireballs.add(lightning)
        lightning_sound.play()

    def take_damage(self):
        if not (self.is_boss and self.shield_active):
            self.hp -= 1
            if self.hp <= 0:
                self.image = pygame.transform.flip(pygame.transform.rotate(self.original_image, 90), True, False)
                self.alive = False
                self.death_time = time.time()

    def activate_shield(self):
        if not self.shield_active:
            self.shield_active = True
            self.shield_time = time.time()
            shield_sound.play()

    def update_shield(self):
        if self.shield_active and time.time() - self.shield_time > 5:
            self.shield_active = False

class Player:
    def __init__(self):
        self.image = wizard_img
        self.rect = None
        self.vel_y = 0
        self.jump = False
        self.on_ground = True
        self.last_fire = 0
        self.last_shield = 0
        self.shield_active = False
        self.shield_time = 0
        self.direction = 1
        self.alive = True
        self.can_move = False
        self.can_fire = False
        self.can_shield = False

    def spawn(self, x, y):
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.alive = True
        self.can_move = False
        self.can_fire = False
        self.can_shield = False
        self.shield_active = False

    def move(self, keys):
        if not self.can_move or not self.alive or not self.rect:
            return
            
        if keys[pygame.K_a]:
            self.rect.x -= 5
            self.direction = -1
        if keys[pygame.K_d]:
            self.rect.x += 5
            self.direction = 1

    def apply_gravity(self):
        if not self.rect:
            return
            
        self.vel_y += 1
        self.rect.y += self.vel_y
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

    def jump_action(self):
        if not self.can_move or not self.alive or not self.on_ground or not self.rect:
            return
            
        self.vel_y = -20
        self.on_ground = False

    def fire(self):
        if not self.can_fire or not self.alive or not self.rect:
            return
            
        now = time.time()
        if now - self.last_fire > 1.5:
            fireball = Fireball(self.rect.centerx + 30 * self.direction, self.rect.centery, self.direction)
            fireballs.add(fireball)
            self.last_fire = now
            fireball_sound.play()

    def activate_shield(self):
        if not self.can_shield or not self.alive or not self.rect:
            return
            
        now = time.time()
        if not self.shield_active and now - self.last_shield > 3:
            self.shield_active = True
            self.shield_time = now
            self.last_shield = now
            shield_sound.play()

    def update(self):
        if self.shield_active and time.time() - self.shield_time > 5:
            self.shield_active = False

    def draw(self):
        if not self.rect:
            return
            
        if not self.alive:
            dead_image = pygame.transform.rotate(self.image, 90)
            screen.blit(dead_image, self.rect)
        else:
            if self.shield_active or time.time() - self.last_fire < 0.3:
                screen.blit(wizard_cast_img, self.rect)
            else:
                screen.blit(self.image, self.rect)
            if self.shield_active:
                shield_rect = shield_img.get_rect(center=(self.rect.centerx + 20, self.rect.centery))
                screen.blit(shield_img, shield_rect)

    def draw_shield_cooldown(self):
        if not self.rect:
            return
            
        cooldown_left = max(0, 3 - (time.time() - self.last_shield))
        cooldown_percent = min(1, cooldown_left / 3)
        
        bar_width = 100
        bar_height = 15
        fill_width = int(bar_width * (1 - cooldown_percent))
        
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 200, 0), (10, 10, bar_width - fill_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, bar_width, bar_height), 2)
        
        if cooldown_left > 0:
            text = font.render(f"{cooldown_left:.1f}s", True, (255, 255, 255))
            screen.blit(text, (15, 30))

def draw_dialog(text, pos, show_enter=True):
    box = pygame.Surface((350, 120))
    box.fill((255, 255, 255))
    pygame.draw.rect(box, (0, 0, 0), box.get_rect(), 2)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        txt_surf = font.render(line, True, (0, 0, 0))
        box.blit(txt_surf, (15, 15 + i * 30))
    
    if show_enter:
        enter_text = font.render("Нажми ENTER", True, (0, 0, 0))
        box.blit(enter_text, (15, 75))
    
    screen.blit(box, (pos[0] - 175, pos[1] - 140))

def reset_game():
    global level, player, fireballs, enemies, dialog_index, boss_dialog_index
    global zombie, skeleton1, skeleton2, antiwizard
    
    level = 0
    player = Player()
    fireballs = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    dialog_index = 0
    boss_dialog_index = 0

    zombie = Enemy(1000, HEIGHT - 50, zombie_img, hp=1)
    skeleton1 = Enemy(900, HEIGHT - 50, skeleton_img, hp=2)
    skeleton2 = Enemy(1050, HEIGHT - 50, skeleton_img, hp=2)
    antiwizard = Enemy(1000, HEIGHT - 50, antiwizard_img, hp=4)
    antiwizard.is_boss = True

# Инициализация игры
reset_game()

# Диалоги
dialogs_lvl1 = [
    "Привет, маг!\nВперёд тебя ждёт путь...",
    "Сначала нажми SPACE,\nчтобы выстрелить!",
    "Теперь нажми F,\nчтобы включить щит!",
    "Отлично! Теперь ты готов\nк путешествию!"
]

boss_dialogs = [
    "Я долго ждал этой встречи...",
    "Ты смог одолеть моих скелетов, но",
    "Ты не сможешь одолеть меня - тебе конец"
]

while True:
    screen.blit(backgrounds[level], (0, 0))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if level == 8 and event.key == pygame.K_RETURN:
                reset_game()
                continue
                
            if level == 0 and event.key == pygame.K_RETURN:
                level = 1
                player.spawn(100, HEIGHT - 50)
            
            if level == 1 and event.key == pygame.K_RETURN:
                if dialog_index < len(dialogs_lvl1) - 1:
                    dialog_index += 1
                    
                    if dialog_index == 1:
                        player.can_fire = True
                    elif dialog_index == 2:
                        player.can_shield = True
                    elif dialog_index == 3:
                        player.can_move = True
                
                if dialog_index == 1 and event.key == pygame.K_SPACE:
                    player.fire()
                elif dialog_index == 2 and event.key == pygame.K_f:
                    player.activate_shield()
            
            if level == 6 and event.key == pygame.K_RETURN and boss_dialog_index < len(boss_dialogs):
                boss_dialog_index += 1
                
                if boss_dialog_index == len(boss_dialogs):
                    antiwizard.boss_phase = 1
                    player.can_move = True
                    player.can_fire = True
                    player.can_shield = True
            
            if event.key == pygame.K_w and (level != 1 or dialog_index == 3) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.jump_action()
            elif event.key == pygame.K_SPACE and (level != 1 or dialog_index >= 1) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.fire()
            elif event.key == pygame.K_f and (level != 1 or dialog_index >= 2) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.activate_shield()

    if player.rect:
        player.move(keys)
        player.apply_gravity()
        player.update()
        fireballs.update()
        
        for enemy in enemies:
            enemy.update(player)
            if enemy.is_boss:
                enemy.update_shield()

        # Проверка столкновений снарядов
        for projectile in fireballs:
            # Проверка столкновения молнии босса с игроком
            if isinstance(projectile, Lightning) and player.rect and player.alive:
                if player.shield_active:
                    shield_rect = shield_img.get_rect(center=(player.rect.centerx + 20, player.rect.centery))
                    if projectile.rect.colliderect(shield_rect):
                        projectile.kill()
                        continue
                elif projectile.rect.colliderect(player.rect):
                    player.alive = False
                    level = 8
                    projectile.kill()
                    continue
            
            # Проверка столкновения с врагами
            for enemy in enemies:
                if projectile.rect.colliderect(enemy.rect) and enemy.alive and not (enemy.is_boss and isinstance(projectile, Lightning)):
                    enemy.take_damage()
                    projectile.kill()

        if level == 1:
            if dialog_index < len(dialogs_lvl1):
                screen.blit(frog_img, (WIDTH//2, HEIGHT - 180))
                draw_dialog(dialogs_lvl1[dialog_index], (WIDTH//2, HEIGHT - 180))
            
            if dialog_index == len(dialogs_lvl1) - 1 and player.rect.right >= WIDTH:
                level = 2
                player.rect.midbottom = (50, HEIGHT - 50)

        elif level == 2:
            if player.rect.right >= WIDTH:
                level = 3
                player.rect.midbottom = (50, HEIGHT - 50)
                enemies.add(zombie)

        elif level == 3:
            if not zombie.alive and not any(e.alive for e in enemies):
                if player.rect.right >= WIDTH:
                    level = 4
                    player.rect.midbottom = (50, HEIGHT - 50)
                    enemies.empty()
                    enemies.add(skeleton1, skeleton2)

        elif level == 4:
            if all(not s.alive for s in [skeleton1, skeleton2]) and not any(e.alive for e in enemies):
                if player.rect.right >= WIDTH:
                    level = 5
                    player.rect.midbottom = (50, HEIGHT - 50)

        elif level == 5:
            screen.blit(frog_img, (WIDTH//2, HEIGHT - 180))
            draw_dialog("Финальная битва\nвпереди. Удачи, маг!", (WIDTH//2, HEIGHT - 180), show_enter=False)
            if player.rect.right >= WIDTH:
                level = 6
                player.rect.midbottom = (50, HEIGHT - 50)
                enemies.empty()
                enemies.add(antiwizard)
                player.can_move = False
                player.can_fire = False
                player.can_shield = False
                boss_dialog_index = 0

        elif level == 6:
            if boss_dialog_index < len(boss_dialogs):
                draw_dialog(boss_dialogs[boss_dialog_index], (WIDTH//2, HEIGHT - 180))
            
            if not antiwizard.alive:
                level = 7

        elif level == 7:
            if player.rect.right >= WIDTH:
                level = 0
                reset_game()

        for enemy in enemies:
            if player.rect.colliderect(enemy.rect) and enemy.alive:
                if not player.shield_active and player.alive:
                    player.alive = False
                    level = 8

    if player.rect:
        for enemy in enemies:
            if enemy.alive or (enemy.death_time and time.time() - enemy.death_time <= 3):
                screen.blit(enemy.image, enemy.rect)
                if enemy.shield_active:
                    shield_rect = shield_img.get_rect(center=(enemy.rect.centerx + 20, enemy.rect.centery))
                    screen.blit(shield_img, shield_rect)
        
        player.draw()
        fireballs.draw(screen)
        
        player.draw_shield_cooldown()

    pygame.display.flip()
    clock.tick(60)