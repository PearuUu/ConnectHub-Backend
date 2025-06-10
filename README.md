# ConnectHub-Backend

ConnectHub-Backend to serwerowa część aplikacji służącej do zarządzania użytkownikami oraz komunikacją. Projekt oparty jest na frameworku FastAPI.

## Wymagania

- Python 3.10+
- pip

## Instalacja

1. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

## Konfiguracja

Skonfiguruj zmienne środowiskowe w pliku `.env` zgodnie z przykładem w `src/config.py`. Ustaw m.in. klucz JWT oraz dane do bazy danych.
Przykładowy plik .env:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
JWT_SECRET_KEY = "<Secret_Key>"
```

## Uruchomienie

Aby uruchomić serwer deweloperski:

```
uvicorn src.main:app --reload
```

## Struktura projektu

```
ConnectHub-Backend/
│
├── requirements.txt
├── .env
├── readme.md
└── src/
    ├── main.py
    ├── config.py
    ├── db/
    │   ├── base.py
    │   └── session.py
    ├── models/
    │   ├── user.py
    │   └── __init__.py
    ├── auth/
    │   ├── routes/
    │   │   └── auth_routes.py
    │   ├── schemas/
    │   │   ├── user.py
    │   │   ├── token_data.py
    │   │   └── __init__.py
    │   ├── utils/
    │   │   └── util.py
    │   └── __init__.py
    ├── api/
    │   ├── routes/
    │   │   └── user_routes.py
    │   └── __init__.py
    └── utils/
        └── helpers.py
```

**Opis wybranych katalogów i plików:**

- `main.py` – punkt wejścia aplikacji FastAPI
- `config.py` – konfiguracja aplikacji (np. odczyt zmiennych środowiskowych)
- `db/` – konfiguracja bazy danych, sesje, modele bazowe
- `models/` – definicje modeli ORM (np. użytkownik)
- `auth/` – moduł autoryzacji i uwierzytelniania (schematy, narzędzia, trasy)
- `api/` – główne trasy API (np. użytkownicy)
- `utils/` – pomocnicze funkcje i narzędzia
