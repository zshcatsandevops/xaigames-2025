import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Ultra! Mario Forever 1.x [Team Flames [C]2025]')
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (165, 42, 42)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)  # For warped theme

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)
hud_font = pygame.font.SysFont('courier', 20)  # Pixel-like for beta feel

# Game states
MENU = 0
OVERWORLD = 1
LEVEL = 2
state = MENU

# Menu sub-views (toggles for Warped Worlds style)
show_jukebox = False
show_options = False
show_extras = False
ai_mode = False  # Toggle for AI Mode (dummy)
audio_stereo = True  # Toggle for stereo/mono (dummy)

# Overworld data
player_pos = [400, 300]  # Starting position in overworld
levels = [[200, 200], [600, 200], [400, 400]]  # Positions of level entrances (black forts)

# Level data
mario_x, mario_y = 100, 450
velocity_y = 0
gravity = 0.8
jump_height = -15
ground_y = 500
is_jumping = False

# Enemy data (Goomba)
enemy_x, enemy_y = 600, 470
enemy_speed = -3
enemy_alive = True
enemy_ko_timer = 0  # Timer for KO display
enemy_state = 'alive'  # 'alive', 'ko'

# HUD data (static for simplicity, beta SM64 style)
lives = 3
coins = 0
stars = 0
health = 8  # Full health (8 segments)

# Jukebox song list from Warped Worlds
jukebox_songs = [
    "M30 - Castle Lobby (Binary Demo)",
    "M25 - Slider Remix",
    "M23 - Piranha Plant Lullaby",
    "01 - Daffodil Meadow",
    "02 - The Internal Fortress",
    "03 - Castle Lobby (Decomp Demo)",
    "04 - Dancing In The Lights",
    "05 - Castle Grounds (Decomp Demo)",
    "06 - Warped Worlds Main Theme",
    "07 - Daffodil Meadow",
    "09 - Brawl With The Deadly Prince",
    "10 - World Behind The Waterfall",
    "12 - Inside The Castle Variation"
]

class Button:
    def __init__(self, text, pos, action):
        self.text = small_font.render(text, True, WHITE)
        self.rect = self.text.get_rect(topleft=pos)
        self.action = action

    def draw(self, screen):
        screen.blit(self.text, self.rect)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.action()
            return True
        return False

# Menu buttons (Warped Worlds inspired: Start, Jukebox, Options, Extras)
def toggle_jukebox():
    global show_jukebox
    show_jukebox = not show_jukebox

def toggle_options():
    global show_options
    show_options = not show_options

def toggle_extras():
    global show_extras
    show_extras = not show_extras

def start_game():
    global state
    state = OVERWORLD

def toggle_ai():
    global ai_mode
    ai_mode = not ai_mode

def toggle_audio():
    global audio_stereo
    audio_stereo = not audio_stereo

menu_buttons = [
    Button("Start Game", (300, 300), start_game),
    Button("Jukebox", (300, 350), toggle_jukebox),
    Button("Options", (300, 400), toggle_options),
    Button("Extras", (300, 450), toggle_extras)
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if state == MENU:
                if event.key == K_SPACE or event.key == K_s:
                    state = OVERWORLD
                elif event.key == K_j:
                    toggle_jukebox()
                elif event.key == K_o:
                    toggle_options()
                elif event.key == K_e:
                    toggle_extras()
                elif show_options:
                    if event.key == K_a:  # A for AI
                        toggle_ai()
                    elif event.key == K_m:  # M for mono/stereo
                        toggle_audio()
            if state == LEVEL and event.key == K_SPACE and not is_jumping:
                velocity_y = jump_height
                is_jumping = True
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if state == MENU:
                for button in menu_buttons:
                    button.check_click(mouse_pos)
                # Check toggles in sub-views if needed
            if state == OVERWORLD:
                for level_pos in levels:
                    if abs(mouse_pos[0] - level_pos[0]) < 30 and abs(mouse_pos[1] - level_pos[1]) < 30:
                        # Reset level positions
                        mario_x, mario_y = 100, 450
                        velocity_y = 0
                        is_jumping = False
                        enemy_x, enemy_y = 600, 470
                        enemy_speed = -3
                        enemy_alive = True
                        enemy_state = 'alive'
                        enemy_ko_timer = 0
                        state = LEVEL
                        break

    # Handle movement
    keys = pygame.key.get_pressed()
    if state == OVERWORLD:
        if keys[K_LEFT]:
            player_pos[0] = max(0, player_pos[0] - 5)
        if keys[K_RIGHT]:
            player_pos[0] = min(800, player_pos[0] + 5)
        if keys[K_UP]:
            player_pos[1] = max(0, player_pos[1] - 5)
        if keys[K_DOWN]:
            player_pos[1] = min(600, player_pos[1] + 5)
    elif state == LEVEL:
        if keys[K_LEFT]:
            mario_x = max(0, mario_x - 5)
        if keys[K_RIGHT]:
            mario_x = min(760, mario_x + 5)

    # Update physics in level
    if state == LEVEL:
        velocity_y += gravity
        mario_y += velocity_y
        if mario_y >= ground_y:
            mario_y = ground_y
            velocity_y = 0
            is_jumping = False

        if enemy_alive and enemy_state == 'alive':
            # Enemy movement
            enemy_x += enemy_speed
            if enemy_x < 0:
                enemy_x = 800

            # Collision check
            if abs(mario_x - enemy_x) < 20 and abs(mario_y - enemy_y) < 40:
                if velocity_y > 0 and mario_y < enemy_y:  # Stomping from above while falling
                    velocity_y = -10  # Bounce up
                    enemy_state = 'ko'
                    enemy_ko_timer = 60  # Display KO for ~1 second (60 frames)
                    enemy_speed = 0  # Stop moving
                    enemy_y += 20  # Flatten visually
                else:
                    state = OVERWORLD  # Side touch: die

        # KO timer countdown
        if enemy_ko_timer > 0:
            enemy_ko_timer -= 1
            if enemy_ko_timer == 0:
                enemy_alive = False  # Remove enemy after KO display

    # Draw everything
    if state == MENU:
        screen.fill(BLACK)  # Dark background for warped theme
        # Warped title with purple accent
        title_text = font.render('Ultra! Mario Forever 1.x [Team Flames [C]2025]', True, PURPLE)
        screen.blit(title_text, (100, 150))
        instructions = small_font.render('Click options or use keys: S-Start, J-Jukebox, O-Options, E-Extras', True, WHITE)
        screen.blit(instructions, (100, 200))

        # Draw menu buttons
        for button in menu_buttons:
            button.draw(screen)

        # Overlay sub-views if toggled
        if show_jukebox:
            pygame.draw.rect(screen, PURPLE, (200, 100, 400, 400), 2)  # Border
            jukebox_title = small_font.render('Jukebox - Press J to close', True, WHITE)
            screen.blit(jukebox_title, (220, 120))
            for i, song in enumerate(jukebox_songs):
                song_text = small_font.render(song, True, WHITE)
                screen.blit(song_text, (220, 150 + i * 20))

        if show_options:
            pygame.draw.rect(screen, PURPLE, (200, 100, 400, 200), 2)
            options_title = small_font.render('Options - Press O to close', True, WHITE)
            screen.blit(options_title, (220, 120))
            ai_text = small_font.render(f'AI Mode: {"On" if ai_mode else "Off"} (Press A to toggle)', True, WHITE)
            screen.blit(ai_text, (220, 150))
            audio_text = small_font.render(f'Audio: {"Stereo" if audio_stereo else "Mono"} (Press M to toggle)', True, WHITE)
            screen.blit(audio_text, (220, 180))

        if show_extras:
            pygame.draw.rect(screen, PURPLE, (200, 100, 400, 200), 2)
            extras_title = small_font.render('Extras - Press E to close', True, WHITE)
            screen.blit(extras_title, (220, 120))
            extras_text = small_font.render('Access Legacy Fortress (Bonus Content)', True, WHITE)
            screen.blit(extras_text, (220, 150))
            # Could add more, but keeping simple

    elif state == OVERWORLD:
        screen.fill(SKY_BLUE)
        # Draw paths (simple lines)
        pygame.draw.line(screen, BROWN, (100, 300), (700, 300), 20)
        pygame.draw.line(screen, BROWN, (400, 100), (400, 500), 20)
        # Draw level entrances (black forts)
        for pos in levels:
            pygame.draw.rect(screen, BLACK, (pos[0] - 30, pos[1] - 30, 60, 60))
            pygame.draw.polygon(screen, BLACK, [(pos[0] - 30, pos[1] - 30), (pos[0], pos[1] - 60), (pos[0] + 30, pos[1] - 30)])
        # Draw player (Mario as red circle with hat)
        pygame.draw.circle(screen, RED, player_pos, 20)
        pygame.draw.rect(screen, RED, (player_pos[0] - 10, player_pos[1] - 30, 20, 10))  # Hat
        overworld_text = small_font.render('Overworld - Move with arrows, click forts to enter levels', True, BLACK)
        screen.blit(overworld_text, (10, 10))
    elif state == LEVEL:
        screen.fill(SKY_BLUE)
        # Draw ground
        pygame.draw.rect(screen, GREEN, (0, ground_y, 800, 100))
        pygame.draw.rect(screen, BROWN, (0, ground_y + 20, 800, 80))
        # Draw simple clouds
        pygame.draw.circle(screen, WHITE, (100, 100), 30)
        pygame.draw.circle(screen, WHITE, (130, 100), 30)
        pygame.draw.circle(screen, WHITE, (70, 100), 30)
        # Draw Mario (blue overalls, red shirt/hat)
        pygame.draw.rect(screen, BLUE, (mario_x, mario_y + 20, 30, 30))  # Legs
        pygame.draw.rect(screen, RED, (mario_x + 5, mario_y, 20, 20))  # Body
        pygame.draw.rect(screen, RED, (mario_x, mario_y - 10, 30, 10))  # Hat
        # Draw enemy if alive
        if enemy_alive:
            if enemy_state == 'alive':
                pygame.draw.rect(screen, BROWN, (enemy_x, enemy_y, 30, 30))
                pygame.draw.circle(screen, BLACK, (enemy_x + 10, enemy_y + 10), 5)
                pygame.draw.circle(screen, BLACK, (enemy_x + 20, enemy_y + 10), 5)
            elif enemy_state == 'ko':
                # Flattened Goomba
                pygame.draw.rect(screen, BROWN, (enemy_x, enemy_y, 30, 10))  # Squished
                # KO text
                if enemy_ko_timer > 0:
                    ko_text = hud_font.render('KO', True, RED)
                    screen.blit(ko_text, (enemy_x + 5, enemy_y - 20))
        level_text = small_font.render('Level - Arrows to move, SPACE to jump', True, BLACK)
        screen.blit(level_text, (10, 10))

        # Draw beta SM64 HUD (top-left lives/coins/stars, top-right health pie)
        # Lives: Mario head icon (red circle) x lives (cartoony font)
        pygame.draw.circle(screen, RED, (30, 30), 10)  # Mario head icon
        lives_text = hud_font.render(f'x {lives}', True, WHITE)
        screen.blit(lives_text, (45, 25))
        
        # Coins: Yellow coin icon x coins
        pygame.draw.circle(screen, YELLOW, (30, 60), 10)
        pygame.draw.circle(screen, GOLD, (30, 60), 8)
        coins_text = hud_font.render(f'x {coins}', True, WHITE)
        screen.blit(coins_text, (45, 55))
        
        # Stars: Yellow star icon x stars
        pygame.draw.polygon(screen, YELLOW, [(30, 90), (25, 100), (35, 100)])  # Simple star
        pygame.draw.polygon(screen, YELLOW, [(30, 95), (20, 95), (25, 85), (35, 85), (40, 95)])
        stars_text = hud_font.render(f'x {stars}', True, WHITE)
        screen.blit(stars_text, (45, 85))
        
        # Health: Pie chart (8 segments, full = circle)
        center_x, center_y = 750, 50
        for i in range(health):
            start_angle = i * (360 / 8)
            end_angle = start_angle + (360 / 8)
            pygame.draw.arc(screen, BLUE, (center_x - 20, center_y - 20, 40, 40), 
                            start_angle * (3.14159 / 180), end_angle * (3.14159 / 180), 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
