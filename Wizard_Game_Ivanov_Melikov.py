# wizard_game.py

import pygame
import sys
import time
from mixer.main import mixer

# Инициализация pygame и микшера для звуков
pygame.init()
pygame.mixer.init()

# --- Основные настройки ---
WIDTH, HEIGHT = 1200, 800  # Размеры игрового окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Righteous Wizard")  # Заголовок окна
clock = pygame.time.Clock()  # Для контроля FPS
font = pygame.font.SysFont("arial", 24)  # Шрифт для текста

# --- Загрузка ассетов ---
# Загрузка фонов для разных уровней
backgrounds = [pygame.image.load(f"level{i}.png") for i in range(9)]
# Загрузка изображений персонажей и эффектов
wizard_img = pygame.image.load("wizard.png")
wizard_cast_img = pygame.image.load("wizard_cast.png")
shield_img = pygame.image.load("shield.png")
fireball_img = pygame.image.load("fireball.png")
lightning_img = pygame.image.load("lightning.png")
frog_img = pygame.image.load("frog.png")
zombie_img = pygame.image.load("zombie.png")
skeleton_img = pygame.image.load("skeleton.png")
antiwizard_img = pygame.image.load("antiwizard.png")

# Загрузка звуковых эффектов
fireball_sound = pygame.mixer.Sound("fireball.wav")
lightning_sound = pygame.mixer.Sound("lightning.wav")
shield_sound = pygame.mixer.Sound("shield.wav")

# Настройка и запуск фоновой музыки
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)  # -1 означает бесконечное воспроизведение

# --- Классы ---
class Fireball(pygame.sprite.Sprite):
    """Класс для огненных шаров, которые выпускает игрок"""
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = fireball_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction  # Направление движения (1 вправо, -1 влево)

    def update(self):
        """Обновление позиции огненного шара"""
        self.rect.x += 15 * self.direction
        # Удаление, если шар вышел за границы экрана
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Lightning(pygame.sprite.Sprite):
    """Класс для молний, которые выпускает босс"""
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = lightning_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.spawn_time = time.time()  # Время создания для ограничения времени жизни

    def update(self):
        """Обновление позиции молнии"""
        self.rect.x += 20 * self.direction
        # Удаление через 5 секунд или при выходе за границы экрана
        if time.time() - self.spawn_time > 5 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    """Базовый класс для врагов"""
    def __init__(self, x, y, image, hp=1):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hp = hp  # Здоровье
        self.max_hp = hp
        self.alive = True  # Жив ли враг
        self.death_time = None  # Время смерти
        self.is_boss = False  # Является ли боссом
        self.last_fire = 0  # Время последней атаки
        self.shield_active = False  # Активен ли щит
        self.shield_time = 0  # Время активации щита
        self.boss_phase = 0  # Фаза босса (для сложного поведения)

    def update(self, player):
        """Обновление состояния врага"""
        if self.alive:
            if self.is_boss:
                self.boss_behavior(player)  # Особое поведение для босса
            else:
                # Простое преследование игрока для обычных врагов
                if player.rect.x > self.rect.x:
                    self.rect.x += 2
                else:
                    self.rect.x -= 2
        elif self.death_time and time.time() - self.death_time > 3:
            self.kill()  # Удаление через 3 секунды после смерти

    def boss_behavior(self, player):
        """Специальное поведение босса"""
        now = time.time()
        
        if self.boss_phase == 1:
            if not self.shield_active:
                self.activate_shield()
                self.boss_phase = 2
        elif self.boss_phase == 2:
            if now - self.last_fire > 6:  # Атака каждые 6 секунд
                self.fire(player)
                self.last_fire = now

    def fire(self, player):
        """Атака босса (выпуск молнии)"""
        direction = 1 if player.rect.x > self.rect.x else -1
        lightning = Lightning(self.rect.centerx + 30 * direction, self.rect.centery, direction)
        fireballs.add(lightning)
        lightning_sound.play()

    def take_damage(self):
        """Получение урона"""
        if not (self.is_boss and self.shield_active):  # Босс неуязвим с активным щитом
            self.hp -= 1
            if self.hp <= 0:
                # Анимация смерти - переворот изображения
                self.image = pygame.transform.flip(pygame.transform.rotate(self.original_image, 90), True, False)
                self.alive = False
                self.death_time = time.time()

    def activate_shield(self):
        """Активация щита"""
        if not self.shield_active:
            self.shield_active = True
            self.shield_time = time.time()
            shield_sound.play()

    def update_shield(self):
        """Обновление состояния щита (деактивация через 5 секунд)"""
        if self.shield_active and time.time() - self.shield_time > 5:
            self.shield_active = False

class Player:
    """Класс игрока (мага)"""
    def __init__(self):
        self.image = wizard_img
        self.rect = None  # Прямоугольник для коллизий
        self.vel_y = 0  # Вертикальная скорость (для прыжка)
        self.jump = False  # В прыжке ли
        self.on_ground = True  # На земле ли
        self.last_fire = 0  # Время последней атаки
        self.last_shield = 0  # Время последней активации щита
        self.shield_active = False  # Активен ли щит
        self.shield_time = 0  # Время активации щита
        self.direction = 1  # Направление взгляда (1 вправо, -1 влево)
        self.alive = True  # Жив ли игрок
        # Флаги доступных действий (изменяются в процессе обучения)
        self.can_move = False
        self.can_fire = False
        self.can_shield = False

    def spawn(self, x, y):
        """Появление игрока на указанных координатах"""
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.alive = True
        self.can_move = False
        self.can_fire = False
        self.can_shield = False
        self.shield_active = False

    def move(self, keys):
        """Движение игрока"""
        if not self.can_move or not self.alive or not self.rect:
            return
            
        if keys[pygame.K_a]:  # Движение влево
            self.rect.x -= 5
            self.direction = -1
        if keys[pygame.K_d]:  # Движение вправо
            self.rect.x += 5
            self.direction = 1

    def apply_gravity(self):
        """Применение гравитации"""
        if not self.rect:
            return
            
        self.vel_y += 1  # Увеличение скорости падения
        self.rect.y += self.vel_y
        # Остановка при достижении "земли"
        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True

    def jump_action(self):
        """Прыжок"""
        if not self.can_move or not self.alive or not self.on_ground or not self.rect:
            return
            
        self.vel_y = -20  # Начальная скорость прыжка
        self.on_ground = False

    def fire(self):
        """Выстрел огненным шаром"""
        if not self.can_fire or not self.alive or not self.rect:
            return
            
        now = time.time()
        if now - self.last_fire > 1.5:  # Ограничение скорости атаки
            fireball = Fireball(self.rect.centerx + 30 * self.direction, self.rect.centery, self.direction)
            fireballs.add(fireball)
            self.last_fire = now
            fireball_sound.play()

    def activate_shield(self):
        """Активация щита"""
        if not self.can_shield or not self.alive or not self.rect:
            return
            
        now = time.time()
        if not self.shield_active and now - self.last_shield > 3:  # Кулдаун 3 секунды
            self.shield_active = True
            self.shield_time = now
            self.last_shield = now
            shield_sound.play()

    def update(self):
        """Обновление состояния игрока"""
        if self.shield_active and time.time() - self.shield_time > 5:
            self.shield_active = False  # Деактивация щита через 5 секунд

    def draw(self):
        """Отрисовка игрока"""
        if not self.rect:
            return
            
        if not self.alive:
            # Анимация смерти - переворот изображения
            dead_image = pygame.transform.rotate(self.image, 90)
            screen.blit(dead_image, self.rect)
        else:
            # Отрисовка в зависимости от состояния
            if self.shield_active or time.time() - self.last_fire < 0.3:
                screen.blit(wizard_cast_img, self.rect)  # Анимация атаки/щита
            else:
                screen.blit(self.image, self.rect)
            if self.shield_active:
                # Отрисовка щита
                shield_rect = shield_img.get_rect(center=(self.rect.centerx + 20, self.rect.centery))
                screen.blit(shield_img, shield_rect)

    def draw_shield_cooldown(self):
        """Отрисовка индикатора кулдауна щита"""
        if not self.rect:
            return
            
        cooldown_left = max(0, 3 - (time.time() - self.last_shield))
        cooldown_percent = min(1, cooldown_left / 3)
        
        # Отрисовка полосы кулдауна
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
    """Отрисовка диалогового окна"""
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
    """Сброс игры в начальное состояние"""
    global level, player, fireballs, enemies, dialog_index, boss_dialog_index
    global zombie, skeleton1, skeleton2, antiwizard
    
    level = 0  # Текущий уровень
    player = Player()  # Создание игрока
    fireballs = pygame.sprite.Group()  # Группа для снарядов
    enemies = pygame.sprite.Group()  # Группа для врагов
    dialog_index = 0  # Индекс текущего диалога
    boss_dialog_index = 0  # Индекс диалога босса

    # Создание врагов
    zombie = Enemy(1000, HEIGHT - 50, zombie_img, hp=1)
    skeleton1 = Enemy(900, HEIGHT - 50, skeleton_img, hp=2)
    skeleton2 = Enemy(1050, HEIGHT - 50, skeleton_img, hp=2)
    antiwizard = Enemy(1000, HEIGHT - 50, antiwizard_img, hp=4)
    antiwizard.is_boss = True  # Последний враг - босс

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
    "Тебе не одолеть меня - тебе конец"
]

# Основной игровой цикл
while True:
    # Отрисовка фона текущего уровня
    screen.blit(backgrounds[level], (0, 0))
    keys = pygame.key.get_pressed()  # Получение состояния клавиш
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            # Обработка нажатия ENTER на экране окончания игры
            if level == 8 and event.key == pygame.K_RETURN:
                reset_game()
                continue
                
            # Начало игры (уровень 0 - меню)
            if level == 0 and event.key == pygame.K_RETURN:
                level = 1
                player.spawn(100, HEIGHT - 50)
            
            # Обработка диалогов на первом уровне (обучение)
            if level == 1 and event.key == pygame.K_RETURN:
                if dialog_index < len(dialogs_lvl1) - 1:
                    dialog_index += 1
                    
                    # Постепенное открытие возможностей игроку
                    if dialog_index == 1:
                        player.can_fire = True
                    elif dialog_index == 2:
                        player.can_shield = True
                    elif dialog_index == 3:
                        player.can_move = True
                
                # Проверка выполнения действий во время обучения
                if dialog_index == 1 and event.key == pygame.K_SPACE:
                    player.fire()
                elif dialog_index == 2 and event.key == pygame.K_f:
                    player.activate_shield()
            
            # Диалоги с боссом
            if level == 6 and event.key == pygame.K_RETURN and boss_dialog_index < len(boss_dialogs):
                boss_dialog_index += 1
                
                if boss_dialog_index == len(boss_dialogs):
                    # После диалогов активируем босса и даем игроку управление
                    antiwizard.boss_phase = 1
                    player.can_move = True
                    player.can_fire = True
                    player.can_shield = True
            
            # Обработка действий игрока с учетом текущего состояния игры
            if event.key == pygame.K_w and (level != 1 or dialog_index == 3) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.jump_action()
            elif event.key == pygame.K_SPACE and (level != 1 or dialog_index >= 1) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.fire()
            elif event.key == pygame.K_f and (level != 1 or dialog_index >= 2) and (level != 6 or boss_dialog_index == len(boss_dialogs)):
                player.activate_shield()

    # Обновление состояния игрока и объектов
    if player.rect:
        player.move(keys)
        player.apply_gravity()
        player.update()
        fireballs.update()
        
        # Обновление врагов
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
                    level = 8  # Переход на экран смерти
                    projectile.kill()
                    continue
            
            # Проверка столкновения с врагами
            for enemy in enemies:
                if projectile.rect.colliderect(enemy.rect) and enemy.alive and not (enemy.is_boss and isinstance(projectile, Lightning)):
                    enemy.take_damage()
                    projectile.kill()

        # Логика перехода между уровнями
        if level == 1:
            # Обучение - показ диалогов
            if dialog_index < len(dialogs_lvl1):
                screen.blit(frog_img, (WIDTH//2, HEIGHT - 180))
                draw_dialog(dialogs_lvl1[dialog_index], (WIDTH//2, HEIGHT - 180))
            
            # Переход на следующий уровень после обучения
            if dialog_index == len(dialogs_lvl1) - 1 and player.rect.right >= WIDTH:
                level = 2
                player.rect.midbottom = (50, HEIGHT - 50)

        elif level == 2:
            # Переход на уровень с зомби
            if player.rect.right >= WIDTH:
                level = 3
                player.rect.midbottom = (50, HEIGHT - 50)
                enemies.add(zombie)

        elif level == 3:
            # Переход на уровень со скелетами после убийства зомби
            if not zombie.alive and not any(e.alive for e in enemies):
                if player.rect.right >= WIDTH:
                    level = 4
                    player.rect.midbottom = (50, HEIGHT - 50)
                    enemies.empty()
                    enemies.add(skeleton1, skeleton2)

        elif level == 4:
            # Переход на уровень с предупреждением о боссе
            if all(not s.alive for s in [skeleton1, skeleton2]) and not any(e.alive for e in enemies):
                if player.rect.right >= WIDTH:
                    level = 5
                    player.rect.midbottom = (50, HEIGHT - 50)

        elif level == 5:
            # Предупреждение о боссе
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
            # Диалог с боссом
            if boss_dialog_index < len(boss_dialogs):
                draw_dialog(boss_dialogs[boss_dialog_index], (WIDTH//2, HEIGHT - 180))
            
            # Переход на следующий уровень после победы над боссом
            if not antiwizard.alive:
                level = 7

        elif level == 7:
            # Завершение игры и возврат в меню
            if player.rect.right >= WIDTH:
                level = 0
                reset_game()

        # Проверка столкновения игрока с врагами
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect) and enemy.alive:
                if not player.shield_active and player.alive:
                    player.alive = False
                    level = 8  # Экран смерти

    # Отрисовка всех объектов
    if player.rect:
        # Отрисовка врагов
        for enemy in enemies:
            if enemy.alive or (enemy.death_time and time.time() - enemy.death_time <= 3):
                screen.blit(enemy.image, enemy.rect)
                if enemy.shield_active:
                    shield_rect = shield_img.get_rect(center=(enemy.rect.centerx + 20, enemy.rect.centery))
                    screen.blit(shield_img, shield_rect)
        
        # Отрисовка игрока и снарядов
        player.draw()
        fireballs.draw(screen)
        
        # Отрисовка индикатора щита
        player.draw_shield_cooldown()

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)  # Ограничение до 60 FPS