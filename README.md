# Python Planner - Aplikacja do Zarządzania Zadaniami

Planner to desktopowa aplikacja do zarządzania zadaniami, która umożliwia:
- **Dodawanie, edytowanie i usuwanie zadań** – szybkie zarządzanie listą zadań.
- **Integrację z kalendarzem** – wizualizację terminów zadań za pomocą kalendarza.
- **Oznaczanie zadań jako ukończonych** – możliwość zaznaczenia wykonanych zadań.
- **Sortowanie zadań według daty** – uporządkowanie zadań w kolejności ich wykonania.
- **Powiadomienia i system tray** – przypomnienia o zadaniach oraz szybki dostęp do najważniejszych funkcji poprzez ikonę w zasobniku systemowym.

## Funkcjonalności

- **Interfejs użytkownika:**  
  Zbudowany przy użyciu `tkinter` i `ttk`, co zapewnia przejrzysty wygląd i łatwość obsługi.
  
- **Kalendarz:**  
  Dzięki integracji z `tkcalendar`, użytkownik może przeglądać zadania w kontekście wbudowanego kalendarza, co ułatwia planowanie.
  
- **System tray:**  
  Aplikacja minimalizuje się do zasobnika systemowego, umożliwiając szybki dostęp do najbliższych zadań oraz wyświetlanie powiadomień.

- **Przechowywanie zadań:**  
  Zadania są zapisywane i odczytywane z pliku `tasks.json`, co pozwala na zachowanie danych między uruchomieniami aplikacji.

## Technologie

- **Python 3**
- **Tkinter** – budowa interfejsu graficznego.
- **tkcalendar** – obsługa kalendarza.
- **pystray** – integracja z zasobnikiem systemowym.
- **Pillow (PIL)** – operacje na obrazach.
- **JSON** – przechowywanie danych.

## Jak uruchomić

1. Sklonuj repozytorium:
    ```bash
    git clone https://github.com/Gulwe/Python-Planner
    ```
2. Zainstaluj wymagane biblioteki:
    ```bash
    pip install tkcalendar pystray pillow
    ```
3. Uruchom aplikację:
    ```bash
    python planner.py
    ```
