import pygame
import sys
import time
import serial  # Import pyserial for communication with Arduino

# Initialize Pygame and the mixer
pygame.init()
pygame.mixer.init()

# Screen settings
screen_width, screen_height = 1500, 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Where's Waldo Game")

# Load and resize the background image
background = pygame.image.load("WW1.jpg")  # replace with your own background image
background = pygame.transform.scale(background, (screen_width, screen_height))

# Waldo's location and clickable area
waldo_position = (928, 281)  # Replace with Waldo Coordinates coordinates
waldo_radius = 20

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Game settings
font = pygame.font.Font(None, 36)
timer_start = time.time()
time_limit = 60  # 1 minute timer
found_waldo = False
relay_activated = False  # Flag to track if relay has been activated

# Serial setup for Arduino communication
arduino = serial.Serial('COM13', 9600)  # Replace with used COM port

# Load music tracks
pygame.mixer.music.load("Nice.mp3")  # Replace with sound track 1
pygame.mixer.music.play(-1)  # Loop the first track indefinitely
track2 = pygame.mixer.Sound("uhoh.mp3")  # Replace with sound track 2

# Game loop
running = True
while running:
    screen.fill(WHITE)
    screen.blit(background, (0, 0))

    # Calculate remaining time
    elapsed_time = int(time.time() - timer_start)
    remaining_time = max(0, time_limit - elapsed_time)

    # Switch to the second track when 11 seconds remain
    if remaining_time == 11 and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        track2.play()

    # Display the timer
    timer_text = font.render(f"Time left: {remaining_time}s", True, BLACK)
    screen.blit(timer_text, (10, 10))

    # Check if time is up and relay has not been activated
    if remaining_time == 0 and not found_waldo and not relay_activated:
        # Send signal to Arduino to activate relay once
        arduino.write(b"activate_relay\n")
        relay_activated = True  # Set flag to prevent repeated signals

        # Display "Time's up!" message
        time_up_text = font.render("Time's up! You didn't find Waldo!", True, RED)
        time_up_rect = time_up_text.get_rect(center=(screen_width // 2, screen_height // 2))
        pygame.draw.rect(screen, WHITE, time_up_rect.inflate(20, 10))
        screen.blit(time_up_text, time_up_rect)

        # Wait 3 seconds before exiting
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False  # Exit the game loop after delay

    elif found_waldo:
        # Display "You found Waldo!" message
        found_text = font.render("You found Waldo!", True, RED)
        found_rect = found_text.get_rect(center=(screen_width // 2, screen_height // 2))
        pygame.draw.rect(screen, WHITE, found_rect.inflate(20, 10))
        screen.blit(found_text, found_rect)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not found_waldo:
                mouse_x, mouse_y = event.pos
                distance = ((mouse_x - waldo_position[0]) ** 2 + (mouse_y - waldo_position[1]) ** 2) ** 0.5

                if distance < waldo_radius:
                    found_waldo = True

    pygame.display.flip()

# Clean up
arduino.close()
pygame.quit()
sys.exit()
