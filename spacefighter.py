import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Difficulty settings
DIFFICULTY = {
    'easy': {
        'enemy_spawn_rate': 0.001,
        'special_enemy_chance': 0.05,
        'enemy_speed_range': (1, 3),
        'enemy_count': 4,
        'life_powerup_chance': 0.001  # 0.1% chance per frame
    },
    'normal': {
        'enemy_spawn_rate': 0.02,
        'special_enemy_chance': 0.1,
        'enemy_speed_range': (1, 4),
        'enemy_count': 8,
        'life_powerup_chance': 0.0007  # 0.07% chance per frame
    },
    'hard': {
        'enemy_spawn_rate': 0.03,
        'special_enemy_chance': 0.15,
        'enemy_speed_range': (2, 5),
        'enemy_count': 10,
        'life_powerup_chance': 0.0005  # 0.05% chance per frame
    }
}

# Current difficulty
current_difficulty = 'normal'

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load assets
def load_image(name, size=None, colorkey=None):
    try:
        image_path = os.path.join('assets', name)
        image = pygame.image.load(image_path)
        image = image.convert_alpha()
        
        # Resize the image if size is specified
        if size:
            image = pygame.transform.scale(image, size)
        else:
            # Auto-resize based on screen dimensions to make it responsive
            # Calculate a reasonable size based on screen dimensions
            width = int(SCREEN_WIDTH * 0.6)  # 6% of screen width
            height = int(SCREEN_HEIGHT * 0.8)  # 8% of screen height
            image = pygame.transform.scale(image, (width, height))
            
        return image
    except pygame.error:
        print(f"Cannot load image: {name}")
        # Create a placeholder colored rectangle
        width = int(SCREEN_WIDTH * 0.06)  # 6% of screen width
        height = int(SCREEN_HEIGHT * 0.08)  # 8% of screen height
        surf = pygame.Surface((width, height))
        surf.fill(colorkey if colorkey else (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        return surf

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Calculate responsive sizes based on screen dimensions
        player_width = int(SCREEN_WIDTH * 0.06)  # 6% of screen width
        player_height = int(SCREEN_HEIGHT * 0.08)  # 8% of screen height
        
        try:
            self.image = load_image('player_ship.png', (player_width, player_height))
        except:
            # Create a placeholder triangle for the player ship
            self.image = pygame.Surface((player_width, player_height), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, GREEN, [(0, player_height), 
                                                   (player_width//2, 0), 
                                                   (player_width, player_height)])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.forward_count = 0
        self.max_forward = 2
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.score = 0
        
    def update(self):
        # Movement
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Keep player on the screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < SCREEN_HEIGHT // 2:
            self.rect.top = SCREEN_HEIGHT // 2
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            # Play sound effect here if available

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type='regular'):
        super().__init__()
        # Calculate responsive sizes based on screen dimensions
        enemy_width = int(SCREEN_WIDTH * 0.05)  # 5% of screen width
        enemy_height = int(SCREEN_HEIGHT * 0.07)  # 7% of screen height
        
        self.enemy_type = enemy_type
        self.points = 5 if enemy_type == 'regular' else 10
        
        try:
            if enemy_type == 'regular':
                self.image = load_image('enemy_ship.png', (enemy_width, enemy_height))
            else:  # special enemy
                self.image = load_image('special_enemy_ship.png', (enemy_width, enemy_height))
        except:
            # Create a placeholder for enemy
            self.image = pygame.Surface((enemy_width, enemy_height), pygame.SRCALPHA)
            if enemy_type == 'regular':
                pygame.draw.polygon(self.image, RED, [(0, 0), 
                                                     (enemy_width, 0), 
                                                     (enemy_width//2, enemy_height)])
            else:  # special enemy
                pygame.draw.polygon(self.image, PURPLE, [(0, enemy_height), 
                                                        (enemy_width//2, 0), 
                                                        (enemy_width, enemy_height)])
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # Get speed range based on current difficulty
        min_speed, max_speed = DIFFICULTY[current_difficulty]['enemy_speed_range']
        self.speedy = random.randrange(min_speed, max_speed + 1)
        
        # Special enemies move faster and can move diagonally
        if enemy_type == 'special':
            self.speedy += 1
            self.speedx = random.randrange(-3, 4)
        else:
            self.speedx = random.randrange(-2, 3)
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # If enemy goes off screen, respawn it
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 25:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            
            # Get speed range based on current difficulty
            min_speed, max_speed = DIFFICULTY[current_difficulty]['enemy_speed_range']
            self.speedy = random.randrange(min_speed, max_speed + 1)
            
            # Special enemies move faster and can move diagonally
            if self.enemy_type == 'special':
                self.speedy += 1
                self.speedx = random.randrange(-3, 4)
            else:
                self.speedx = random.randrange(-2, 3)

# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type='life'):
        super().__init__()
        # Calculate responsive sizes based on screen dimensions
        powerup_size = int(SCREEN_WIDTH * 0.04)  # 4% of screen width
        
        self.type = power_type
        
        try:
            if power_type == 'life':
                self.image = load_image('life.png', (powerup_size, powerup_size))
        except:
            # Create a placeholder for power-up
            self.image = pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA)
            if power_type == 'life':
                # Heart shape for life power-up
                pygame.draw.circle(self.image, RED, (powerup_size//4, powerup_size//4), powerup_size//4)
                pygame.draw.circle(self.image, RED, (powerup_size*3//4, powerup_size//4), powerup_size//4)
                pygame.draw.polygon(self.image, RED, [(0, powerup_size//4), 
                                                     (powerup_size//2, powerup_size), 
                                                     (powerup_size, powerup_size//4)])
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = 3
        
    def update(self):
        self.rect.y += self.speedy
        # Remove if it goes off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Calculate responsive sizes based on screen dimensions
        bullet_width = max(int(SCREEN_WIDTH * 0.006), 3)  # 0.6% of screen width, minimum 3px
        bullet_height = max(int(SCREEN_HEIGHT * 0.015), 8)  # 1.5% of screen height, minimum 8px
        
        self.image = pygame.Surface((bullet_width, bullet_height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0:
            self.kill()

# Explosion animation
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        # Calculate responsive size based on screen dimensions
        self.size = int(SCREEN_WIDTH * 0.06)  # 6% of screen width
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.frame_rate = 50
        self.last_update = pygame.time.get_ticks()
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 8:  # End of animation
                self.kill()
            else:
                size = self.size - self.frame * 5
                if size > 0:
                    self.image = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.circle(self.image, (255, 100, 0), (size // 2, size // 2), size // 2)
                    self.rect = self.image.get_rect()
                    self.rect.center = self.rect.center

# Background stars
class Star:
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.size = random.randrange(1, 3)
        self.speed = random.randrange(1, 3)
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randrange(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        # Ensure star is within screen bounds after resize
        if 0 <= self.x < SCREEN_WIDTH and 0 <= self.y < SCREEN_HEIGHT:
            pygame.draw.circle(surface, WHITE, (self.x, self.y), self.size)

# Game functions
def draw_text(surf, text, size, x, y, color=WHITE):
    # Make font size responsive to screen dimensions
    font_size = int(size * (SCREEN_WIDTH / 800))  # Scale based on screen width
    font = pygame.font.Font(pygame.font.match_font('arial'), font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_lives(surf, x, y, lives, img=None):
    # Calculate responsive size based on screen dimensions
    life_icon_size = int(SCREEN_WIDTH * 0.025)  # 2.5% of screen width
    spacing = int(SCREEN_WIDTH * 0.035)  # 3.5% of screen width for spacing
    
    if img:
        # Resize the life icon image to be responsive
        img = pygame.transform.scale(img, (life_icon_size, life_icon_size))
        for i in range(lives):
            img_rect = img.get_rect()
            img_rect.x = x + spacing * i
            img_rect.y = y
            surf.blit(img, img_rect)
    else:
        for i in range(lives):
            pygame.draw.rect(surf, GREEN, (x + spacing * i, y, life_icon_size, life_icon_size))

def show_difficulty_screen():
    screen.fill(BLACK)
    draw_text(screen, "SPACE SHOOTER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Select Difficulty:", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    draw_text(screen, "E - Easy", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "N - Normal", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
    draw_text(screen, "H - Hard", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return 'easy'
                if event.key == pygame.K_n:
                    return 'normal'
                if event.key == pygame.K_h:
                    return 'hard'

def show_game_over_screen(score=0):
    screen.fill(BLACK)
    draw_text(screen, "SPACE SHOOTER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, f"Score: {score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Press R to restart or Q to quit", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3/4)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Game loop
game_over = True
running = True
show_difficulty = True
player_score = 0  # Keep track of score between game sessions

# Handle window resizing
def handle_resize(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    # Reposition player after resize
    if 'player' in globals() and player:
        player.rect.centerx = SCREEN_WIDTH // 2
        player.rect.bottom = SCREEN_HEIGHT - 10

# Function to spawn a new enemy with a chance of special enemy
def spawn_enemy():
    # Check if we should spawn a special enemy based on difficulty
    if random.random() < DIFFICULTY[current_difficulty]['special_enemy_chance']:
        enemy = Enemy('special')
    else:
        enemy = Enemy('regular')
    all_sprites.add(enemy)
    enemies.add(enemy)
    return enemy

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

while running:
    if show_difficulty:
        current_difficulty = show_difficulty_screen()
        show_difficulty = False
        game_over = True
    
    if game_over:
        show_game_over_screen(player_score)
        game_over = False
        
        # Reset game
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        
        player = Player()
        all_sprites.add(player)
        player_score = 0  # Reset score for new game
        
        # Spawn initial enemies based on difficulty
        enemy_count = DIFFICULTY[current_difficulty]['enemy_count']
        for i in range(enemy_count):
            spawn_enemy()
        
        stars = [Star() for _ in range(100)]
    
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            handle_resize(event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speedx = -5
            elif event.key == pygame.K_RIGHT:
                player.speedx = 5
            elif event.key == pygame.K_UP:
                if player.forward_count < player.max_forward:
                    player.speedy = -5
                    player.forward_count += 1
            elif event.key == pygame.K_DOWN:
                if player.forward_count > 0:
                    player.speedy = 5
            elif event.key == pygame.K_SPACE:
                player.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.speedx < 0:
                player.speedx = 0
            elif event.key == pygame.K_RIGHT and player.speedx > 0:
                player.speedx = 0
            elif event.key == pygame.K_UP and player.speedy < 0:
                player.speedy = 0
            elif event.key == pygame.K_DOWN and player.speedy > 0:
                player.speedy = 0
                player.forward_count -= 1
    
    # Update
    all_sprites.update()
    for star in stars:
        star.update()
    
    # Randomly spawn new enemies based on difficulty
    if random.random() < DIFFICULTY[current_difficulty]['enemy_spawn_rate']:
        spawn_enemy()
    
    # Randomly spawn life power-up based on difficulty
    if random.random() < DIFFICULTY[current_difficulty]['life_powerup_chance']:
        powerup = PowerUp('life')
        all_sprites.add(powerup)
        powerups.add(powerup)
    
    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        player_score += hit.points  # Add points based on enemy type
        player.score = player_score  # Update player's score
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        spawn_enemy()
    
    # Check for player-powerup collisions
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'life':
            player.lives += 1
            # Play power-up sound here if available
    
    # Check for player-enemy collisions
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.lives -= 1
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        spawn_enemy()
        
        if player.lives <= 0:
            player_score = player.score  # Save score before game over
            game_over = True
            show_difficulty = True  # Show difficulty selection on next restart
    
    # Draw / render
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        star.draw(screen)
    
    # Draw all sprites
    all_sprites.draw(screen)
    
    # Draw UI
    draw_text(screen, str(player.score), 18, SCREEN_WIDTH // 2, 10)
    draw_lives(screen, SCREEN_WIDTH - 100, 10, player.lives)
    
    # Display current difficulty
    difficulty_colors = {'easy': GREEN, 'normal': YELLOW, 'hard': RED}
    draw_text(screen, f"Difficulty: {current_difficulty.capitalize()}", 
              18, 100, 10, difficulty_colors[current_difficulty])
    
    # Flip the display
    pygame.display.flip()

pygame.quit()