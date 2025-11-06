import pygame
import socket
import pickle
import time

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Block size
BLOCK_SIZE = 20

# FPS
FPS = 10

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
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            x = (pygame.time.get_ticks() % (SCREEN_WIDTH // BLOCK_SIZE)) * BLOCK_SIZE
            y = (pygame.time.get_ticks() % (SCREEN_HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE
            if (x, y) not in self.snake:
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
            new_head in self.snake):
            self.game_over = True
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
        pygame.draw.rect(self.screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
        font = pygame.font.SysFont(None, 35)
        text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))
        pygame.display.update()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)

        print("Waiting for start signal from joystick...")
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print("Start signal received, starting game...")
                break
            except BlockingIOError:
                pass
            time.sleep(0.1)

        while not self.game_over:
            try:
                data, addr = sock.recvfrom(1024)
                direction = pickle.loads(data).decode()
                if direction in [UP, DOWN, LEFT, RIGHT]:
                    self.direction = direction
            except BlockingIOError:
                pass

            self.move_snake()
            self.draw()
            self.clock.tick(FPS)

        # Game over screen
        font = pygame.font.SysFont(None, 55)
        text = font.render("Game Over", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()