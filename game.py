import pygame
import random

# Initialize Pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init()

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
icon = pygame.image.load('assets/waterbottle.png')
pygame.display.set_icon(icon)

# Load assets
start_background = pygame.image.load("assets/background4.png").convert()
start_background = pygame.transform.scale(start_background, (WIDTH, HEIGHT))

gameplay_background = pygame.image.load("assets/background.png").convert()
gameplay_background = pygame.transform.scale(gameplay_background, (WIDTH, HEIGHT))

gameover_background = pygame.image.load("assets/background2.png").convert()
gameover_background = pygame.transform.scale(gameover_background, (WIDTH, HEIGHT))

levelup_background = pygame.image.load("assets/background4.png").convert()
levelup_background = pygame.transform.scale(levelup_background, (WIDTH, HEIGHT))

hero_img = pygame.image.load("assets/hero.png").convert_alpha()
enemy_img = pygame.image.load("assets/enemy.png").convert_alpha()
water_img = pygame.image.load("assets/water.png").convert_alpha()
bullet_img = pygame.image.load("assets/bullet.png").convert_alpha()

# Load sounds with error handling
try:
    pygame.mixer.music.load("assets/background_music.wav")
    bullet_sound = pygame.mixer.Sound("assets/bullet_sound.wav")
except pygame.error as e:
    print(f"Error loading sound: {e}")

# Set volume (optional)
pygame.mixer.music.set_volume(0.5)
bullet_sound.set_volume(0.5)

# Global variable for sound state
sound_on = True

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(hero_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.lives = 3

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
            if sound_on:
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

# Function to create a button
def create_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    small_text = pygame.font.Font(None, 30)
    text_surf = small_text.render(text, True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (width / 2)), (y + (height / 2)))
    screen.blit(text_surf, text_rect)

# Function to start the game
def start_game():
    global game_state
    game_state = "playing"

# Function to toggle sound
def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()

# Function to quit the game
def quit_game():
    global running
    running = False

# Function to resume the game after level up
def resume_game():
    global game_state, level
    level += 1  # Increment the level here
    game_state = "playing"

# Function to restart the game
def restart_game():
    global score, level, player, all_sprites, enemies, waters, bullets, enemy_spawn_delay
    score = 0
    level = 1
    player = Player()
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    waters = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    all_sprites.add(player)
    enemy_spawn_delay = 120
    start_game()

# Function to show start screen
def show_start_screen():
    screen.blit(start_background, (0, 0))
    create_button("START", 300, 200, 200, 50, BLUE, (0, 0, 200), start_game)
    create_button("SOUND: " + ("ON" if sound_on else "OFF"), 300, 300, 200, 50, BLUE, (0, 0, 200), toggle_sound)
    create_button("EXIT", 300, 400, 200, 50, BLUE, (0, 0, 200), quit_game)

# Function to show game over screen
def show_game_over_screen():
    screen.blit(gameover_background, (0, 0))
    draw_text("GAME OVER", 64, BLACK, WIDTH // 2, HEIGHT // 4)
    draw_text(f"Score: {score}", 22, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text(f"High Score: {high_score}", 22, WHITE, WIDTH // 2, HEIGHT // 2 + 40)
    
    create_button("RESTART", 250, 400, 150, 50, BLUE, (0, 0, 200), restart_game)
    create_button("QUIT", 450, 400, 150, 50, BLUE, (0, 0, 200), quit_game)

# Function to show level up screen
def show_level_up_screen():
    screen.blit(levelup_background, (0, 0))
    draw_text(f"Level {level} Complete", 64, WHITE, WIDTH // 2, HEIGHT // 4)
    draw_text(f"Next Level: {level + 1}", 48, WHITE, WIDTH // 2, HEIGHT // 2)
    
    create_button("RESUME", 250, 400, 150, 50, BLUE, (0, 0, 200), resume_game)
    create_button("QUIT", 450, 400, 150, 50, BLUE, (0, 0, 200), quit_game)

# Game variables
clock = pygame.time.Clock()
score = 0
high_score = 0
level = 1
enemy_spawn_delay = 120

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
waters = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game states
game_state = "start"

# Game loop
running = True
if sound_on:
    pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key == pygame.K_SPACE:
                water = player.shoot()
                all_sprites.add(water)
                waters.add(water)

    if game_state == "start":
        show_start_screen()
    elif game_state == "playing":
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
                game_state = "game_over"

        # Check for level up
        if score >= level * 100:
            game_state = "level_up"

        # Draw
        screen.blit(gameplay_background, (0, 0))
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", 18, WHITE, WIDTH // 2, 10)
        draw_text(f"Level: {level}", 18, WHITE, WIDTH - 100, 10)
        draw_text(f"Lives: {player.lives}", 18, WHITE, 100, 10)

    elif game_state == "game_over":
        show_game_over_screen()
    elif game_state == "level_up":
        show_level_up_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
