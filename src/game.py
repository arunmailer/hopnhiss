import pygame
import socket
import pickle
import time
import random
import xml.etree.ElementTree as ET

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def draw_stripe_rect(screen, x, y, w, h, color=BLUE, stripe_width=4):
    # Draw vertical stripes
    for i in range(0, w, stripe_width):
        pygame.draw.line(screen, color, (x + i, y), (x + i, y + h - 1))
    # Optionally, alternate colors, but for simplicity, just blue stripes

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Block size
BLOCK_SIZE = 15

# FPS
FPS = 6

# UDP settings
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005

# Directions
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hop 'n' Hiss")
        self.clock = pygame.time.Clock()
        self.load_config()
        self.reset()

    def load_config(self):
        try:
            tree = ET.parse('config.xml')
            root = tree.getroot()
            self.fps = int(root.find('fps').text)
            self.udp_ip = root.find('udp_ip').text
            self.udp_port = int(root.find('udp_port').text)
            obstacles_enabled = int(root.find('obstacles').text)
            num_obstacles = int(root.find('num_obstacles').text) if root.find('num_obstacles') is not None else 50
        except Exception as e:
            self.fps = 6
            self.udp_ip = "0.0.0.0"
            self.udp_port = 5005
            obstacles_enabled = 0
            num_obstacles = 50
        
        self.obstacles = []
        if obstacles_enabled:
            # Generate random maze obstacles, each 2x2 blocks
            obs_size = 2 * BLOCK_SIZE
            for _ in range(num_obstacles):
                x = random.randint(0, (SCREEN_WIDTH // obs_size) - 1) * obs_size
                y = random.randint(0, (SCREEN_HEIGHT // obs_size) - 1) * obs_size
                # Avoid the starting area of the snake (top-left corner)
                if not (x < 200 and y < 200):
                    self.obstacles.append((x, y, obs_size, obs_size))

    def reset(self):
        start_x = (SCREEN_WIDTH // 2) // BLOCK_SIZE * BLOCK_SIZE
        start_y = (SCREEN_HEIGHT // 2) // BLOCK_SIZE * BLOCK_SIZE
        self.snake = [(start_x, start_y)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            x = random.randint(0, SCREEN_WIDTH // BLOCK_SIZE - 1) * BLOCK_SIZE
            y = random.randint(0, SCREEN_HEIGHT // BLOCK_SIZE - 1) * BLOCK_SIZE
            if (x, y) not in self.snake and not any(obs[0] <= x < obs[0] + obs[2] and obs[1] <= y < obs[1] + obs[3] for obs in self.obstacles):
                return (x, y)

    def move_snake(self):
        head = self.snake[0]
        if self.direction == UP:
            new_head = (head[0], head[1] - BLOCK_SIZE)
        elif self.direction == DOWN:
            new_head = (head[0], head[1] + BLOCK_SIZE)
        elif self.direction == LEFT:
            new_head = (head[0] - BLOCK_SIZE, head[1])
        elif self.direction == RIGHT:
            new_head = (head[0] + BLOCK_SIZE, head[1])

        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in self.snake or any(obs[0] <= new_head[0] < obs[0] + obs[2] and obs[1] <= new_head[1] < obs[1] + obs[3] for obs in self.obstacles)):
            self.game_over = True
            print("Game over triggered")
            return
        
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))
        for obs in self.obstacles:
            draw_stripe_rect(self.screen, obs[0], obs[1], obs[2], obs[3])
        pygame.draw.rect(self.screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
        font = pygame.font.SysFont(None, 35)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))
        pygame.display.update()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))
        sock.setblocking(False)

        running = True
        skip_waiting = False
        while running:
            if not skip_waiting:
                print("Waiting for start signal from joystick...")
                waiting_start = True
                while waiting_start:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting_start = False
                    try:
                        data, addr = sock.recvfrom(1024)
                        print("Start signal received, starting game...")
                        waiting_start = False
                    except BlockingIOError:
                        pass
                    
                    self.screen.fill(BLACK)
                    font = pygame.font.SysFont(None, 35)
                    text = font.render("Waiting for joystick input...", True, WHITE)
                    self.screen.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))
                    pygame.display.update()
                    time.sleep(0.1)
            skip_waiting = False

            if not running:
                break

            self.reset()
            while not self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_over = True
                        running = False
                try:
                    data, addr = sock.recvfrom(1024)
                    direction = pickle.loads(data).decode()
                    if direction in [UP, DOWN, LEFT, RIGHT]:
                        self.direction = direction
                except BlockingIOError:
                    pass

                self.move_snake()
                self.draw()
                self.clock.tick(self.fps)

            # Game over screen
            flash_count = 0
            visible = True
            flash_timer = time.time()
            blinking = True
            waiting_restart = True
            while blinking or waiting_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        blinking = False
                        waiting_restart = False
                        running = False
                
                try:
                    data, addr = sock.recvfrom(1024)
                    direction = pickle.loads(data).decode()
                    if direction in [UP, DOWN, LEFT, RIGHT] and not blinking:
                        self.direction = direction
                        skip_waiting = True
                        waiting_restart = False
                except BlockingIOError:
                    pass
                
                current_time = time.time()
                if blinking and current_time - flash_timer > 1.0:
                    visible = not visible
                    flash_timer = current_time
                    flash_count += 1
                    if flash_count >= 4:  # 2 blinks
                        blinking = False
                        visible = True  # Show steady
                
                self.screen.fill(BLACK)
                if visible:
                    font = pygame.font.SysFont(None, 55)
                    text = font.render("Game Over", True, WHITE)
                    self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
                if not blinking:
                    font_small = pygame.font.SysFont(None, 35)
                    restart_text = font_small.render("Move joystick to restart", True, WHITE)
                    self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 20))
                pygame.display.update()
                time.sleep(0.1)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()