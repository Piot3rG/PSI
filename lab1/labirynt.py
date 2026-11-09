
import argparse
import os
import sys
import time
from collections import deque


# Kierunki: góra, dół, prawo, lewo
DIRECTIONS = {
    "U": (-1, 0),
    "D": (1, 0),
    "R": (0, 1),
    "L": (0, -1),
}

# Kierunki dostępne z poszczególnych pól
CONNECTIONS = {
    "\u253C": set("UDRL"),
    "\u2502": set("UD"),
    "\u2500": set("RL"),
    "\u0020": set(),

    "\u2510": set("DL"),
    "\u2518": set("UL"),
    "\u2514": set("UR"),
    "\u250C": set("DR"),

    "\u2524": set("UDL"),
    "\u2534": set("URL"),
    "\u251C": set("UDR"),
    "\u252C": set("DRL"),

    "\u2575": set("U"),
    "\u2577": set("D"),
    "\u2574": set("L"),
    "\u2576": set("R"),

}

OPPOSITE = {
    "U": "D",
    "D": "U",
    "R": "L",
    "L": "R",
}

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
RESET = "\033[0m"


def load_maze(filename):
    """Wczytuje mapę, zachowując spacje wewnątrz wierszy."""
    with open(filename, "r", encoding="utf-8") as file:
        lines = [line.rstrip("\r\n") for line in file]

    # Usuń ewentualne puste wiersze na końcu pliku.
    while lines and lines[-1] == "":
        lines.pop()

    if not lines:
        raise ValueError("Mapa jest pusta.")

    width = max(map(len, lines))

    # Krótsze wiersze uzupełnij spacjami.
    return [line.ljust(width) for line in lines]


def inside(maze, pos):
    r, c = pos
    return 0 <= r < len(maze) and 0 <= c < len(maze[0])


def can_move(maze, current, direction):
    """Sprawdza połączenie w obu sąsiednich polach."""
    r, c = current
    dr, dc = DIRECTIONS[direction]
    neighbor = (r + dr, c + dc)

    if not inside(maze, neighbor):
        return False

    current_char = maze[r][c]
    nr, nc = neighbor
    neighbor_char = maze[nr][nc]

    current_connections = CONNECTIONS.get(current_char, set())
    neighbor_connections = CONNECTIONS.get(neighbor_char, set())

    return (
        direction in current_connections
        and OPPOSITE[direction] in neighbor_connections
    )


def neighbors(maze, pos):
    """Zwraca dostępnych sąsiadów w ustalonej kolejności."""
    for direction in "UDRL":
        if can_move(maze, pos, direction):
            dr, dc = DIRECTIONS[direction]
            yield (pos[0] + dr, pos[1] + dc)


def draw_maze(maze, start, end, visited, frontier, delay=0.1):
    """Wyświetla aktualny stan przeszukiwania."""
    os.system("cls" if os.name == "nt" else "clear")

    frontier_set = set(frontier)

    for r, row in enumerate(maze):
        output = []

        for c, char in enumerate(row):
            pos = (r, c)

            if pos == start:
                output.append(f"{RED}{char}{RESET}")
            elif pos == end:
                output.append(f"{BLUE}{char}{RESET}")
            elif pos in frontier_set:
                output.append(f"{YELLOW}{char}{RESET}")
            elif pos in visited:
                output.append(f"{GREEN}{char}{RESET}")
            else:
                output.append(char)

        print("".join(output))

    print()
    print(f"{RED}Start{RESET}  "
          f"{BLUE}Koniec{RESET}  "
          f"{GREEN}Odwiedzone{RESET}  "
          f"{YELLOW}Oczekujące{RESET}")

    time.sleep(delay)


def search(maze, start, end, algorithm, delay=0.1):
    """Przeszukuje mapę metodą BFS lub DFS."""
    if algorithm == "BFS":
        frontier = deque([start])
    else:
        frontier = [start]

    visited = set()
    parent = {start: None}
    steps = 0

    while frontier:
        draw_maze(maze, start, end, visited, frontier, delay)

        if algorithm == "BFS":
            current = frontier.popleft()
        else:
            current = frontier.pop()

        if current in visited:
            continue

        visited.add(current)
        steps += 1

        if current == end:
            break

        next_positions = list(neighbors(maze, current))

        # DFS korzysta ze stosu LIFO, więc odwracamy kolejność,
        # aby zachować tę samą preferencję kierunków co BFS.
        if algorithm == "DFS":
            next_positions.reverse()

        for nxt in next_positions:
            if nxt not in parent and nxt not in visited:
                parent[nxt] = current
                frontier.append(nxt)

    found = end in visited
    path = []

    if found:
        pos = end
        while pos is not None:
            path.append(pos)
            pos = parent[pos]
        path.reverse()

    draw_maze(maze, start, end, visited, [], delay=0)

    # Wyświetl wynik i długość ścieżki.
    print()

    if found:
        print(f"{GREEN}Znaleziono ścieżkę!{RESET}")
        print(f"Długość ścieżki: {len(path) - 1} kroków")
        print("Współrzędne ścieżki:")
        print(" -> ".join(f"({r}, {c})" for r, c in path))
    else:
        print(f"{RED}Nie znaleziono ścieżki.{RESET}")

    print(f"Liczba przetworzonych pól: {steps}")
    return path, steps


def read_position(prompt, maze):
    while True:
        try:
            raw = input(prompt).strip().replace(",", " ")
            r, c = map(int, raw.split())
            pos = (r, c)

            if not inside(maze, pos):
                print("Współrzędne są poza mapą.")
                continue

            if maze[r][c] == " ":
                print("To puste pole bez połączeń. Wybierz inne.")
                continue

            return pos

        except ValueError:
            print("Podaj dwa całkowite numery: wiersz kolumna.")


def main():
    parser = argparse.ArgumentParser(
        description="Wyszukiwanie drogi w labiryncie metodą BFS lub DFS."
    )
    parser.add_argument("mapa", help="Ścieżka do pliku z mapą")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Opóźnienie animacji w sekundach (domyślnie 0.1)"
    )
    args = parser.parse_args()

    try:
        maze = load_maze(args.mapa)
    except (OSError, ValueError) as error:
        print(f"Błąd wczytywania mapy: {error}", file=sys.stderr)
        sys.exit(1)

    print("Mapa labiryntu:")
    for row in maze:
        print(row)

    print(f"\nRozmiar mapy: {len(maze)} wierszy x {len(maze[0])} kolumn")
    print("Współrzędne liczone od 0.")

    start = read_position("Podaj start (wiersz kolumna): ", maze)
    end = read_position("Podaj koniec (wiersz kolumna): ", maze)

    while True:
        algorithm = input("Wybierz algorytm (BFS/DFS): ").strip().upper()
        if algorithm in ("BFS", "DFS"):
            break
        print("Wpisz BFS lub DFS.")

    search(maze, start, end, algorithm, max(0, args.delay))


if __name__ == "__main__":
    main()
