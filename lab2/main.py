import json
from pathlib import Path


def wczytaj_baze(nazwa_pliku="baza.json"):
    """Wczytuje pytania i reguły z pliku JSON."""
    sciezka = Path(__file__).with_name(nazwa_pliku)
    with sciezka.open("r", encoding="utf-8") as plik:
        return json.load(plik)


def zadaj_pytanie(numer, pytanie):
    """Wyświetla pytanie i pilnuje, aby odpowiedź była jedną z dozwolonych."""
    print(f"\n{numer}. {pytanie['text']}")
    odpowiedzi = pytanie["answers"]

    for indeks, odpowiedz in enumerate(odpowiedzi, start=1):
        opis = odpowiedz.replace("_", " ")
        print(f"  {indeks}. {opis}")

    while True:
        wybor = input("Wybierz numer odpowiedzi: ").strip()
        if wybor.isdigit():
            indeks = int(wybor)
            if 1 <= indeks <= len(odpowiedzi):
                return odpowiedzi[indeks - 1]
        print(f"Nieprawidłowy wybór. Podaj liczbę od 1 do {len(odpowiedzi)}.")


def dopasuj_reguly(reguly, odpowiedzi_uzytkownika):
    """Zwraca reguły, których wszystkie warunki są spełnione (AND)."""
    pasujace = []

    for regula in reguly:
        warunki = regula["if"]
        if all(
            odpowiedzi_uzytkownika.get(pytanie) == oczekiwana_odpowiedz
            for pytanie, oczekiwana_odpowiedz in warunki.items()
        ):
            pasujace.append(regula)

    return pasujace


def main():
    try:
        baza = wczytaj_baze()
    except (OSError, json.JSONDecodeError) as blad:
        print(f"Nie udało się wczytać pliku baza.json: {blad}")
        return

    print("=" * 67)
    print(baza["title"])
    print("=" * 67)
    print("Odpowiadaj na pytania, wybierając numer odpowiedzi.")
    print("To narzędzie edukacyjne i nie zastępuje diagnozy mechanika.")

    odpowiedzi_uzytkownika = {}
    for numer, (id_pytania, pytanie) in enumerate(baza["questions"].items(), start=1):
        odpowiedzi_uzytkownika[id_pytania] = zadaj_pytanie(numer, pytanie)

    pasujace = dopasuj_reguly(baza["rules"], odpowiedzi_uzytkownika)

    print("\n" + "=" * 67)
    print("WYNIKI SYSTEMU EKSPERCKIEGO")
    print("=" * 67)

    if not pasujace:
        print("Nie znaleziono reguły pasującej do wszystkich udzielonych odpowiedzi.")
        print("Nie oznacza to, że samochód jest sprawny. Skonsultuj objawy z mechanikiem.")
        return

    print(f"Liczba dopasowanych reguł: {len(pasujace)}")
    for regula in pasujace:
        wynik = regula["then"]
        print(f"\n[{regula['id']}] Możliwa diagnoza: {wynik['diagnosis']}")
        print(f"Poziom pilności: {wynik['severity']}")
        print(f"Zalecane działanie: {wynik['action']}")
        print(f"Spełnione warunki: {regula['if']}")

    if any(regula["then"]["severity"] == "wysokie" for regula in pasujace):
        print("\nUWAGA: Wśród wyników jest reguła o wysokim poziomie pilności.")
        print("Zadbaj o bezpieczeństwo i nie kontynuuj jazdy, jeśli dotyczy to hamulców,")
        print("przegrzewania lub poważnych odgłosów silnika.")


if __name__ == "__main__":
    main()
