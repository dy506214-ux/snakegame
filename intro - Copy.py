import pygame, sys, math, random, time
from pygame import gfxdraw

pygame.init()

WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Pro Intro")

# Colors
COLORS = {
    'bg_primary': (3, 3, 10),
    'bg_gradient': (15, 25, 50),
    'snake_skin': (35, 180, 100),
    'snake_head': (55, 220, 130),
    'snake_glow': (0, 200, 80),
    'snake_eye': (255, 255, 255),
    'snake_tongue': (220, 50, 50),
    'star': (255, 255, 200),
    'text_glow': (0, 255, 140),
    'text_glow2': (100, 255, 200)
}

SNAKE_SEGMENTS = 35
SNAKE_LENGTH = 450
SNAKE_THICKNESS = 35

# **SNAKE STATIC POSITION - NO MOVEMENT**
SNAKE_STATIC_PROGRESS = 3.8  # Perfect center position

show_start_screen = True  # **INSTANT SHOW BUTTONS**

def draw_realistic_anaconda(surface):
    """STATIC Anaconda - NO movement, perfect center position"""
    # **FIXED POSITION - Snake in center**
    x_offset = int(-SNAKE_LENGTH + (SNAKE_STATIC_PROGRESS * (WIDTH + SNAKE_LENGTH * 1.5)))
    
    # HEAD (center position)
    head_segment = SNAKE_SEGMENTS - 1
    head_progress = head_segment / SNAKE_SEGMENTS
    head_x = x_offset + (head_progress * SNAKE_LENGTH)
    head_y = HEIGHT * 0.3  # Static Y position
    
    head_center = (int(head_x), int(head_y))
    head_radius = SNAKE_THICKNESS + 8
    
    # HEAD GLOW
    for glow_i in range(5):
        glow_r = max(2, head_radius + 12 - glow_i * 3)
        pygame.draw.circle(surface, COLORS['snake_glow'], head_center, glow_r)
    
    # HEAD
    pygame.draw.circle(surface, COLORS['snake_head'], head_center, head_radius)
    gfxdraw.filled_circle(surface, *head_center, head_radius, (75, 240, 150))
    
    # EYES
    eye1_x = head_center[0] - 12
    eye1_y = head_center[1] - 8
    eye2_x = head_center[0] + 8
    eye2_y = head_center[1] - 8
    
    pygame.draw.circle(surface, COLORS['snake_eye'], (int(eye1_x), int(eye1_y)), 7)
    pygame.draw.circle(surface, COLORS['snake_eye'], (int(eye2_x), int(eye2_y)), 7)
    pygame.draw.circle(surface, (20, 20, 20), (int(eye1_x-2), int(eye1_y-2)), 3)
    pygame.draw.circle(surface, (20, 20, 20), (int(eye2_x-2), int(eye2_y-2)), 3)
    
    # TONGUE (animated but static position)
    tongue_progress = math.sin(time.time() * 3) * 0.5 + 0.5
    tongue_length = 45 + tongue_progress * 30
    tongue_x = head_center[0] - 28
    tongue_y = head_center[1]
    
    pygame.draw.circle(surface, COLORS['snake_tongue'], (int(tongue_x), int(tongue_y)), 6)
    for i in range(10):
        t_radius = max(2, 5 - i)
        t_x = tongue_x - (i * tongue_length / 10)
        t_y = tongue_y + math.sin((i + time.time() * 6) * 0.7) * 4
        pygame.draw.circle(surface, COLORS['snake_tongue'], (int(t_x), int(t_y)), t_radius)
    
    tip1_x = tongue_x - tongue_length + 4
    tip2_x = tongue_x - tongue_length - 4
    pygame.draw.circle(surface, (255, 40, 40), (int(tip1_x), int(tongue_y-3)), 3)
    pygame.draw.circle(surface, (255, 40, 40), (int(tip2_x), int(tongue_y+3)), 3)
    
    # BODY (static positions)
    for i in range(SNAKE_SEGMENTS - 4):
        segment_progress = i / SNAKE_SEGMENTS
        segment_x = x_offset + (segment_progress * SNAKE_LENGTH)
        y_pos = HEIGHT * 0.3  # Static Y
        radius = max(10, SNAKE_THICKNESS - int(segment_progress * 10))
        
        center = (int(segment_x), int(y_pos))
        
        for glow_i in range(3):
            glow_r = max(2, radius + 10 - glow_i * 4)
            pygame.draw.circle(surface, COLORS['snake_glow'], center, glow_r)
        
        pygame.draw.circle(surface, COLORS['snake_skin'], center, radius)
        gfxdraw.filled_circle(surface, *center, radius, (25, 160, 80))

def draw_star(surface, color, center):
    pygame.draw.circle(surface, color, center, 2)

def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLORS['bg_primary'][0] + (COLORS['bg_gradient'][0] - COLORS['bg_primary'][0]) * ratio)
        g = int(COLORS['bg_primary'][1] + (COLORS['bg_gradient'][1] - COLORS['bg_primary'][1]) * ratio)
        b = int(COLORS['bg_primary'][2] + (COLORS['bg_gradient'][2] - COLORS['bg_primary'][2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_start_game_button(surface):
    """PROFESSIONAL START BUTTON"""
    font_title = pygame.font.Font(None, 180)
    font_press = pygame.font.Font(None, 70)
    
    pulse = (math.sin(time.time() * 6) + 1) / 2
    
    # START GAME TITLE
    title_text = font_title.render("START GAME", True, COLORS['text_glow'])
    
    for glow_offset in [8, 5, 3]:
        glow_surf = pygame.Surface((title_text.get_width() + glow_offset*2, title_text.get_height() + glow_offset*2))
        glow_surf.set_colorkey((0,0,0))
        glow_surf.fill((0, 255, 140))
        glow_surf.set_alpha(int(120 * pulse))
        glow_surf.blit(title_text, (glow_offset, glow_offset))
        screen.blit(glow_surf, (WIDTH//2 - title_text.get_width()//2 - glow_offset, HEIGHT//2 - 50))
    
    title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(title_text, title_rect)
    
    # BUTTON
    button_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 + 60, 500, 80)
    pygame.draw.rect(screen, (0, 50, 25), button_rect)
    pygame.draw.rect(screen, COLORS['text_glow'], button_rect, 5)
    
    press_text = font_press.render("PRESS ANY KEY", True, COLORS['text_glow2'])
    press_rect = press_text.get_rect(center=button_rect.center)
    press_text.set_alpha(int(255 * pulse))
    screen.blit(press_text, press_rect)

def run_intro():
    clock = pygame.time.Clock()
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0, 1)) for _ in range(80)]
    
    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                return  # **GAME START**
        
        draw_gradient_bg(screen)
        
        # Animated stars
        for i, (x, y, twinkle) in enumerate(stars):
            twinkle += 0.04
            alpha = int(220 * (0.7 + 0.3 * math.sin(twinkle)))
            stars[i] = (x, y, twinkle)
            draw_star(screen, (*COLORS['star'], alpha), (int(x), int(y)))
        
        # **STATIC SNAKE - NO MOVEMENT**
        draw_realistic_anaconda(screen)
        
        # **INSTANT BUTTONS - NO DELAY**
        draw_start_game_button(screen)
        
        pygame.display.flip()

if __name__ == "__main__":
    try:
        run_intro()
    finally:
        pygame.quit()
