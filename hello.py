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

# Load assets
start_background = pygame.image.load("background1.png").convert()
start_background = pygame.transform.scale(start_background, (WIDTH, HEIGHT))

gameplay_background = pygame.image.load("background.png").convert()
gameplay_background = pygame.transform.scale(gameplay_background, (WIDTH, HEIGHT))

gameover_background = pygame.image.load("background2.png").convert()
gameover_background = pygame.transform.scale(gameover_background, (WIDTH, HEIGHT))

hero_img = pygame.image.load("hero.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
water_img = pygame.image.load("water.png").convert_alpha()
bullet_img = pygame.image.load("bullet.png").convert_alpha()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(hero_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5

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
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.speed = random.randint(1, 3)
        self.health = 3

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

    def shoot(self):
        return Bullet(self.rect.right, self.rect.centery)

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

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
waters = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Game variables
clock = pygame.time.Clock()
score = 0
high_score = 0

# Game loop
running = True
game_over = True
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
        enemy_spawn_timer = 0
        enemy_spawn_delay = 120  # 2 seconds at 60 FPS

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                water = player.shoot()
                all_sprites.add(water)
                waters.add(water)

    # Update
    all_sprites.update()

    # Determine number of enemies and firing rate based on score
    if score < 100:
        max_enemies = 3
        fire_chance = 30  # 1 in 30 chance to fire each frame
    elif score < 200:
        max_enemies = 6
        fire_chance = 20  # 1 in 20 chance to fire each frame
    else:
        max_enemies = 9
        fire_chance = 10  # 1 in 10 chance to fire each frame

    # Spawn enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_delay and len(enemies) < max_enemies:
        enemy_spawn_timer = 0
        new_enemy = Enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    # Enemy shooting
    for enemy in enemies:
        if random.randint(1, fire_chance) == 1:
            bullet = enemy.shoot()
            all_sprites.add(bullet)
            bullets.add(bullet)

    # Check for collisions
    for water in waters:
        hit_enemies = pygame.sprite.spritecollide(water, enemies, False)
        for enemy in hit_enemies:
            water.kill()
            enemy.health -= 1
            if enemy.health <= 0:
                enemy.kill()
                score += 10

    # Check if player is hit
    if pygame.sprite.spritecollide(player, bullets, True):
        if score > high_score:
            high_score = score
        show_game_over_screen(score, high_score)
        game_over = True

    # Draw
    screen.blit(gameplay_background, (0, 0))
    all_sprites.draw(screen)

    # Draw score
    draw_text(f"Water: {score}", 22, BLACK, 60, 10)
    draw_text(f"High Score: {high_score}", 22, BLACK, WIDTH - 100, 10)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()