# Shadow Mazes

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Architecture](https://img.shields.io/badge/Architecture-Client--Server-green?style=flat-square)
![Protocol](https://img.shields.io/badge/Protocol-TCP%2FJSON-orange?style=flat-square)

## Project Overview

**Shadow Mazes** is a concurrent, turn-based multiplayer game implemented in Python. The project demonstrates the practical application of network programming using raw TCP sockets and multi-threading without relying on high-level web frameworks.

The core gameplay revolves on asymmetric visibility mechanics. Two players compete on 10x10 grids to find a hidden treasure within a randomly generated maze. The client application utilizes the **Model-View-Controller (MVC)** pattern to ensure separation of concerns between the networking logic and the graphical user interface.

## Technical Architecture

The system is built upon a robust Client-Server architecture:

### 1. Server-Side
* **Concurrency Model:** The server is multi-threaded. It assigns a dedicated thread (`threading.Thread`) for each connected client, allowing simultaneous communication.
* **State Management:** The game state (player positions, maze layouts, turn logic) is centralized on the server to prevent cheating. Access to shared resources is synchronized using `threading.Lock` to prevent race conditions.
* **Fault Tolerance:** The server detects unexpected disconnections (e.g., socket closure) and automatically handles "walkover" victories to maintain game integrity.

### 2. Client-Side
* **MVC Pattern:**
    * **Model:** `state.py` manages the local game state (energy, board data).
    * **View:** `board.py` and `gui.py` handle rendering using the Tkinter canvas.
    * **Controller:** `input_handler.py` processes user input and dispatches network events.
* **Non-Blocking UI:** Network communication runs in a separate background thread to ensure the GUI remains responsive while waiting for server packets.

### 3. Communication Protocol
Data exchange is performed via a custom, stateless application-layer protocol using JSON payloads over TCP.
* **Request:** `MOVE`, `CHAT`
* **Response:** `MOVE_RESULT`, `OPPONENT_ACTION`, `GAME_START`, `GAME_OVER`

## Game Mechanics

The game enforces specific rules validated by the server:

1.  **Map Generation:** Procedural generation guarantees a valid path of exactly 30 steps from start to treasure.
2.  **Asymmetric Information:**
    * **Defense Sector:** Displays the player's own maze and the opponent's current position (passive view).
    * **Attack Radar:** Displays the opponent's maze. Initially shrouded in darkness, tiles are revealed only upon exploration.
3.  **Turn System:** Players act in turns with a limit of **5 energy points** per turn. A collision with a wall immediately ends the current turn.

## Installation and Execution

The project relies solely on the Python Standard Library (no external `pip` dependencies required).

### Prerequisites
* Python 3.6+

### 1. Clone the Repository
```bash
git clone [https://github.com/DamMitros/ShadowMazes.git](https://github.com/DamMitros/ShadowMazes.git)
cd shadow-mazes
```

### 2. Start the Server
Initialize the server instance to listen for incoming connections.
```bash
python server/server.py
```
*Default configuration: Host `127.0.0.1`, Port `65432`.*

### 3. Start Clients
Launch two separate client instances to simulate a match.
```bash
python client/gui.py
```
*(Repeat this step in a second terminal for Player 2)*

## Controls

The interface is optimized for keyboard navigation.

| Key | Function |
| :--- | :--- |
| **Arrow Keys** | Select movement direction (Plan move) |
| **Spacebar** | Confirm and execute the selected move |
| **Enter** | Send a chat message |

## Project Structure

```text
shadow-mazes/
├── client/             # Client-side application (MVC)
│   ├── gui.py          # Entry point & Main Window
│   ├── board.py        # Canvas rendering logic
│   ├── client.py       # Network socket wrapper
│   └── state.py        # Local game state storage
├── server/             # Server-side application
│   ├── server.py       # Connection handling & Threading
│   ├── request_handler.py # Protocol processing logic
│   └── game_state.py   # Game rules & Validation
├── common/             # Shared resources
│   ├── constants.py    # Configuration (Ports, Colors, Sizes)
│   └── protocol.py     # Protocol definitions
└── docs/               # Documentation
```

---

**Author:** Damian Mitros
