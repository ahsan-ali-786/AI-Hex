import pygame
import math
import random
import sys
import heapq
from collections import deque, defaultdict

# Initialize Pygame
pygame.init()

# Screen Settings
WIDTH, HEIGHT = 1200, 800  # Increased width for info panel
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hex Game Board with Image Obstacles")

# Colors
BACKGROUND_COLOR = (255, 255, 255)
HEX_COLOR = (255, 255, 255)  # White hexagons
BORDER_COLOR = (0, 0, 0)  # Black borders
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255)]  # Red and Blue players
PLAYER_NAMES = ["Red", "Blue"]
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow highlight for path
INFO_PANEL_COLOR = (240, 240, 240)
TEXT_COLOR = (0, 0, 0)

# Board Settings
ROWS, COLS = 8, 8  # Slightly smaller board for better gameplay
HEX_RADIUS = 25  # Size of hexagons
BOARD_OFFSET_X = 100
BOARD_OFFSET_Y = 100
INFO_PANEL_X = 800  # X position for info panel

# Game state
TURN = 0  # Player turn (0: Red, 1: Blue)
AI_PLAYER = 1  # AI plays as Blue
hex_states = {}  # (row, col) -> color
obstacles = set()  # Set of obstacle hexes
game_over = False
winner = None
bonus_move_counter = random.randint(1, 5)  # Initialize bonus move counter
bonus_move_active = False
bonus_player = None
move_count = 0

# Font setup
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
large_font = pygame.font.SysFont("Arial", 36)

# Load obstacle image and scale it
try:
    obstacle_img = pygame.image.load("obstacle.png")
    obstacle_img = pygame.transform.scale(obstacle_img, (HEX_RADIUS * 1.5, HEX_RADIUS * 1.5))
except pygame.error:
    # Create a default obstacle image if file not found
    obstacle_img = pygame.Surface((HEX_RADIUS * 1.5, HEX_RADIUS * 1.5), pygame.SRCALPHA)
    pygame.draw.circle(obstacle_img, (100, 100, 100), 
                      (HEX_RADIUS * 0.75, HEX_RADIUS * 0.75), 
                      HEX_RADIUS * 0.7)
    pygame.draw.circle(obstacle_img, (50, 50, 50), 
                      (HEX_RADIUS * 0.75, HEX_RADIUS * 0.75), 
                      HEX_RADIUS * 0.7, 3)

# Function to calculate hex corner points
def hex_corner(center_x, center_y, size, i):
    angle_deg = 60 * i
    angle_rad = math.radians(angle_deg)
    return (center_x + size * math.cos(angle_rad), center_y + size * math.sin(angle_rad))

# Function to draw hexagons
def draw_hex(x, y, row, col):
    points = [hex_corner(x, y, HEX_RADIUS, i) for i in range(6)]
    
    # Draw obstacle image
    if (row, col) in obstacles:
        screen.blit(obstacle_img, obstacle_img.get_rect(center=(x, y)))
    else:
        color = hex_states.get((row, col), HEX_COLOR)  # Default or player color
        pygame.draw.polygon(screen, color, points)

    # Draw border
    pygame.draw.polygon(screen, BORDER_COLOR, points, 2)  # Black border

# Function to get hex center coordinates
def get_hex_center(row, col):
    x = col * HEX_RADIUS * 1.5 + BOARD_OFFSET_X
    y = row * HEX_RADIUS * math.sqrt(3) + BOARD_OFFSET_Y
    # Adjust for offset rows
    if col % 2 == 1:
        y += HEX_RADIUS * math.sqrt(3) / 2
    return x, y

# Function to generate board positions
def generate_board():
    hexagons = []
    for row in range(ROWS):
        for col in range(COLS):
            x, y = get_hex_center(row, col)
            hexagons.append(((x, y), row, col))
            draw_hex(x, y, row, col)
    
    # Draw player territories (top/bottom for Red, left/right for Blue)
    for col in range(COLS):
        # Red's top territory
        pygame.draw.rect(screen, (255, 200, 200), 
                        (col * HEX_RADIUS * 1.5 + BOARD_OFFSET_X - HEX_RADIUS/2, 
                         BOARD_OFFSET_Y - HEX_RADIUS - 10, 
                         HEX_RADIUS, 10))
        # Red's bottom territory
        pygame.draw.rect(screen, (255, 200, 200), 
                        (col * HEX_RADIUS * 1.5 + BOARD_OFFSET_X - HEX_RADIUS/2, 
                         BOARD_OFFSET_Y + ROWS * HEX_RADIUS * math.sqrt(3) + HEX_RADIUS, 
                         HEX_RADIUS, 10))
    
    for row in range(ROWS):
        # Blue's left territory
        y_offset = 0
        if row % 2 == 1:
            y_offset = HEX_RADIUS * math.sqrt(3) / 2
        pygame.draw.rect(screen, (200, 200, 255), 
                        (BOARD_OFFSET_X - HEX_RADIUS - 10, 
                         row * HEX_RADIUS * math.sqrt(3) + BOARD_OFFSET_Y + y_offset - HEX_RADIUS/2, 
                         10, HEX_RADIUS))
        # Blue's right territory
        pygame.draw.rect(screen, (200, 200, 255), 
                        (BOARD_OFFSET_X + COLS * HEX_RADIUS * 1.5 + HEX_RADIUS, 
                         row * HEX_RADIUS * math.sqrt(3) + BOARD_OFFSET_Y + y_offset - HEX_RADIUS/2, 
                         10, HEX_RADIUS))
    
    return hexagons

# Function to get clicked hex
def get_clicked_hex(pos, hexagons):
    mx, my = pos
    for (hx, hy), row, col in hexagons:
        dx, dy = mx - hx, my - hy
        distance = math.sqrt(dx**2 + dy**2)
        if distance < HEX_RADIUS:
            return row, col
    return None

# Function to get neighboring hex coordinates
def get_neighbors(row, col):
    neighbors = []
    # Define the six neighbor directions
    even_row_neighbors = [(-1, 0), (-1, 1), (0, 1), (1, 0), (0, -1), (-1, -1)]
    odd_row_neighbors = [(-1, 0), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    
    directions = odd_row_neighbors if col % 2 == 1 else even_row_neighbors
    
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            neighbors.append((nr, nc))
    
    return neighbors

# Function to check if a player has won
def check_win():
    # For Red player (top to bottom)
    if has_path(0, ROWS-1):
        return 0  # Red wins
    
    # For Blue player (left to right)
    if has_path_horizontal():
        return 1  # Blue wins
    
    return None

# Function to check if the board is full (draw condition)
def check_draw():
    available_cells = ROWS * COLS - len(obstacles) - len(hex_states)
    return available_cells == 0

# BFS to check if player has a connected path
def has_path(start_edge, end_edge):
    """Check if Red player has a path from top to bottom"""
    # Create virtual nodes for the top and bottom edges
    visited = set()
    queue = deque()
    
    # Add all top-row red hexes to the queue
    for col in range(COLS):
        if hex_states.get((0, col)) == PLAYER_COLORS[0]:
            queue.append((0, col))
            visited.add((0, col))
    
    while queue:
        row, col = queue.popleft()
        
        # If we reached the bottom edge
        if row == end_edge:
            return True
        
        # Check neighbors
        for nr, nc in get_neighbors(row, col):
            if (nr, nc) not in visited and hex_states.get((nr, nc)) == PLAYER_COLORS[0]:
                visited.add((nr, nc))
                queue.append((nr, nc))
    
    return False

def has_path_horizontal():
    """Check if Blue player has a path from left to right"""
    visited = set()
    queue = deque()
    
    # Add all left-column blue hexes to the queue
    for row in range(ROWS):
        if hex_states.get((row, 0)) == PLAYER_COLORS[1]:
            queue.append((row, 0))
            visited.add((row, 0))
    
    while queue:
        row, col = queue.popleft()
        
        # If we reached the right edge
        if col == COLS - 1:
            return True
        
        # Check neighbors
        for nr, nc in get_neighbors(row, col):
            if (nr, nc) not in visited and hex_states.get((nr, nc)) == PLAYER_COLORS[1]:
                visited.add((nr, nc))
                queue.append((nr, nc))
    
    return False

# Draw information panel
def draw_info_panel():
    panel_width = WIDTH - INFO_PANEL_X
    
    # Draw panel background
    pygame.draw.rect(screen, INFO_PANEL_COLOR, (INFO_PANEL_X, 0, panel_width, HEIGHT))
    pygame.draw.line(screen, BORDER_COLOR, (INFO_PANEL_X, 0), (INFO_PANEL_X, HEIGHT), 2)
    
    # Game title
    title = large_font.render("HEX GAME", True, TEXT_COLOR)
    screen.blit(title, (INFO_PANEL_X + 20, 20))
    
    # Game instructions
    instructions = [
        "Instructions:",
        "- Players take turns placing pieces on the board",
        "- Red connects from top to bottom",
        "- Blue connects from left to right",
        "- First player to form a continuous path wins",
        "- If board fills up with no winner, it's a draw",
        "- Obstacles cannot be occupied",
        "",
        "Bonus Move:",
        f"- After {bonus_move_counter} moves, current player gets an extra turn",
        "",
        "Controls:",
        "- Click on a hex to place your piece",
        "- Press 'R' to restart the game",
        "- Press 'ESC' to exit"
    ]
    
    y_offset = 80
    for line in instructions:
        text = small_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (INFO_PANEL_X + 20, y_offset))
        y_offset += 25
    
    # Game status
    y_offset = 500
    pygame.draw.line(screen, BORDER_COLOR, (INFO_PANEL_X + 10, y_offset - 10), 
                     (WIDTH - 10, y_offset - 10), 2)
    
    # Current turn
    current_player = "Bonus: " + PLAYER_NAMES[bonus_player] if bonus_move_active else PLAYER_NAMES[TURN]
    turn_text = font.render(f"Current Turn: {current_player}", True, PLAYER_COLORS[bonus_player if bonus_move_active else TURN])
    screen.blit(turn_text, (INFO_PANEL_X + 20, y_offset))
    
    # Moves until bonus
    if not bonus_move_active:
        moves_left = bonus_move_counter - (move_count % bonus_move_counter)
        if moves_left == 0:
            moves_left = bonus_move_counter
        bonus_text = font.render(f"Moves until bonus: {moves_left}", True, TEXT_COLOR)
        screen.blit(bonus_text, (INFO_PANEL_X + 20, y_offset + 40))
    else:
        bonus_text = font.render("BONUS MOVE ACTIVE!", True, HIGHLIGHT_COLOR)
        screen.blit(bonus_text, (INFO_PANEL_X + 20, y_offset + 40))
    
    # Game status
    if game_over:
        if winner is not None:
            status = font.render(f"Game Over! {PLAYER_NAMES[winner]} wins!", True, PLAYER_COLORS[winner])
        else:
            status = font.render("Game Over! It's a draw!", True, TEXT_COLOR)
        screen.blit(status, (INFO_PANEL_X + 20, y_offset + 80))

# Draw winner or draw dialog
def draw_game_end_dialog():
    dialog_width, dialog_height = 400, 200
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    
    # Draw dialog background with shadow
    pygame.draw.rect(screen, (100, 100, 100), 
                    (dialog_x + 5, dialog_y + 5, dialog_width, dialog_height))
    pygame.draw.rect(screen, (220, 220, 220), 
                    (dialog_x, dialog_y, dialog_width, dialog_height))
    pygame.draw.rect(screen, BORDER_COLOR, 
                    (dialog_x, dialog_y, dialog_width, dialog_height), 3)
    
    # Result text
    if winner is not None:
        result_text = large_font.render(f"{PLAYER_NAMES[winner]} WINS!", True, PLAYER_COLORS[winner])
    else:
        result_text = large_font.render("IT'S A DRAW!", True, TEXT_COLOR)
    text_rect = result_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 70))
    screen.blit(result_text, text_rect)
    
    # Instruction text
    instruction = font.render("Press 'R' to restart or 'ESC' to quit", True, TEXT_COLOR)
    inst_rect = instruction.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 130))
    screen.blit(instruction, inst_rect)

# AI Player with Alpha-Beta Pruning
def evaluate_board(player):
    """Evaluate the current board state for the given player"""
    # Simple heuristic: calculate shortest path length
    if player == 0:  # Red player (top to bottom)
        return -shortest_path_length(0)  # Negative because shorter is better
    else:  # Blue player (left to right)
        return -shortest_path_length(1)  # Negative because shorter is better

def shortest_path_length(player):
    """Calculate the shortest path length for a player"""
    if player == 0:  # Red (top to bottom)
        start_points = [(0, col) for col in range(COLS)]
        end_points = [(ROWS-1, col) for col in range(COLS)]
    else:  # Blue (left to right)
        start_points = [(row, 0) for row in range(ROWS)]
        end_points = [(row, COLS-1) for row in range(ROWS)]
    
    # Create graph with hex cells as nodes
    graph = defaultdict(list)
    
    # Add edges between hexes
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) in hex_states and hex_states[(row, col)] != PLAYER_COLORS[player]:
                continue  # Skip opponent's hexes and obstacles
            for nr, nc in get_neighbors(row, col):
                if (nr, nc) in obstacles:
                    continue
                if (nr, nc) in hex_states and hex_states[(nr, nc)] != PLAYER_COLORS[player]:
                    continue
                # Weight: 0 for player's cells, 1 for empty cells
                weight = 0 if (row, col) in hex_states and hex_states[(row, col)] == PLAYER_COLORS[player] else 1
                graph[(row, col)].append(((nr, nc), weight))
    
    # Find shortest path using Dijkstra's algorithm
    min_dist = float('inf')
    
    for start in start_points:
        if start in obstacles or (start in hex_states and hex_states[start] != PLAYER_COLORS[player]):
            continue
            
        # Distances dict
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_dist, current_node = heapq.heappop(priority_queue)
            
            if current_dist > distances[current_node]:
                continue
                
            for neighbor, weight in graph[current_node]:
                distance = current_dist + weight
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        # Check all end points
        for end in end_points:
            if end in distances and distances[end] < min_dist:
                min_dist = distances[end]
    
    return min_dist if min_dist != float('inf') else 1000  # Large value if no path

def get_valid_moves():
    """Get all valid moves on the board"""
    valid_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) not in hex_states and (row, col) not in obstacles:
                valid_moves.append((row, col))
    return valid_moves

def alpha_beta_search(depth, player):
    """Alpha-Beta pruning to find best move"""
    def max_value(state, alpha, beta, depth, player):
        if depth == 0:
            return evaluate_board(player), None
        
        v = float('-inf')
        move = None
        for r, c in get_valid_moves():
            # Make move
            hex_states[(r, c)] = PLAYER_COLORS[player]
            
            # Get value
            v2, _ = min_value(state, alpha, beta, depth - 1, player)
            
            # Undo move
            del hex_states[(r, c)]
            
            if v2 > v:
                v = v2
                move = (r, c)
            
            if v >= beta:
                return v, move
            
            alpha = max(alpha, v)
        
        return v, move
    
    def min_value(state, alpha, beta, depth, player):
        if depth == 0:
            return evaluate_board(player), None
        
        v = float('inf')
        move = None
        opponent = 1 - player
        for r, c in get_valid_moves():
            # Make move
            hex_states[(r, c)] = PLAYER_COLORS[opponent]
            
            # Get value
            v2, _ = max_value(state, alpha, beta, depth - 1, player)
            
            # Undo move
            del hex_states[(r, c)]
            
            if v2 < v:
                v = v2
                move = (r, c)
            
            if v <= alpha:
                return v, move
            
            beta = min(beta, v)
        
        return v, move
    
    # Start alpha-beta search
    _, move = max_value(hex_states, float('-inf'), float('inf'), depth, player)
    return move

def ai_make_move():
    """AI makes a move using alpha-beta pruning"""
    depth = 2  # Adjust depth based on performance
    move = alpha_beta_search(depth, AI_PLAYER)
    
    if move:
        hex_states[move] = PLAYER_COLORS[AI_PLAYER]
        return True
    return False

# Randomly place obstacles
NUM_OBSTACLES = min(8, int(ROWS * COLS * 0.05))  # Adjust based on board size
all_positions = [(r, c) for r in range(ROWS) for c in range(COLS)]
# Skip edges for obstacles to ensure players can make connections
edge_positions = set()
for r in range(ROWS):
    edge_positions.add((r, 0))
    edge_positions.add((r, COLS-1))
for c in range(COLS):
    edge_positions.add((0, c))
    edge_positions.add((ROWS-1, c))
valid_obstacle_positions = [pos for pos in all_positions if pos not in edge_positions]
obstacles = set(random.sample(valid_obstacle_positions, NUM_OBSTACLES))

# Main loop
running = True
clock = pygame.time.Clock()

def restart_game():
    global hex_states, game_over, winner, TURN, bonus_move_counter, bonus_move_active
    global bonus_player, move_count
    
    hex_states = {}
    game_over = False
    winner = None
    TURN = 0
    # Fix bug with bonus_move_counter - ensure it gets a new random value
    bonus_move_counter = random.randint(1, 5)
    bonus_move_active = False
    bonus_player = None
    move_count = 0

while running:
    screen.fill(BACKGROUND_COLOR)
    hex_positions = generate_board()
    draw_info_panel()
    
    # If game is over, draw game end dialog
    if game_over:
        draw_game_end_dialog()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                restart_game()
                # Regenerate obstacles
                obstacles = set(random.sample(valid_obstacle_positions, NUM_OBSTACLES))

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if TURN != AI_PLAYER or bonus_move_active and bonus_player != AI_PLAYER:
                clicked_hex = get_clicked_hex(pygame.mouse.get_pos(), hex_positions)
                if clicked_hex and clicked_hex not in hex_states and clicked_hex not in obstacles:
                    current_player = bonus_player if bonus_move_active else TURN
                    hex_states[clicked_hex] = PLAYER_COLORS[current_player]
                    
                    # Check for win
                    winner = check_win()
                    if winner is not None:
                        game_over = True
                    # Check for draw (if board is full)
                    elif check_draw():
                        game_over = True
                        winner = None  # Draw condition
                    else:
                        # Handle bonus move logic
                        if bonus_move_active:
                            # Fix bug - generate a new random bonus_move_counter
                            # Don't use random.seed() as it can produce the same result
                            bonus_move_counter = random.randint(1, 5)
                            bonus_move_active = False
                            TURN = 1 - bonus_player  # Next turn after bonus
                        else:
                            move_count += 1
                            # Check if it's time for a bonus move
                            if move_count % bonus_move_counter == 0:
                                bonus_move_active = True
                                bonus_player = TURN  # Current player gets a bonus
                            else:
                                TURN = 1 - TURN  # Switch turn
    
    # AI's turn
    if not game_over and (TURN == AI_PLAYER and not bonus_move_active or 
                         bonus_move_active and bonus_player == AI_PLAYER):
        ai_made_move = ai_make_move()
        
        if ai_made_move:
            # Check for win
            winner = check_win()
            if winner is not None:
                game_over = True
            # Check for draw (if board is full)
            elif check_draw():
                game_over = True
                winner = None  # Draw condition
            else:
                # Handle bonus move logic
                if bonus_move_active:
                    # Fix bug - generate a new random bonus_move_counter
                    bonus_move_counter = random.randint(1, 5)
                    bonus_move_active = False
                    TURN = 1 - bonus_player  # Next turn after bonus
                else:
                    move_count += 1
                    # Check if it's time for a bonus move
                    if move_count % bonus_move_counter == 0:
                        bonus_move_active = True
                        bonus_player = TURN  # Current player gets a bonus
                    else:
                        TURN = 1 - TURN  # Switch turn
    
    pygame.display.flip()
    clock.tick(60)  # Cap at 60 FPS

pygame.quit()
sys.exit()