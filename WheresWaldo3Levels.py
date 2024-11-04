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

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Game settings
font = pygame.font.Font(None, 36)
found_waldo = False
relay_activated = False
level = 0  # Start with level 0
num_levels = 3  # Total number of levels

# Serial setup for Arduino communication
arduino = serial.Serial('COM12', 9600)  # Update to COM port of choice

# Load music tracks
pygame.mixer.music.load("Nice.mp3") # Use own sound track 1
pygame.mixer.music.play(-1)  # Loop the first track indefinitely
track2 = pygame.mixer.Sound("uhoh.mp3") # Use own sound track 2

# Define level data: each level has a background, Waldo's position, and time limit
levels = [
    {"background": "WW1.jpg", "waldo_position": (928, 281), "time_limit": 60},
    {"background": "WW2.jpg", "waldo_position": (378, 543), "time_limit": 60},
    {"background": "WW3.jpg", "waldo_position": (30000, 30000), "time_limit": 60} # No waldo in 3rd level, make it impossible
]

# Load and scale the background for the first level
background = pygame.image.load(levels[level]["background"])
background = pygame.transform.scale(background, (screen_width, screen_height))

# Game loop
running = True
while running:
    # Reset timer and variables for each level start
    if level < num_levels:
        waldo_position = levels[level]["waldo_position"]
        waldo_radius = 20
        timer_start = time.time()
        time_limit = levels[level]["time_limit"]
        found_waldo = False
        relay_activated = False

        # Reload and restart the Nice.mp3 track for the new level
        pygame.mixer.music.load("Nice.mp3")
        pygame.mixer.music.play(-1)  # Loop the first track indefinitely
        
        # Main game loop for the current level
        while not found_waldo and level < num_levels:
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
            if remaining_time == 0 and not relay_activated:
                arduino.write(b"activate_relay\n")
                relay_activated = True  # Prevent repeated signals

                # Display "Time's up!" message
                time_up_text = font.render("HAHAHAHHA ZAP", True, RED)
                time_up_rect = time_up_text.get_rect(center=(screen_width // 2, screen_height // 2))
                pygame.draw.rect(screen, WHITE, time_up_rect.inflate(20, 10))
                screen.blit(time_up_text, time_up_rect)
                
                pygame.display.flip()
                pygame.time.delay(3000)

                # Game over message
                screen.fill(WHITE)
                game_over_text = font.render("hahahahahah u suck", True, RED)
                game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(game_over_text, game_over_rect)
                pygame.display.flip()
                pygame.time.delay(3000)

                running = False  # Exit the game loop
                break

            # Detect mouse clicks
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    level = num_levels  # Exit all levels
                elif event.type == pygame.MOUSEBUTTONDOWN and not found_waldo:
                    mouse_x, mouse_y = event.pos
                    distance = ((mouse_x - waldo_position[0]) ** 2 + (mouse_y - waldo_position[1]) ** 2) ** 0.5

                    if distance < waldo_radius:
                        found_waldo = True

            # Display message if Waldo is found
            if found_waldo:
                # Stop the uhoh.mp3 soundtrack
                track2.stop()

                found_text = font.render("You found Waldo!", True, RED)
                found_rect = found_text.get_rect(center=(screen_width // 2, screen_height // 2))
                pygame.draw.rect(screen, WHITE, found_rect.inflate(20, 10))
                screen.blit(found_text, found_rect)
                pygame.display.flip()
                pygame.time.delay(3000)
                
                # Go to next level if not the last one
                level += 1
                if level < num_levels:
                    background = pygame.image.load(levels[level]["background"])
                    background = pygame.transform.scale(background, (screen_width, screen_height))
                break  # Exit inner loop to reset for next level

            pygame.display.flip()

    else:
        # Game end message (if you want to add something here)
        screen.fill(WHITE)
        end_text = font.render("Congratulations! You've completed all levels!", True, RED)
        end_text_rect = end_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(end_text, end_text_rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

# Clean up
arduino.close()
pygame.quit()
sys.exit()
