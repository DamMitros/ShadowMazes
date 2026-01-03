# Dokumentacja Klienta

## 1. Architektura
Struktura modułów:

* `gui.py` **(View/Manager)**: Główny punkt wejścia. Inicjalizuje okno tkinter, układa widgety i zarządza stanem UI. Łączy pozostałe komponenty.
* `client.py` **(Networking)**: Obsługuje gniazda TCP. Działa na osobnym wątku (threading), aby nie blokować interfejsu graficznego. Przekazuje przychodzące pakiety JSON do GUI za pomocą callbacków.
* `board.py` **(Renderer)**: Klasa statyczna odpowiedzialna wyłącznie za rysowanie na obiekcie tk.Canvas. Nie przechowuje stanu gry.
* `input_handler.py` **(Controller)**: Mapuje zdarzenia klawiatury (Strzałki, Enter) na żądania sieciowe (wysłanie ruchu, wysłanie wiadomości).

## 2. Interfejs Użytkownika (GUI)
Interfejs podzielony jest na trzy główne sekcje:

* **Defense Sector** (Lewa strona): Wyświetla pełną mapę gracza. Pokazuje pozycję startową przeciwnika oraz własny skarb.
* **Attack Radar** (Środek): Wyświetla mapę przeciwnika pokrytą mgłą wojny (Fog of War). Odkrywa teren w miarę poruszania się gracza.

  * Kolor czarny: Teren nieznany.
  * Kolor fioletowy: Odkryta ścieżka.
  * Kolor czerwony: Odkryta ściana.

* **Chat & Log** (Prawa strona): Historia zdarzeń systemowych oraz komunikator tekstowy między graczami.

## 3.  Obsługa Współbieżności

Ze względu na specyfikę `tkinter` (który musi działać w głównym wątku), komunikacja sieciowa została wyniesiona do wątku pobocznego.

* Metody `gui.py` używają ```root.after(0, callback)```, aby bezpiecznie aktualizować interfejs graficzny w odpowiedzi na zdarzenia z wątku sieciowego (Thread Safety).

## 4. Wymagania

* Python 3.x
* `requirements.txt`