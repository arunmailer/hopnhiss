# Snake Game over Intranet

This is a Snake game implemented with Pygame, controlled remotely over UDP socket.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the game: `python src/main.py` (on the display device)
3. Run the joystick sender: `python src/joystick_sender.py` (on the control device, update UDP_IP to the game device's IP)

## Standalone Executables

Executables are available in the `dist/` folder:
- `dist/main`: Run the Snake game receiver.
- `dist/joystick_sender`: Run the joystick sender.

No Python installation required for these executables.

## How to Play

- The game listens for direction commands (UP, DOWN, LEFT, RIGHT) over UDP on port 5005.
- Use the joystick sender script on another device to control the snake.
- Eat the red food to grow and increase score.
- Avoid walls and yourself.

## Notes

- Ensure both devices are on the same network.
- Update the UDP_IP in joystick_sender.py or the executable's config if needed to the IP address of the device running the game.