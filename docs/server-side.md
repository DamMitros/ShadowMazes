# Dokumentacja Serwera

## 1. Architektura
Serwer oparty jest na zasadzie **Separation of Concerns** (Rozdziału Odpowiedzialności).

### Struktura modułów:
* `server.py` **(Connection Layer)**: Zarządza gniazdami (Sockets), wątkami klientów i cyklem życia serwera. Nie zawiera logiki biznesowej gry.
* `request_handler.py` **(Logic Layer)**: Przetwarza przychodzące pakiety JSON. Decyduje o tym, jak obsłużyć ruch, czat czy rozłączenie.
* `game_state.py` **(Domain Layer)**: Zawiera czystą logikę gry (generowanie map, walidacja ruchów, sprawdzanie warunków zwycięstwa).

## 2. Współbieżność i Bezpieczeństwo
* **Threading**: Każdy gracz obsługiwany jest przez osobny wątek.
* **Synchronizacja**: Dostęp do współdzielonego stanu gry chroniony jest przez `threading.Lock()`, co zapobiega wyścigom (Race Conditions).
* **Deadlock Prevention**: Zastosowano architekturę metod prywatnych (`_broadcast_internal`) i publicznych (`broadcast`), aby uniknąć zakleszczeń przy rekurencyjnym wywoływaniu blokad.

## 3. Protokół (JSON)
Komunikacja odbywa się bezstanowo za pomocą obiektów JSON.

### Przykładowy przepływ (Ruch):
1. **Klient**: `{"type": "MOVE", "direction": "UP"}`
2. **Serwer (Handler)**: Waliduje ruch w `game_state.py`.
3. **Serwer**: Odsyła `MOVE_RESULT` do autora i `OPPONENT_ACTION` do przeciwnika.

## 4. Mechanizmy Specjalne
* **Walkower**: Serwer automatycznie wykrywa nagłe rozłączenie gracza i przyznaje zwycięstwo walkowerem pozostałemu uczestnikowi.
* **Lobby**: Mechanizm oczekiwania na podłączenie dwóch graczy przed startem rundy.