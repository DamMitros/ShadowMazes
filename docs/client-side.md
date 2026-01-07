# Dokumentacja Klienta

## 1. Architektura (Wzorzec MVC)
Aplikacja kliencka została zrefaktoryzowana do wzorca **Model-View-Controller (MVC)**, co zapewnia czytelność i łatwość rozbudowy.

### Struktura modułów:

* **Model (Dane):**
    * `state.py`: Przechowuje pełny stan rozgrywki (plansze, tury, punkty ruchu, flagi zakończenia gry). Jest niezależny od interfejsu graficznego.

* **View (Widok):**
    * `board.py`: Odpowiada za renderowanie siatki gry (Canvas), ścian i pionków.
    * `screens.py`: Zarządza nakładkami interfejsu (Lobby, Game Over, Connection Lost). Oddziela logikę budowania okien od logiki gry.

* **Controller (Sterowanie):**
    * `gui.py`: Główny koordynator. Spina Model z Widokiem, odbiera zdarzenia sieciowe i aktualizuje UI.
    * `input_handler.py`: Mapuje zdarzenia klawiatury na polecenia sieciowe.
    * `client.py`: Warstwa sieciowa działająca w osobnym wątku.

## 2. Interfejs Użytkownika (GUI)
Interfejs podzielony jest na trzy główne sekcje:

* **Defense Sector** (Lewa strona): Wyświetla pełną mapę gracza.
* **Attack Radar** (Środek): Wyświetla mapę przeciwnika.
* **Chat & Log** (Prawa strona): Historia zdarzeń i komunikator.

## 3. Obsługa Współbieżności
Ze względu na specyfikę biblioteki `tkinter`, komunikacja sieciowa odbywa się w tle. Metody aktualizujące interfejs są wywoływane bezpiecznie poprzez `root.after()`.

## 4. Wymagania
* Python 3.x
* Biblioteki z `requirements.txt`