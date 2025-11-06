import pygame
import socket
import pickle
import time

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((600, 450), pygame.RESIZABLE)
pygame.display.set_caption("Hop 'n' Hiss Controller")
font = pygame.font.SysFont(None, 24)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Directions
UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'

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
    print("No joystick detected")

# GUI elements
ip = "127.0.0.1"
port = "5005"
active_text = None
sending = False
sock = None
last_direction = None
cursor_visible = True
last_cursor_toggle = time.time()
stick_choice = 'right'  # 'left' or 'right'

# Rects
ip_label_rect = pygame.Rect(50, 50, 100, 30)
ip_input_rect = pygame.Rect(160, 50, 200, 30)
port_label_rect = pygame.Rect(50, 100, 100, 30)
port_input_rect = pygame.Rect(160, 100, 200, 30)
start_button_rect = pygame.Rect(380, 50, 100, 40)
stick_button_rect = pygame.Rect(380, 100, 100, 30)
# Direction buttons (triangles) - positions will be calculated dynamically
offset_y = 95
offset_x = 80
triangle_size = 30
enclosing_radius = 130
joystick_y = 280
center_radius = 25

def get_direction():
    if has_joystick:
        pygame.event.pump()
        if stick_choice == 'right' and joystick.get_numaxes() > 4:
            x = joystick.get_axis(3)  # Right horizontal
            y = joystick.get_axis(4)  # Right vertical
        elif stick_choice == 'left':
            x = joystick.get_axis(0)  # Left horizontal
            y = joystick.get_axis(1)  # Left vertical
        else:
            return None
        
        if y < -0.5:
            return UP
        elif y > 0.5:
            return DOWN
        elif x < -0.5:
            return LEFT
        elif x > 0.5:
            return RIGHT
    return None

def draw_text(text, rect, color=WHITE, show_cursor=False):
    txt_surface = font.render(text, True, color)
    screen.blit(txt_surface, (rect.x + 5, rect.y + 5))
    if show_cursor and cursor_visible:
        cursor_x = rect.x + 5 + txt_surface.get_width()
        pygame.draw.line(screen, color, (cursor_x, rect.y + 5), (cursor_x, rect.y + 25), 2)

def is_point_in_circle(point, center, radius):
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return dx*dx + dy*dy <= radius*radius

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if ip_input_rect.collidepoint(event.pos):
                active_text = 'ip'
            elif port_input_rect.collidepoint(event.pos):
                active_text = 'port'
            elif start_button_rect.collidepoint(event.pos):
                sending = not sending
                if sending:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    except:
                        pass
                else:
                    if sock:
                        sock.close()
                        sock = None
            elif stick_button_rect.collidepoint(event.pos):
                stick_choice = 'left' if stick_choice == 'right' else 'right'
            else:
                active_text = None
        elif event.type == pygame.KEYDOWN:
            if active_text == 'ip' or active_text == 'port':
                if event.key == pygame.K_BACKSPACE:
                    if active_text == 'ip' and len(ip) > 0:
                        ip = ip[:-1]
                    elif active_text == 'port' and len(port) > 0:
                        port = port[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                    active_text = None
                elif event.key != pygame.K_LSHIFT and event.key != pygame.K_RSHIFT:
                    char = event.unicode
                    if char and char.isprintable():
                        if active_text == 'ip':
                            ip += char
                        elif active_text == 'port' and char.isdigit():
                            port += char
    
    # Toggle cursor
    current_time = time.time()
    if current_time - last_cursor_toggle > 0.5:
        cursor_visible = not cursor_visible
        last_cursor_toggle = current_time

    direction = get_direction()
    if sending and direction and direction != last_direction:
        try:
            data = pickle.dumps(direction.encode())
            sock.sendto(data, (ip, int(port)))
            last_direction = direction
        except:
            pass
    elif not sending:
        last_direction = None
    
    # Draw
    # Get current screen size for centering
    width, height = screen.get_size()
    center_x = width // 2
    center_y = height // 2
    
    # Update positions - joystick below text, horizontally centered
    center_circle_pos = (center_x, joystick_y)
    up_center_pos = (center_x, joystick_y - offset_y)
    down_center_pos = (center_x, joystick_y + offset_y)
    left_center_pos = (center_x - offset_x, joystick_y)
    right_center_pos = (center_x + offset_x, joystick_y)
    
    screen.fill(BLACK)
    
    # Labels
    draw_text("IP:", ip_label_rect)
    draw_text("Port:", port_label_rect)
    
    # Input boxes
    pygame.draw.rect(screen, BLUE if active_text == 'ip' else GRAY, ip_input_rect, 2)
    draw_text(ip, ip_input_rect, show_cursor=(active_text == 'ip'))
    pygame.draw.rect(screen, BLUE if active_text == 'port' else GRAY, port_input_rect, 2)
    draw_text(port, port_input_rect, show_cursor=(active_text == 'port'))
    
    # Buttons
    pygame.draw.rect(screen, GREEN if sending else GRAY, start_button_rect)
    button_text = "Stop" if sending else "Start"
    button_text_surface = font.render(button_text, True, BLACK)
    text_rect = button_text_surface.get_rect(center=start_button_rect.center)
    screen.blit(button_text_surface, text_rect)
    
    pygame.draw.rect(screen, BLUE, stick_button_rect)
    stick_text = f"{stick_choice.capitalize()} Stick"
    stick_text_surface = font.render(stick_text, True, BLACK)
    stick_text_rect = stick_text_surface.get_rect(center=stick_button_rect.center)
    screen.blit(stick_text_surface, stick_text_rect)
    
    # Enclosing circle for joystick
    pygame.draw.circle(screen, GRAY, center_circle_pos, enclosing_radius, 2)
    
    # Direction buttons (triangles)
    # Up triangle: base at top, point down (towards center)
    up_points = [(up_center_pos[0], up_center_pos[1] - triangle_size), (up_center_pos[0] - triangle_size, up_center_pos[1] + triangle_size), (up_center_pos[0] + triangle_size, up_center_pos[1] + triangle_size)]
    pygame.draw.polygon(screen, GREEN if last_direction == UP else GRAY, up_points)
    # Down triangle: base at bottom, point up (towards center)
    down_points = [(down_center_pos[0], down_center_pos[1] + triangle_size), (down_center_pos[0] - triangle_size, down_center_pos[1] - triangle_size), (down_center_pos[0] + triangle_size, down_center_pos[1] - triangle_size)]
    pygame.draw.polygon(screen, GREEN if last_direction == DOWN else GRAY, down_points)
    # Left triangle: base at left, point right (towards center)
    left_points = [(left_center_pos[0] - triangle_size, left_center_pos[1]), (left_center_pos[0] + triangle_size, left_center_pos[1] - triangle_size), (left_center_pos[0] + triangle_size, left_center_pos[1] + triangle_size)]
    pygame.draw.polygon(screen, GREEN if last_direction == LEFT else GRAY, left_points)
    # Right triangle: base at right, point left (towards center)
    right_points = [(right_center_pos[0] + triangle_size, right_center_pos[1]), (right_center_pos[0] - triangle_size, right_center_pos[1] - triangle_size), (right_center_pos[0] - triangle_size, right_center_pos[1] + triangle_size)]
    pygame.draw.polygon(screen, GREEN if last_direction == RIGHT else GRAY, right_points)
    # Center circle
    pygame.draw.circle(screen, GRAY, center_circle_pos, center_radius)
    
    pygame.display.flip()
    time.sleep(0.1)

if sock:
    sock.close()
pygame.quit()