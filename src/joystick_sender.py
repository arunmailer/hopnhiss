import pygame
import socket
import pickle
import time

# Initialize Pygame
pygame.init()

# UDP settings
UDP_IP = "127.0.0.1"  # Change to the IP of the game device
UDP_PORT = 5005

# Directions
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Check for joystick
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
print(f"Joystick count: {joystick_count}")
has_joystick = joystick_count > 0
if has_joystick:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Using joystick: {joystick.get_name()}")
else:
    print("No joystick detected, using keyboard (arrow keys, ESC to quit)")

def get_direction():
    if has_joystick:
        pygame.event.pump()
        x = joystick.get_axis(0)  # Horizontal axis
        y = joystick.get_axis(1)  # Vertical axis

        if y < -0.5:
            return UP
        elif y > 0.5:
            return DOWN
        elif x < -0.5:
            return LEFT
        elif x > 0.5:
            return RIGHT
    else:
        # Keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            return UP
        elif keys[pygame.K_DOWN]:
            return DOWN
        elif keys[pygame.K_LEFT]:
            return LEFT
        elif keys[pygame.K_RIGHT]:
            return RIGHT
        elif keys[pygame.K_ESCAPE]:
            return 'QUIT'
    return None

running = True
last_direction = None
while running:
    direction = get_direction()
    if direction == 'QUIT':
        running = False
    elif direction and direction != last_direction:
        data = pickle.dumps(direction.encode())
        sock.sendto(data, (UDP_IP, UDP_PORT))
        last_direction = direction
    time.sleep(0.1)  # Poll every 100ms

pygame.quit()