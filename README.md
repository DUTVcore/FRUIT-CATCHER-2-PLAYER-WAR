# 🍎 FRUIT CATCHER - 2 PLAYER CHAOS

![Python](https://img.shields.io/badge/Python-3.12.8-blue?style=flat&logo=python)
![Pygame](https://img.shields.io/badge/Made%20with-Pygame-red?style=flat&logo=pygame)
![Status](https://img.shields.io/badge/Status-Completed-success)

A fun, chaotic arcade fruit-catching game built with Python and Pygame. Features distinct 2-player modes, crazy power-ups, seasonal environmental mechanics, and intense Boss fights!

---

## ✨ Key Features

* **Versatile Game Modes:** Play Solo (1 Player) or compete/co-op in the chaotic 2 Player Mode.
* **Power-up System:**
    * 🧲 **Magnet:** Automatically attracts fruits to your bucket.
    * ❄️ **Freeze:** Slows down time and falling objects.
    * 🛡️ **Shield:** Protects you from bombs for a short duration.
    * ☠️ **Poison:** Confuses the opponent (or yourself) by inverting controls.
    * 🧨 **TNT:** Explodes and clears all falling items on the screen.
* **Seasonal Environment Mechanics:** Gameplay changes every level cycle:
    * 🌸 **Spring:** Higher chance of healing items.
    * ☀️ **Summer:** Fruits fall 30% faster due to the heat.
    * 🍂 **Autumn:** Strong winds cause fruits to drift sideways (Sine wave motion).
    * ❄️ **Winter:** Icy floors create inertia/sliding physics for movement.
* **Boss Fight 🦍:** Every 4 Levels, the Gorilla Boss appears to rain down bombs. The difficulty scales the longer you survive!
* **Visual "Juice":** Includes Screen Shake impacts and Particle effects for a satisfying experience.

---

## 🎮 How to Play

### Controls
| Action | Player 1 (P1) | Player 2 (P2) |
| :--- | :---: | :---: |
| **Move** | Arrow Keys (⬅️ ➡️) | WASD Keys (A - D) |
| **Character** | Red Bucket 🔴 | Blue Bucket 🔵 |

### Rules
1.  Catch fruits to gain points and level up.
2.  Avoid **Bombs** 💣. Catching a bomb costs 1 Life (unless you have a Shield).
3.  **2-Player Mode:** If **ANY** player runs out of lives, it is **GAME OVER** immediately. The surviving player is declared the winner!

---

## 📦 Installation & Setup

### Prerequisites
* Python 3.12.8
* `pygame` library

### Installation Steps
1.  **Clone or Download the repository:**
    ```bash
    git clone https://github.com/DUTVcore/Game_baitapnhapmonnganh.git
    ```

2.  **Install dependencies:**
    ```bash
    pip install pygame
    ```

3.  **Add Assets (Important):**
    Ensure your `imgs/` folder contains the necessary PNG files (Transparent backgrounds recommended):
    * `bucket.png`, `bomb.png`, `heart.png`
    * Fruits: `apple.png`, `banana.png`, etc.
    * Items: `item_magnet.png`, `item_freeze.png`, `item_poison.png`, `item_tnt.png`
    * Boss: `boss_monkey.png`
    * Backgrounds: `bg_spring.png`, `bg_summer.png`, etc.

4.  **Run the game:**
    ```bash
    python game.py
    ```

---

## 🛠️ Project Structure

```text
Fruit-Catcher/
├── imgs/               # Images (Sprites, Backgrounds, UI)
├── sounds/             # Audio files (BGM, Sound Effects)
├── game.py             # Main game loop and logic
├── settings.py         # Configuration (Colors, Paths, Screen Size)
└── README.md           # Documentation
```

---
## License
This project was created for educational and entertainment purposes. Happy Coding And I hope you can give me a 10 XD 🚀

---

## 👥 Authors
Project developed by:
* **DUTVcore (PHAM LE NAM BINH)**
* **TranHuuLai**
