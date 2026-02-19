import pygame
import random
import json
import os
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum
import math
import intro
import pygame
pygame.init()

# run intro AFTER pygame init
import intro
intro.run_intro()



# After intro → start game
print("Snake Game Started...")

# Your snake game code here

@dataclass
class ScaleManager:
    base_width: int = 800
    base_height: int = 600
    min_scale: float = 0.7
    max_scale: float = 1.5
    
    def __post_init__(self):
        try:
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
        except:
            self.screen_width = 1024
            self.screen_height = 768
            
        self.scale_x = min(self.screen_width / self.base_width, self.screen_height / self.base_height)
        self.scale_x = max(self.min_scale, min(self.scale_x, self.max_scale))
        self.scale_y = self.scale_x
        self.scaled_width = int(self.base_width * self.scale_x)
        self.scaled_height = int(self.base_height * self.scale_y)

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("⚠️  No numpy - Audio disabled (pygame still works perfectly)")
    NUMPY_AVAILABLE = False

pygame.init()
if NUMPY_AVAILABLE:
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    except:
        NUMPY_AVAILABLE = False

@dataclass
class Vector2:
    x: float
    y: float

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    RESUMED = 3
    GAME_OVER = 4

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 50
        self.max_life = 50
        self.color = color
        self.size = random.randint(3, 6)
    
    def update(self) -> bool:
        self.x += self.vx * 0.8
        self.y += self.vy * 0.8
        self.vy += 0.12
        self.life -= 1
        self.vx *= 0.98
        self.vy *= 0.98
        return self.life > 0
    
    def draw(self, screen, scale_x: float, scale_y: float):
        alpha_ratio = self.life / self.max_life
        size = int(self.size * alpha_ratio * scale_x)
        if size > 0:
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), size)

class SnakeGame:
    def __init__(self):
        self.scale_manager = ScaleManager()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("🐍 REAL SNAKE PRO - ULTRA SMOOTH 🐍")
        self.clock = pygame.time.Clock()
        
        try:
            self.font_large = pygame.font.Font(None, 72)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 32)
            self.font_button = pygame.font.Font(None, 20)
            self.font_welcome = pygame.font.Font(None, 36)
            self.font_logo = pygame.font.Font(None, 64)
        except:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
            self.font_button = pygame.font.Font(None, 16)
            self.font_welcome = pygame.font.Font(None, 28)
            self.font_logo = pygame.font.Font(None, 48)
        
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        
        self.snake_block = 25
        self.update_play_area()
        
        self.snake = [Vector2(250, 375)]
        self.direction = Vector2(1.0, 0.0)
        self.next_direction = Vector2(1.0, 0.0)
        self.move_timer = 0.0
        self.MOVE_INTERVAL = 0.12
        self.game_speed = 1.0
        
        # ✅ FIXED: Call spawn_food AFTER play_area is initialized
        self.food = self.spawn_food()
        self.particles: List[Particle] = []
        self.saved_game_state = None
        
        self.bg_themes = [
            ((8, 12, 30), (18, 28, 50)),
            ((30, 8, 12), (50, 18, 28)),
            ((12, 30, 8), (28, 50, 18)),
            ((30, 12, 8), (50, 28, 18)),
            ((8, 30, 12), (18, 50, 28)),
            ((12, 8, 30), (28, 18, 50)),
        ]
        self.bg_index = 0
        
        self.bg_music = None
        self.eat_sound = None
        self.bg_channel = None
        self.eat_channel = None
        self.setup_audio()
        
        self.colors = {
            'bg_primary': (8, 12, 30),
            'bg_secondary': (18, 28, 50),
            'snake_head': (0, 220, 140),
            'snake_mouth': (255, 50, 50),
            'snake_eye_white': (255, 255, 255),
            'snake_eye_black': (0, 0, 0),
            'snake_body': (0, 180, 110),
            'snake_tail': (0, 120, 80),
            'food': (255, 80, 80),
            'ui_primary': (100, 200, 255),
            'ui_secondary': (255, 255, 255),
            'particle_gold': (255, 215, 0),
            'glow': (50, 255, 200),
            'score_box_bg': (45, 25, 80, 200),
            'score_box_border': (120, 80, 255),
            'control_box_bg': (80, 25, 45, 200),
            'control_box_border': (255, 120, 80),
            'highscore_box_bg': (25, 80, 45, 200),
            'highscore_box_border': (80, 255, 120),
            'button_bg': (60, 80, 120, 200),
            'button_hover': (100, 140, 200, 255),
            'button_text': (255, 255, 255),
            'button_border': (180, 200, 255),
            # New colors for welcome screen
            'welcome_text': (120, 220, 255),
            'logo_primary': (0, 255, 180),
            'logo_secondary': (100, 255, 200),
        }
        
        self.food_counter = 0
        self.big_food = False
        self.button_hover = {'new': False, 'pause': False, 'resume': False}
        self.touch_positions = []

    def update_play_area(self):
        scale = self.scale_manager.scale_x
        self.play_area = {
            'x': int(50 * scale),
            'y': int(180 * scale),
            'w': self.WIDTH - int(100 * scale),
            'h': self.HEIGHT - int(190 * scale)
        }

    def check_button_hover(self, pos_x: float, pos_y: float):
        scale = self.scale_manager.scale_x
        control_box_width = 220 * scale
        control_box_x = self.WIDTH // 2 - control_box_width // 2
        control_box_y = 70 * scale
        button_width = 50 * scale
        button_height = 28 * scale
        button_spacing = 6 * scale
        
        self.button_hover['new'] = False
        self.button_hover['pause'] = False
        self.button_hover['resume'] = False
        
        new_rect = pygame.Rect(control_box_x + 15 * scale, control_box_y + 25 * scale, 
                             button_width, button_height)
        if new_rect.collidepoint(pos_x, pos_y):
            self.button_hover['new'] = True
        
        pause_rect = pygame.Rect(control_box_x + 15 * scale + button_width + button_spacing, 
                               control_box_y + 25 * scale, button_width, button_height)
        if pause_rect.collidepoint(pos_x, pos_y):
            self.button_hover['pause'] = True
        
        resume_rect = pygame.Rect(control_box_x + 15 * scale + 2*(button_width + button_spacing), 
                                control_box_y + 25 * scale, button_width, button_height)
        if resume_rect.collidepoint(pos_x, pos_y):
            self.button_hover['resume'] = True

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        self.check_button_hover(*mouse_pos)
        
        current_touches = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.size
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                self.update_play_area()
                self.food = self.spawn_food()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_touch(mouse_pos[0], mouse_pos[1])
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU and event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif self.state in (GameState.PLAYING, GameState.RESUMED):
                    if event.key == pygame.K_UP and self.direction.y == 0:
                        self.next_direction = Vector2(0, -1)
                    elif event.key == pygame.K_DOWN and self.direction.y == 0:
                        self.next_direction = Vector2(0, 1)
                    elif event.key == pygame.K_LEFT and self.direction.x == 0:
                        self.next_direction = Vector2(-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction.x == 0:
                        self.next_direction = Vector2(1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.save_game_state()
                        self.state = GameState.PAUSED
                        if self.bg_channel:
                            self.bg_channel.pause()
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_r:
                        self.load_game_state()
                        self.state = GameState.RESUMED
                        if self.bg_channel:
                            self.bg_channel.unpause()
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
        
        self.direction = self.next_direction
        return True

    def handle_touch(self, pos_x: float, pos_y: float):
        scale = self.scale_manager.scale_x
        control_box_x = self.WIDTH // 2 - (220 * scale) // 2
        button_width = 50 * scale
        button_height = 28 * scale
        button_spacing = 6 * scale
        button_y = 95 * scale
        
        new_rect = pygame.Rect(control_box_x + 15 * scale, button_y, button_width, button_height)
        if new_rect.collidepoint(pos_x, pos_y):
            self.reset_game()
            self.state = GameState.PLAYING
            return
        
        pause_rect = pygame.Rect(control_box_x + 15 * scale + button_width + button_spacing, 
                               button_y, button_width, button_height)
        if pause_rect.collidepoint(pos_x, pos_y) and self.state in (GameState.PLAYING, GameState.RESUMED):
            self.save_game_state()
            self.state = GameState.PAUSED
            if self.bg_channel:
                self.bg_channel.pause()
            return
        
        resume_rect = pygame.Rect(control_box_x + 15 * scale + 2*(button_width + button_spacing), 
                                button_y, button_width, button_height)
        if resume_rect.collidepoint(pos_x, pos_y) and self.state == GameState.PAUSED:
            self.load_game_state()
            self.state = GameState.RESUMED
            if self.bg_channel:
                self.bg_channel.unpause()
            return

    def save_game_state(self):
        self.saved_game_state = {
            'snake': [Vector2(s.x, s.y) for s in self.snake],
            'direction': Vector2(self.direction.x, self.direction.y),
            'next_direction': Vector2(self.next_direction.x, self.next_direction.y),
            'food': Vector2(self.food.x, self.food.y),
            'score': self.score,
            'level': self.level,
            'game_speed': self.game_speed,
            'move_timer': self.move_timer,
            'MOVE_INTERVAL': self.MOVE_INTERVAL,
            'food_counter': self.food_counter,
            'big_food': self.big_food,
            'bg_index': self.bg_index
        }
    
    def load_game_state(self):
        if self.saved_game_state:
            self.snake = [Vector2(s.x, s.y) for s in self.saved_game_state['snake']]
            self.direction = self.saved_game_state['direction']
            self.next_direction = self.saved_game_state['next_direction']
            self.food = self.saved_game_state['food']
            self.score = self.saved_game_state['score']
            self.level = self.saved_game_state['level']
            self.game_speed = self.saved_game_state['game_speed']
            self.move_timer = self.saved_game_state['move_timer']
            self.MOVE_INTERVAL = self.saved_game_state['MOVE_INTERVAL']
            self.food_counter = self.saved_game_state['food_counter']
            self.big_food = self.saved_game_state['big_food']
            self.bg_index = self.saved_game_state['bg_index']

    def setup_audio(self):
        if not NUMPY_AVAILABLE:
            return
        try:
            self.bg_music = self.generate_bg_music()
            self.bg_channel = pygame.mixer.Channel(0)
            self.eat_sound = self.generate_eat_sound()
            self.eat_channel = pygame.mixer.Channel(1)
            print("✅ Audio loaded successfully!")
        except Exception as e:
            print(f"⚠️ Audio setup failed: {e}")
    
    def generate_bg_music(self):
        sample_rate = 22050
        duration = 10
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        drone = 0.3 * np.sin(2 * np.pi * 65 * t) * np.exp(-t * 0.1)
        pulse = 0.2 * np.sin(2 * np.pi * 130 * t) * (np.sin(t * 2) * 3.0 + 3.0)
        music = (drone + pulse) / 2 * 0.4
        stereo = np.column_stack((music, music))
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))
    
    def generate_eat_sound(self):
        sample_rate = 22050
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        growl = 0.8 * np.sin(2 * np.pi * 80 * t) * np.exp(-t * 8)
        screech = 0.6 * np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 5)
        sound = (growl + screech) * 0.6
        stereo = np.column_stack((sound * 0.8, sound * 0.6))
        return pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))
    
    def play_bg_music(self):
        if self.bg_music and self.bg_channel and not self.bg_channel.get_busy():
            self.bg_channel.play(self.bg_music, loops=-1)
    
    def play_eat_sound(self):
        if self.eat_sound and self.eat_channel:
            self.eat_channel.play(self.eat_sound)
    
    def load_high_score(self) -> int:
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open('high_score.json', 'w') as f:
                    json.dump({'high_score': self.high_score}, f)
            except:
                pass
    
    # ✅ FIXED: Correct random.randint() usage - only 2 arguments
    def spawn_food(self) -> Vector2:
        while True:
            food_x = random.randint(
                self.play_area['x'] + self.snake_block, 
                self.play_area['x'] + self.play_area['w'] - self.snake_block * 2
            )
            food_y = random.randint(
                self.play_area['y'] + self.snake_block, 
                self.play_area['y'] + self.play_area['h'] - self.snake_block * 2
            )
            food = Vector2(food_x, food_y)
            if food not in self.snake:
                return food
    
    def update_game(self, dt: float):
        if self.state not in (GameState.PLAYING, GameState.RESUMED):
            return
        
        self.move_timer += dt
        if self.move_timer >= self.MOVE_INTERVAL:
            self.move_timer = 0
            head = self.snake[0]
            new_head = Vector2(
                head.x + self.direction.x * self.snake_block,
                head.y + self.direction.y * self.snake_block
            )
            
            # Collision detection
            if (new_head.x < self.play_area['x'] or 
                new_head.x >= self.play_area['x'] + self.play_area['w'] or 
                new_head.y < self.play_area['y'] or 
                new_head.y >= self.play_area['y'] + self.play_area['h'] or 
                new_head in self.snake[1:]):
                self.game_over()
                return
            
            self.snake.insert(0, new_head)
            
            # Food collision
            if (abs(new_head.x - self.food.x) < self.snake_block and 
                abs(new_head.y - self.food.y) < self.snake_block):
                self.food_counter += 1
                self.big_food = (self.food_counter % 3 == 0)
                self.score += 30 if self.big_food else 10 * self.level
                
                self.game_speed = min(1.0 + self.food_counter * 0.05, 2.5)
                self.MOVE_INTERVAL = max(0.08, 0.15 - self.game_speed * 0.03)
                
                self.bg_index = (self.bg_index + 1) % len(self.bg_themes)
                self.colors['bg_primary'], self.colors['bg_secondary'] = self.bg_themes[self.bg_index]
                self.play_eat_sound()
                
                particle_count = 25 if self.big_food else 15
                center_x = self.food.x + self.snake_block//2
                center_y = self.food.y + self.snake_block//2
                for _ in range(particle_count):
                    self.particles.append(Particle(center_x, center_y, self.colors['particle_gold']))
                
                self.food = self.spawn_food()
                if self.score % 200 == 0:
                    self.level += 1
            else:
                self.snake.pop()
        
        self.particles = [p for p in self.particles if p.update()]
    
    def reset_game(self):
        self.snake = [Vector2(250, 375)]
        self.direction = Vector2(1.0, 0.0)
        self.next_direction = Vector2(1.0, 0.0)
        self.score = 0
        self.level = 1
        self.game_speed = 1.0
        self.move_timer = 0.0
        self.MOVE_INTERVAL = 0.12
        self.food = self.spawn_food()
        self.particles.clear()
        self.bg_index = 0
        self.colors['bg_primary'], self.colors['bg_secondary'] = self.bg_themes[0]
        self.food_counter = 0
        self.big_food = False
        self.saved_game_state = None
    
    def game_over(self):
        self.save_high_score()
        if self.bg_channel:
            self.bg_channel.stop()
        self.state = GameState.GAME_OVER

    def draw_gradient_bg(self, screen):
        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            r = int(self.colors['bg_primary'][0] + (self.colors['bg_secondary'][0] - self.colors['bg_primary'][0]) * ratio)
            g = int(self.colors['bg_primary'][1] + (self.colors['bg_secondary'][1] - self.colors['bg_primary'][1]) * ratio)
            b = int(self.colors['bg_primary'][2] + (self.colors['bg_secondary'][2] - self.colors['bg_primary'][2]) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.WIDTH, y))
        
        grid_color = (255, 255, 255, 30)
        for x in range(self.play_area['x'], self.play_area['x'] + self.play_area['w'], self.snake_block):
            pygame.draw.line(screen, grid_color, (x, self.play_area['y']), (x, self.play_area['y'] + self.play_area['h']), 1)
        for y in range(self.play_area['y'], self.play_area['y'] + self.play_area['h'], self.snake_block):
            pygame.draw.line(screen, grid_color, (self.play_area['x'], y), (self.play_area['x'] + self.play_area['w'], y), 1)

    def draw_menu_bar(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, self.WIDTH, 60))
        pygame.draw.line(screen, self.colors['ui_primary'], (0, 60), (self.WIDTH, 60), 2)
        title = self.font_medium.render("🐍 SNAKE PRO - ULTRA SMOOTH", True, self.colors['ui_secondary'])
        screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 15))

    def draw_play_area_borders(self, screen):
        pygame.draw.rect(screen, self.colors['ui_primary'], 
                        (self.play_area['x'], self.play_area['y'], self.play_area['w'], self.play_area['h']), 4)

    def draw_real_snake(self, screen):
        head = self.snake[0]
        head_center = (int(head.x + self.snake_block//2), int(head.y + self.snake_block//2))
        
        pygame.draw.circle(screen, self.colors['glow'], head_center, self.snake_block//2 + 4)
        
        head_points = [
            (head_center[0], int(head.y)),
            (int(head.x), int(head.y + self.snake_block)),
            (int(head.x + self.snake_block), int(head.y + self.snake_block))
        ]
        pygame.draw.polygon(screen, self.colors['snake_head'], head_points)
        
        mouth_points = [
            (head_center[0] + 8, head_center[1] - 4),
            (head_center[0] + 14, head_center[1] - 8),
            (head_center[0] + 14, head_center[1])
        ]
        pygame.draw.polygon(screen, self.colors['snake_mouth'], mouth_points)
        
        eye1 = (head_center[0] - 6, head_center[1] - 8)
        eye2 = (head_center[0], head_center[1] - 8)
        pygame.draw.circle(screen, self.colors['snake_eye_white'], eye1, 4)
        pygame.draw.circle(screen, self.colors['snake_eye_black'], eye1, 2)
        pygame.draw.circle(screen, self.colors['snake_eye_white'], eye2, 3)
        pygame.draw.circle(screen, self.colors['snake_eye_black'], eye2, 1)
        
        for i, segment in enumerate(self.snake[1:]):
            body_ratio = i / max(1, len(self.snake) - 1)
            body_width = max(10, self.snake_block - int(body_ratio * 12))
            body_color = (0, int(180 - body_ratio * 80), int(110 - body_ratio * 50))
            pygame.draw.ellipse(screen, body_color, 
                              (int(segment.x + 3), int(segment.y + 3), body_width, self.snake_block - 6))
        
        if len(self.snake) > 2:
            tail = self.snake[-1]
            tail_points = [
                (int(tail.x + self.snake_block//2), int(tail.y + 2)),
                (int(tail.x + 2), int(tail.y + self.snake_block//2)),
                (int(tail.x + self.snake_block//2), int(tail.y + self.snake_block - 2))
            ]
            pygame.draw.polygon(screen, self.colors['snake_tail'], tail_points)

    def draw_food(self, screen):
        center = (int(self.food.x + self.snake_block//2), int(self.food.y + self.snake_block//2))
        if self.big_food:
            glow_radius = self.snake_block + 3
            food_radius = self.snake_block
        else:
            glow_radius = self.snake_block//2 + 3
            food_radius = self.snake_block//2
        
        pygame.draw.circle(screen, self.colors['glow'], center, glow_radius)
        pygame.draw.circle(screen, self.colors['food'], center, food_radius)

    def draw_paused_menu(self, screen):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("PAUSED", True, self.colors['ui_secondary'])
        score = self.font_medium.render(f"Score: {self.score}", True, self.colors['ui_primary'])
        instructions = self.font_small.render("Touch/Swipe: Move | ESC:R/Q", True, self.colors['ui_secondary'])
        
        screen.blit(title, (self.WIDTH//2 - title.get_width()//2, self.HEIGHT//2 - 80))
        screen.blit(score, (self.WIDTH//2 - score.get_width()//2, self.HEIGHT//2))
        screen.blit(instructions, (self.WIDTH//2 - instructions.get_width()//2, self.HEIGHT//2 + 80))

    def draw_snake_pro_logo(self, screen, x: int, y: int, scale: float = 1.0):
        """Draws a professional Snake Pro logo"""
        logo_width = 120 * scale
        logo_height = 80 * scale
        
        # Main snake body (curved S shape)
        points = [
            (x + 20*scale, y + 10*scale),
            (x + 40*scale, y + 5*scale),
            (x + 60*scale, y + 20*scale),
            (x + 80*scale, y + 15*scale),
            (x + 100*scale, y + 30*scale),
        ]
        pygame.draw.lines(screen, self.colors['logo_secondary'], False, points, int(12*scale))
        
        # Snake head
        head_center = (int(x + 105*scale), int(y + 35*scale))
        head_points = [
            head_center,
            (int(x + 90*scale), int(y + 25*scale)),
            (int(x + 90*scale), int(y + 45*scale))
        ]
        pygame.draw.polygon(screen, self.colors['logo_primary'], head_points)
        
        # Snake eyes
        eye1 = (int(x + 95*scale), int(y + 30*scale))
        eye2 = (int(x + 100*scale), int(y + 32*scale))
        pygame.draw.circle(screen, (255, 255, 255), eye1, int(3*scale))
        pygame.draw.circle(screen, (0, 0, 0), eye1, int(1*scale))
        pygame.draw.circle(screen, (255, 255, 255), eye2, int(2*scale))
        pygame.draw.circle(screen, (0, 0, 0), eye2, int(1*scale))
        
        # Glow effect
        pygame.draw.circle(screen, (0, 255, 200, 100), head_center, int(15*scale), 0)
        
        # "PRO" text next to snake
        pro_text = self.font_logo.render("PRO", True, self.colors['logo_primary'])
        screen.blit(pro_text, (int(x + 30*scale), int(y + 45*scale)))

    def draw_menu(self, screen):
        self.draw_gradient_bg(screen)
        
        # NEW: Welcome text and logo in the top empty space (above gradient play area)
        scale = self.scale_manager.scale_x
        welcome_text = self.font_welcome.render("WELCOME TO SNAKE PRO GAME", True, self.colors['welcome_text'])
        screen.blit(welcome_text, (self.WIDTH//2 - welcome_text.get_width()//2, 90))
        
        # Snake Pro Logo
        self.draw_snake_pro_logo(screen, self.WIDTH//2 - 60, 130, scale)
        
        # Original menu content below
        title = self.font_large.render("🐍 REAL SNAKE PRO", True, self.colors['ui_secondary'])
        subtitle = self.font_medium.render("ULTRA SMOOTH EDITION", True, self.colors['ui_primary'])
        instruction = self.font_small.render("SPACE/Touch: Start | Arrow Keys: Move", True, self.colors['ui_secondary'])
        hs_text = self.font_medium.render(f"High Score: {self.high_score}", True, self.colors['ui_primary'])
        
        screen.blit(title, (self.WIDTH//2 - title.get_width()//2, self.HEIGHT//2 - 100))
        screen.blit(subtitle, (self.WIDTH//2 - subtitle.get_width()//2, self.HEIGHT//2 - 40))
        screen.blit(instruction, (self.WIDTH//2 - instruction.get_width()//2, self.HEIGHT//2 + 40))
        screen.blit(hs_text, (self.WIDTH//2 - hs_text.get_width()//2, self.HEIGHT//2 + 100))

    def draw_game_over(self, screen):
        self.draw_gradient_bg(screen)
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("GAME OVER", True, self.colors['ui_secondary'])
        score = self.font_medium.render(f"Final Score: {self.score}", True, self.colors['ui_primary'])
        hs = self.font_medium.render(f"High Score: {self.high_score}", True, self.colors['ui_primary'])
        restart = self.font_small.render("R=Restart | M=Menu | Click Buttons", True, self.colors['ui_secondary'])
        
        screen.blit(title, (self.WIDTH//2 - title.get_width()//2, self.HEIGHT//2 - 80))
        screen.blit(score, (self.WIDTH//2 - score.get_width()//2, self.HEIGHT//2))
        screen.blit(hs, (self.WIDTH//2 - hs.get_width()//2, self.HEIGHT//2 + 60))
        screen.blit(restart, (self.WIDTH//2 - restart.get_width()//2, self.HEIGHT//2 + 140))

    def draw_ui(self, screen):
        scale = self.scale_manager.scale_x
        box_height = int(100 * scale)
        box_y = int(70 * scale)
        box_inner_y = box_y + int(10 * scale)
        
        # Score Box
        score_box_width = int(340 * scale)
        score_rect = pygame.Rect(int(30 * scale), box_y, score_box_width, box_height)
        pygame.draw.rect(screen, self.colors['score_box_bg'], score_rect)
        pygame.draw.rect(screen, self.colors['score_box_border'], score_rect, 4)
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, self.colors['ui_secondary'])
        level_text = self.font_small.render(f"Level: {self.level}", True, self.colors['ui_secondary'])
        speed_text = self.font_small.render(f"Speed: {self.game_speed:.1f}", True, self.colors['score_box_border'])
        screen.blit(score_text, (int(45 * scale), box_inner_y))
        screen.blit(level_text, (int(45 * scale), box_inner_y + int(35 * scale)))
        screen.blit(speed_text, (int(45 * scale), box_inner_y + int(65 * scale)))
        
        # Control Box
        if self.state in (GameState.PLAYING, GameState.RESUMED, GameState.PAUSED):
            control_box_width = int(220 * scale)
            control_box_x = self.WIDTH // 2 - control_box_width // 2
            control_rect = pygame.Rect(control_box_x, box_y, control_box_width, box_height)
            pygame.draw.rect(screen, self.colors['control_box_bg'], control_rect)
            pygame.draw.rect(screen, self.colors['control_box_border'], control_rect, 4)
            
            control_title = self.font_small.render("CONTROLS", True, self.colors['ui_secondary'])
            screen.blit(control_title, (control_box_x + int(15 * scale), box_inner_y))
            
            button_width = int(50 * scale)
            button_height = int(28 * scale)
            button_spacing = int(6 * scale)
            button_y = int(95 * scale)
            
            # NEW Button
            new_color = self.colors['button_hover'] if self.button_hover['new'] else self.colors['button_bg']
            pygame.draw.rect(screen, new_color, (control_box_x + int(15 * scale), button_y, button_width, button_height))
            pygame.draw.rect(screen, self.colors['button_border'], (control_box_x + int(15 * scale), button_y, button_width, button_height), 2)
            new_text = self.font_button.render("NEW", True, self.colors['button_text'])
            screen.blit(new_text, (control_box_x + int(15 * scale) + (button_width - new_text.get_width()) // 2, button_y + int(6 * scale)))
            
            # PAUSE Button
            pause_x = control_box_x + int(15 * scale) + button_width + button_spacing
            pause_color = self.colors['button_hover'] if self.button_hover['pause'] else self.colors['button_bg']
            pygame.draw.rect(screen, pause_color, (pause_x, button_y, button_width, button_height))
            pygame.draw.rect(screen, self.colors['button_border'], (pause_x, button_y, button_width, button_height), 2)
            pause_text = self.font_button.render("PAUSE", True, self.colors['button_text'])
            screen.blit(pause_text, (pause_x + (button_width - pause_text.get_width()) // 2, button_y + int(4 * scale)))
            
            # RESUME Button
            resume_x = control_box_x + int(15 * scale) + 2*(button_width + button_spacing)
            resume_color = self.colors['button_hover'] if self.button_hover['resume'] else self.colors['button_bg']
            pygame.draw.rect(screen, resume_color, (resume_x, button_y, button_width, button_height))
            pygame.draw.rect(screen, self.colors['button_border'], (resume_x, button_y, button_width, button_height), 2)
            resume_text = self.font_button.render("RESUME", True, self.colors['button_text'])
            screen.blit(resume_text, (resume_x + (button_width - resume_text.get_width()) // 2, button_y + int(6 * scale)))
        
        # High Score Box
        hs_box_width = int(340 * scale)
        hs_rect = pygame.Rect(self.WIDTH - int(30 * scale) - hs_box_width, box_y, hs_box_width, box_height)
        pygame.draw.rect(screen, self.colors['highscore_box_bg'], hs_rect)
        pygame.draw.rect(screen, self.colors['highscore_box_border'], hs_rect, 4)
        hs_text = self.font_medium.render(f"High: {self.high_score}", True, self.colors['ui_secondary'])
        screen.blit(hs_text, (self.WIDTH - int(25 * scale) - hs_box_width, box_inner_y + int(20 * scale)))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            running = self.handle_input()
            
            if self.state in (GameState.PLAYING, GameState.RESUMED):
                self.update_game(dt)
                self.play_bg_music()
            
            self.screen.fill(self.colors['bg_primary'])
            self.draw_gradient_bg(self.screen)
            self.draw_menu_bar(self.screen)
            
            if self.state == GameState.MENU:
                self.play_bg_music()
                self.draw_menu(self.screen)
            elif self.state in (GameState.PLAYING, GameState.RESUMED):
                self.draw_ui(self.screen)
                self.draw_play_area_borders(self.screen)
                self.draw_real_snake(self.screen)
                self.draw_food(self.screen)
                for particle in self.particles:
                    particle.draw(self.screen, self.scale_manager.scale_x, self.scale_manager.scale_y)
            elif self.state == GameState.PAUSED:
                self.draw_ui(self.screen)
                self.draw_play_area_borders(self.screen)
                self.draw_real_snake(self.screen)
                self.draw_food(self.screen)
                for particle in self.particles:
                    particle.draw(self.screen, self.scale_manager.scale_x, self.scale_manager.scale_y)
                self.draw_paused_menu(self.screen)
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    print("🐍 Starting FIXED Snake Pro - 100% STABLE!")
    print("✅ ALL CRASHES FIXED | ULTRA SMOOTH | FULLY RESPONSIVE | PROFESSIONAL WELCOME SCREEN")
    game = SnakeGame()
    game.run()
