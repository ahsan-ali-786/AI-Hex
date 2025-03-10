# import pygame
# import math

# # Initialize Pygame
# pygame.init()

# # Screen Settings
# WIDTH, HEIGHT = 1000, 800
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Hex Game Board")

# # Board Settings
# ROWS, COLS = 15, 15  # Standard Hex size
# HEX_RADIUS = 25  # Size of a hexagon
# BACKGROUND_COLOR = (255, 255, 255)
# HEX_COLOR = (255, 255, 255)  # White hexagons
# BORDER_COLOR = (0, 0, 0)  # Black borders
# PLAYER_COLORS = [(255, 0, 0), (0, 0, 255)]  # Red and Blue
# TURN = 0  # Player turn (0: Red, 1: Blue)

# # Store hexagon states
# hex_states = {}  # (row, col) -> color

# # Function to calculate hex corner points
# def hex_corner(center_x, center_y, size, i):
#     angle_deg = 60 * i
#     angle_rad = math.radians(angle_deg)
#     return (center_x + size * math.cos(angle_rad), center_y + size * math.sin(angle_rad))

# # Function to draw hexagons
# def draw_hex(x, y, row, col):
#     color = hex_states.get((row, col), HEX_COLOR)  # Get current hex color
#     points = [hex_corner(x, y, HEX_RADIUS, i) for i in range(6)]
#     pygame.draw.polygon(screen, color, points)
#     pygame.draw.polygon(screen, BORDER_COLOR, points, 2)  # Black border

# # Function to generate board positions
# def generate_board():
#     hexagons = []
#     for row in range(ROWS):
#         for col in range(COLS):
#             x = col * HEX_RADIUS * 1.5 + 100  # Offset by 100 for margin
#             y = row * HEX_RADIUS * math.sqrt(3) + (col % 2) * HEX_RADIUS * math.sqrt(3) / 2 + 100
#             hexagons.append(((x, y), row, col))
#             draw_hex(x, y, row, col)
#     return hexagons

# # Function to get clicked hex
# def get_clicked_hex(pos, hexagons):
#     mx, my = pos
#     for (hx, hy), row, col in hexagons:
#         dx, dy = mx - hx, my - hy
#         distance = math.sqrt(dx**2 + dy**2)
#         if distance < HEX_RADIUS:
#             return row, col
#     return None

# # Main loop
# running = True
# while running:
#     screen.fill(BACKGROUND_COLOR)
#     hex_positions = generate_board()
    
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#             clicked_hex = get_clicked_hex(pygame.mouse.get_pos(), hex_positions)
#             if clicked_hex and clicked_hex not in hex_states:  # Check if empty
#                 hex_states[clicked_hex] = PLAYER_COLORS[TURN]  # Assign color
#                 TURN = 1 - TURN  # Switch turn

#     pygame.display.flip()

# pygame.quit()

import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen Settings
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Board with Random Crosses")

# Board Settings
ROWS, COLS = 11, 11  # Standard Hex board size
HEX_RADIUS = 35  # Size of hexagons
BORDER_COLOR = (0, 0, 0)  # Black border
BACKGROUND_COLOR = (255, 255, 255)  # White background
HEX_COLOR = (255, 255, 255)  # White hexagons
NUM_CROSSES = 8  # Number of random crosses

# Load and scale cross image
# Load image with transparency
cross_img = pygame.image.load("obstacle.png")
cross_img = pygame.transform.scale(cross_img, (HEX_RADIUS * 1.2, HEX_RADIUS * 1.2))  # Scale to fit hex

# Function to calculate hex corners
def hex_corner(center_x, center_y, size, i):
    angle_deg = 60 * i
    angle_rad = math.radians(angle_deg)
    return (center_x + size * math.cos(angle_rad), center_y + size * math.sin(angle_rad))

# Function to draw hexagon
def draw_hex(x, y):
    points = [hex_corner(x, y, HEX_RADIUS, i) for i in range(6)]
    pygame.draw.polygon(screen, HEX_COLOR, points)
    pygame.draw.polygon(screen, BORDER_COLOR, points, 2)

# Generate hex positions
hex_positions = []
for row in range(ROWS):
    for col in range(COLS):
        x = col * HEX_RADIUS * 1.5 + 100
        y = row * HEX_RADIUS * math.sqrt(3) + (col % 2) * HEX_RADIUS * math.sqrt(3) / 2 + 100
        hex_positions.append((x, y))

# Select 8 unique random positions for crosses
cross_positions = random.sample(hex_positions, NUM_CROSSES)

# Main loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    # Draw hex board
    for hx, hy in hex_positions:
        draw_hex(hx, hy)

    # Draw crosses at random positions
    for cx, cy in cross_positions:
        img_rect = cross_img.get_rect(center=(cx, cy))
        screen.blit(cross_img, img_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
