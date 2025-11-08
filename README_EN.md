# 🎮 Snake AI Game

[简体中文](README.md) | English

<div align="center">
  <img src="http://vincentcassano.cn/upload/vimeo-v-blue.png" alt="Snake AI Game" style="border-radius: 10px; max-width: 60px;">
  <p style="color: #666; font-style: italic;">A feature-rich Snake game with intelligent AI opponents and multiple game modes</p>
</div>

## 📋 Project Introduction
This is a carefully designed enhanced version of the classic Snake game, incorporating intelligent AI opponent systems and multiple game modes. Developed in Python and built with Pygame library, the game features a beautiful graphical interface, rich gameplay experience, flexible customization options, and immersive sound effects. Whether you're a casual player or looking to challenge AI, you'll find enjoyment here.

## ✨ Game Features

### 🎮 Multiple Game Modes
- **Classic Mode**: Traditional Snake gameplay, control the snake to collect food and grow longer, challenging for the highest score
- **VS Mode**: Real-time battle against AI-controlled snakes, see who survives longer or achieves higher scores
- **Time Attack Mode**: Quick challenge within 60 seconds, intense and exciting, aiming for the highest score

### 🧠 Intelligent AI System
- AI opponents based on advanced pathfinding and decision algorithms
- Adjustable AI difficulty levels (Easy, Medium, Hard) to suit different player skills
- AI can perceive environment, plan paths, and make strategic moves, providing a realistic competitive experience

### 🎨 Beautiful Visual Effects
- Gradient background design for comfortable visual experience
- Smooth snake movement and animation effects for enhanced gameplay fluidity
- Intuitive and friendly UI interface, including game menu, settings panel, and help interface
- Full support for Chinese font display, ensuring clear readability of in-game text

### 🔊 Immersive Sound Effects
- Food collection sound effects for instant feedback
- Countdown sound effects to increase game tension
- Game over sound effects to enhance gameplay experience
- Sound effects can be flexibly turned on or off in settings

### ⚙️ Rich Customization Options
- **Board Size**: Freely adjust the size of the game board to suit different screens
- **Cell Size**: Adjust the pixel size of each grid cell for optimized visual effects
- **Snake Speed**: Customize snake movement speed, from casual to extreme challenges
- **Food Value**: Set the base score for each food, changing game strategy
- **Border Settings**: Toggle game boundary collision detection, experience borderless mode
- **AI Difficulty**: Flexibly set AI opponent difficulty levels, suitable for beginners to experts

### 📖 Detailed Game Help
- Complete operation guide for quick start
- Clear game rule explanations to understand all gameplay
- Practical shortcut key hints to improve operation efficiency
- Mode selection help to choose the most suitable gaming experience

## 📦 Installation Instructions

### 💻 System Requirements
- **Python Version**: 3.6 or higher
- **Operating System**: Pygame-supported operating systems (Windows, macOS, Linux)
- **Hardware Requirements**: Basic graphics display capability and processing performance
- **Audio Device**: Optional, for experiencing game sound effects

### 🚀 Quick Start
1. **Clone or download the repository**
   ```bash
   git clone https://github.com/VincentCassano/SnakeAI_Game.git
   cd snakeAI_Game
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/
   ```

3. **Start the game**
   ```bash
   python snakeAI_Game-v1.0.5.py
   ```

## 🎯 Usage Guide

### 🏠 Main Menu Operations
After starting the game, you will enter the graphical main menu directly. You can:
- Press **Number Key 1**: Enter Classic Mode
- Press **Number Key 2**: Enter VS Mode (Battle with AI)
- Press **Number Key 3**: Enter Time Attack Mode
- Press **Number Key 5**: Open Game Settings Panel
- Press **Number Key 6**: View Game Help and Tutorial
- Press **ESC Key** or **q Key**: Exit the game

### 🎮 Game Controls
During gameplay, you can use the following keys to control the snake's movement:
- **Arrow Keys** (Up, Down, Left, Right): Control the snake's moving direction
- **WASD Keys**: Alternative control method, also controlling the snake's moving direction
<!-- - **Space Key**: Pause or continue the game
- **ESC Key**: Return to main menu -->

## 📜 Detailed Game Rules

### 🎯 Basic Rules
1. Control the snake to move on the board, eating randomly appearing food
2. Each food eaten makes the snake grow longer and gain corresponding scores
3. The snake cannot hit the game boundaries (unless borders are turned off in settings)
4. The snake cannot hit its own body
5. Hitting boundaries or its own body will result in game over

### 🆚 Mode-Specific Rules

#### VS Mode
- You and AI-controlled snakes move simultaneously on the board
- You can gain advantages by eating food or making AI snakes hit obstacles
- The last surviving player wins, or if both survive, the one with higher score wins

#### Time Attack Mode
- Game countdown is 60 seconds
- Try to get as many points as possible before time ends
- Snake movement speed gradually increases as score increases, adding challenge
- After time ends, final score and ranking are displayed

#### Shadow Mode
- AI snakes completely mimic the player's movement and body length, AI is the shadow
- If AI dies, player also dies

## ⚙️ Game Settings Guide
In the settings interface, you can adjust the following options:

1. **Board Size**: Adjust the size of the game board (default 40)
2. **Cell Size**: Adjust the pixel size of each grid cell (default 20)
3. **Snake Speed**: Adjust snake movement speed, smaller values mean faster speed (default 0.10 seconds/step)
4. **Food Value**: Set the base score for each food (default 1)
5. **Enable Sound Effects**: Toggle sound effects on/off (default on)
6. **Enable Borders**: Toggle game boundary collision detection on/off (default on)
7. **AI Difficulty**: Set AI opponent difficulty level (Easy, Medium, Hard) (default Medium)

**Note**: Some settings require restarting the game to take effect.

## 📁 Project Directory Structure
```
snakeAI_Game-v1.0.0/
├── requirements.txt         # Project dependencies file
├── snakeAI_Game-v1.0.1.py   # Historical version of the game
├── snakeAI_Game-v1.0.2.py   # Historical version of the game
├── snakeAI_Game-v1.0.3.py   # Historical version of the game
├── snakeAI_Game-v1.0.4.py   # Historical version of the game
├── snakeAI_Game-v1.0.5.py   # Main game program (latest version)
├── sound/                   # Sound effects resource directory
│   ├── count.wav           # Countdown sound effect
│   ├── eat.wav             # Food eating sound effect
│   └── game_over.wav       # Game over sound effect
├── icon.png                 # Game icon
└── user_game_main.py        # Project file
```

## 🛠️ Technology Stack
- **Programming Language**: Python 3
- **Graphics Library**: Pygame 2.0+
- **Mathematical Calculation**: NumPy 1.20+
- **UI Design**: Custom Pygame interface

## 📊 Version History
- **v1.0.5**: Latest version, includes all features and optimizations
- **v1.0.4**: Intermediate iteration version
- **v1.0.3**: Intermediate iteration version
- **v1.0.2**: Intermediate iteration version
- **v1.0.1**: Early version

## 🤝 Contribution Guide
Contributions to this project are welcome! You can:
- Submit Issues to report bugs or suggest features
- Submit Pull Requests to improve code or add new features
- Provide translations or improvements to documentation

## 📄 License
This project is licensed under the MIT License.

## 🎉 Acknowledgements
Thank you to all developers and players who have provided help and support for this project!