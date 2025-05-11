# Hex Game

A Python implementation of the classic board game Hex with bonus moves and obstacle features.

![Hex Game Screenshot](https://github.com/ahsan-ali-786/AI-Hex/blob/main/image.png)

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Game Rules](#game-rules)
- [Controls](#controls)
- [AI Implementation](#ai-implementation)
- [Customization](#customization)

## Description

Hex is a strategy board game played on a hexagonal grid. This implementation features a customizable board size, an AI opponent using Alpha-Beta pruning, random obstacles, and a bonus move mechanic for added strategic depth.

## Features

- Hexagonal game board with customizable dimensions
- Human vs AI gameplay
- Obstacles that cannot be occupied
- Bonus move mechanic that gives players an extra turn at random intervals
- Visual representation of player territories and winning paths
- Information panel with game status and instructions
- Game state tracking (wins, draws)
- Alpha-Beta pruning AI for intelligent opponent play

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ahsan-ali-786/AI-Hex.git
cd AI-Hex
```

2. Install dependencies:

```bash
pip install pygame numpy
```

3. Run the game:

```bash
python hex.py
```

## How to Play

In Hex, the goal is to create a continuous path of your pieces connecting your two sides of the board:

- Red player connects from top to bottom
- Blue player connects from left to right

## Game Rules

1. Players take turns placing pieces on the board
2. Red aims to create a path from top to bottom
3. Blue aims to create a path from left to right
4. A cell occupied by a player cannot be taken by the opponent
5. Obstacles (randomly placed at the start) cannot be occupied
6. After a specific number of moves (randomly determined), the current player gets a bonus move
7. The game ends when one player completes a path or the board is full (draw)

## Controls

- **Left Click**: Place your piece on an empty hex
- **R**: Restart the game with a new obstacle layout
- **ESC**: Quit the game

## AI Implementation

The AI opponent uses Alpha-Beta pruning with a heuristic based on shortest path calculations:

1. The AI evaluates the board state by calculating the shortest path from its starting edge to its goal edge
2. It uses Dijkstra's algorithm to find this path, considering opponent pieces as blocked cells
3. The Alpha-Beta pruning search looks ahead several moves to find the optimal placement
4. The search depth can be adjusted in the code for different difficulty levels

## Customization

You can customize several game parameters in the code:

- `ROWS` and `COLS`: Change the board dimensions
- `HEX_RADIUS`: Adjust the size of hexagons
- `NUM_OBSTACLES`: Modify the number of obstacles
- Search `depth` in the `ai_make_move()` function: Change AI difficulty

To customize the game's appearance:

- Modify the color constants at the beginning of the code
- Replace the default obstacle image with your own by placing an "obstacle.png" file in the same directory

---

Created by [ahsan-ali-786, SyedAbdullah10]
