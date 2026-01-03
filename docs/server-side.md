# Dokumentacja Serwera

## 1. Architektura
* **Model:** Client-Server (TCP Sockets).
* **Współbieżność:** `threading` (osobny wątek dla każdego gracza).
* **Dane:** JSON (UTF-8).

## 2. Pliki
* `server.py`: Obsługa sieci. Przyjmuje JSON -> pyta logikę -> odsyła JSON.
* `game_state.py`: Czysta logika. Trzyma plansze, sprawdza kolizje i wygraną.

## 3. Protokół (Przykładowe komunikaty)

### Klient -> Serwer
* **Ruch:** `{"type": "MOVE", "direction": "UP"}`

### Serwer -> Klient
* **Start:** `{"type": "GAME_START", "turn": 0, "board_size": 10}`
* **Wynik ruchu (do autora):** `{"type": "MOVE_RESULT", "payload": {"status": "MOVED", "x": 2, "y": 3}}`
    * Statusy: `MOVED`, `WALL_HIT`, `TREASURE_FOUND`, `NOT_YOUR_TURN`.
* **Info o wrogu (do drugiego):** `{"type": "OPPONENT_ACTION", "result": {...}}`
* **Koniec:** `{"type": "GAME_OVER", "winner": 1}`

## 4. Zasady Gry (Backend)
* Plansza 10x10.
* Ruchy na zmianę.
* Serwer blokuje ruchy nie w swojej turze.