import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Water Hero Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Title
icon = pygame.image.load('waterbottle.png')
pygame.display.set_icon(icon)

# Load assets
start_background = pygame.image.load("background1.png").convert()
start_background = pygame.transform.scale(start_background, (WIDTH, HEIGHT))

gameplay_background = pygame.image.load("background.png").convert()
gameplay_background = pygame.transform.scale(gameplay_background, (WIDTH, HEIGHT))

gameover_background = pygame.image.load("background2.png").convert()
gameover_background = pygame.transform.scale(gameover_background, (WIDTH, HEIGHT))

levelup_background = pygame.image.load("background4.png").convert()
levelup_background = pygame.transform.scale(levelup_background, (WIDTH, HEIGHT))

hero_img = pygame.image.load("hero.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
water_img = pygame.image.load("water.png").convert_alpha()
bullet_img = pygame.image.load("bullet.png").convert_alpha()

# Load sounds
pygame.mixer.music.load("background_music.wav")
bullet_sound = pygame.mixer.Sound("bullet_sound.wav")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(hero_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.lives = 3  # Hero has 3 lives

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        return Water(self.rect.centerx, self.rect.centery)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.speed = 1 + (level - 1) * 0.5  
        self.health = 3
        self.level = level  
        self.last_shot_time = 0  
        self.shot_delay = 500  
        self.bullets_fired = 0  
        self.max_bullets = min(self.level, 3)  
        self.stopped_firing = False  

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

    def shoot(self):
        if self.stopped_firing:
            return []  

        current_time = pygame.time.get_ticks()  
        bullets = []

        
        if current_time - self.last_shot_time >= self.shot_delay and self.bullets_fired < self.max_bullets:
            bullet = Bullet(self.rect.right, self.rect.centery)
            bullets.append(bullet)
            self.last_shot_time = pygame.time.get_ticks()  
            self.bullets_fired += 1  
            bullet_sound.play()

       
        if self.bullets_fired >= self.max_bullets:
            self.stopped_firing = True

        return bullets

# Water class
class Water(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(water_img, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img, (15, 15))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speed = 5

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

# Function to draw text
def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

# Function to show start screen
def show_start_screen():
    screen.blit(start_background, (0, 0))
    draw_text("Water Hero", 64, BLUE, WIDTH // 2, HEIGHT // 4)
    draw_text("Press SPACE to start", 22, WHITE, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Function to show game over screen
def show_game_over_screen(score, high_score):
    screen.blit(gameover_background, (0, 0))
    draw_text("GAME OVER", 64, WHITE, WIDTH // 2, HEIGHT // 4)
    draw_text(f"Score: {score}", 22, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text(f"High Score: {high_score}", 22, WHITE, WIDTH // 2, HEIGHT // 2 + 40)
    draw_text("Press SPACE to play again", 22, WHITE, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    waiting = False

#level up screen
def show_level_up_screen(level):
    screen.blit(levelup_background, (0, 0))
    draw_text(f"Level {level} Complete", 64, BLUE, WIDTH // 2, HEIGHT // 4)
    draw_text("Press ENTER to continue", 22, WHITE, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
waters = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Game variables
clock = pygame.time.Clock()
score = 0
high_score = 0
level = 1
enemy_spawn_delay = 120  
level_up = False  

# Game loop
running = True
game_over = True
pygame.mixer.music.play(-1)  

while running:
    if game_over:
        show_start_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        waters = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        score = 0
        level = 1
        enemy_spawn_delay = 120

    if level_up:
        show_level_up_screen(level - 1)  
        level_up = False
        enemy_spawn_delay = max(30, 120 - (level * 10))  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                water = player.shoot()
                all_sprites.add(water)
                waters.add(water)

    all_sprites.update()

    # Enemy spawning logic
    enemy_spawn_delay -= 1
    if enemy_spawn_delay <= 0:
        enemy = Enemy(level)
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_spawn_delay = max(30, 120 - (level * 10))  

    # Enemy shooting logic
    for enemy in enemies:
        bullets_from_enemy = enemy.shoot()
        for bullet in bullets_from_enemy:
            all_sprites.add(bullet)
            bullets.add(bullet)

    # Collision detection
    for enemy in pygame.sprite.groupcollide(enemies, waters, True, True):
        score += 10

    for bullet in pygame.sprite.spritecollide(player, bullets, True):
        player.lives -= 1
        if player.lives <= 0:
            if score > high_score:
                high_score = score
            show_game_over_screen(score, high_score)
            game_over = True

    # Check for level up
    if score >= level * 100: 
        level += 1
        level_up = True

    # Draw
    screen.blit(gameplay_background, (0, 0))
    all_sprites.draw(screen)
    draw_text(f"Score: {score}", 18, WHITE, WIDTH // 2, 10)
    draw_text(f"Level: {level}", 18, WHITE, WIDTH - 100, 10)
    draw_text(f"Lives: {player.lives}", 18, WHITE, 100, 10)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
