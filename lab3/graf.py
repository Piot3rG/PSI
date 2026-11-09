
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import heapq


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Szukanie ścieżki w grafie")
        self.root.geometry("850x650")

        self.graph = {}
        self.positions = {}

        self.create_interface()

    # ---------------- WCZYTYWANIE GRAFU ----------------

    def load_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Pliki tekstowe", "*.txt")]
        )

        if not filename:
            return

        try:
            with open(filename, "r") as file:
                lines = [line.strip() for line in file if line.strip()]

            n = int(lines[0])

            if len(lines) != 2 * n + 1:
                raise ValueError("Nieprawidłowa liczba linii.")

            self.positions = {}

            # Wczytywanie współrzędnych
            for i in range(n):
                x, y = map(int, lines[i + 1].split())
                self.positions[i + 1] = (x, y)

            # Wczytywanie sąsiadów
            self.graph = {i: [] for i in range(1, n + 1)}

            for i in range(n):
                data = list(map(int, lines[n + 1 + i].split()))

                count = data[0]
                neighbors = data[1:]

                if len(neighbors) != count:
                    raise ValueError("Nieprawidłowa lista sąsiadów.")

                for neighbor in neighbors:
                    if neighbor not in self.graph:
                        raise ValueError("Nieprawidłowy numer wierzchołka.")

                    if neighbor != i + 1:
                        if neighbor not in self.graph[i + 1]:
                            self.graph[i + 1].append(neighbor)

                        if i + 1 not in self.graph[neighbor]:
                            self.graph[neighbor].append(i + 1)

            values = list(self.graph.keys())

            self.start_box["values"] = values
            self.goal_box["values"] = values

            self.start_box.current(0)
            self.goal_box.current(len(values) - 1)

            self.reset_search()
            self.draw_graph()

        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    # ---------------- INTERFEJS ----------------

    def create_interface(self):
        controls = tk.Frame(self.root)
        controls.pack(pady=10)

        tk.Button(
            controls,
            text="Wczytaj graf",
            command=self.load_graph
        ).grid(row=0, column=0, padx=5)

        tk.Label(controls, text="Algorytm:").grid(row=0, column=1)

        self.algorithm_box = ttk.Combobox(
            controls,
            values=["Best First Search", "Dijkstra", "A*"],
            state="readonly",
            width=20
        )
        self.algorithm_box.current(0)
        self.algorithm_box.grid(row=0, column=2, padx=5)

        tk.Label(controls, text="Start:").grid(row=0, column=3)

        self.start_box = ttk.Combobox(
            controls,
            state="readonly",
            width=5
        )
        self.start_box.grid(row=0, column=4, padx=5)

        tk.Label(controls, text="Cel:").grid(row=0, column=5)

        self.goal_box = ttk.Combobox(
            controls,
            state="readonly",
            width=5
        )
        self.goal_box.grid(row=0, column=6, padx=5)

        tk.Button(
            controls,
            text="Rozpocznij",
            command=self.start_search
        ).grid(row=0, column=7, padx=5)

        buttons = tk.Frame(self.root)
        buttons.pack(pady=5)

        tk.Button(
            buttons,
            text="Następny krok",
            command=self.next_step
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons,
            text="Wykonaj do końca",
            command=self.run_all
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons,
            text="Reset",
            command=self.reset_search
        ).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(
            self.root,
            width=800,
            height=450,
            bg="white"
        )
        self.canvas.pack(pady=10)

        self.info = tk.Label(
            self.root,
            text="Wczytaj graf, wybierz algorytm i rozpocznij.",
            font=("Arial", 12)
        )
        self.info.pack(pady=10)

    # ---------------- RYSOWANIE GRAFU ----------------

    def draw_graph(self):
        self.canvas.delete("all")

        if not self.graph:
            return

        width = 800
        height = 450
        margin = 50

        xs = [p[0] for p in self.positions.values()]
        ys = [p[1] for p in self.positions.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        scale_x = (width - 2 * margin) / max(max_x - min_x, 1)
        scale_y = (height - 2 * margin) / max(max_y - min_y, 1)

        scale = min(scale_x, scale_y)

        self.screen_positions = {}

        for node, (x, y) in self.positions.items():
            sx = margin + (x - min_x) * scale
            sy = height - margin - (y - min_y) * scale
            self.screen_positions[node] = (sx, sy)

        # Rysowanie krawędzi
        for node in self.graph:
            for neighbor in self.graph[node]:
                if node < neighbor:
                    x1, y1 = self.screen_positions[node]
                    x2, y2 = self.screen_positions[neighbor]

                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill="gray",
                        width=2
                    )

        # Rysowanie wierzchołków
        for node, (x, y) in self.screen_positions.items():

            color = "lightgray"

            if node in self.closed:
                color = "skyblue"

            if node in self.path:
                color = "purple"

            if node == self.start:
                color = "green"

            if node == self.goal:
                color = "red"

            if node == self.current:
                color = "orange"

            self.canvas.create_oval(
                x - 15, y - 15,
                x + 15, y + 15,
                fill=color,
                outline="black",
                width=2
            )

            self.canvas.create_text(
                x, y,
                text=str(node),
                font=("Arial", 10, "bold"),
                fill="white" if color in ["purple", "green", "red", "orange"] else "black"
            )

    # ---------------- OBLICZANIE ODLEGŁOŚCI ----------------

    def distance(self, a, b):
        x1, y1 = self.positions[a]
        x2, y2 = self.positions[b]

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # Heurystyka - odległość od celu

    def heuristic(self, node):
        return self.distance(node, self.goal)

    # ---------------- ROZPOCZĘCIE SZUKANIA ----------------

    def reset_search(self):
        self.g_score = {}
        self.came_from = {}

        self.frontier = []
        self.closed = set()

        self.path = []
        self.current = None

        self.start = None
        self.goal = None

        self.finished = True
        self.counter = 0

        self.draw_graph()

    def start_search(self):
        if not self.graph:
            messagebox.showwarning("Uwaga", "Najpierw wczytaj graf.")
            return

        self.reset_search()

        self.start = int(self.start_box.get())
        self.goal = int(self.goal_box.get())

        self.algorithm = self.algorithm_box.get()

        self.g_score[self.start] = 0

        priority = self.get_priority(self.start)

        heapq.heappush(
            self.frontier,
            (priority, self.counter, self.start, 0)
        )

        self.counter += 1
        self.finished = False

        self.info.config(text="Rozpoczęto szukanie ścieżki.")

        self.draw_graph()

    # ---------------- FUNKCJA KOSZTU ----------------

    def get_priority(self, node):
        g = self.g_score[node]
        h = self.heuristic(node)

        if self.algorithm == "Best First Search":
            return h

        elif self.algorithm == "Dijkstra":
            return g

        else:  # A*
            return g + h

    # ---------------- KOLEJNY KROK ALGORYTMU ----------------

    def next_step(self):
        if self.finished:
            return

        # Pobranie najlepszego wierzchołka z kolejki
        while self.frontier:
            priority, _, node, old_g = heapq.heappop(self.frontier)

            # Pomijamy nieaktualne wpisy
            if old_g != self.g_score.get(node):
                continue

            if node in self.closed:
                continue

            break
        else:
            self.finished = True
            self.info.config(text="Nie znaleziono ścieżki!")
            self.draw_graph()
            return

        self.current = node
        self.closed.add(node)

        # Czy dotarliśmy do celu?
        if node == self.goal:
            self.reconstruct_path()

            self.finished = True

            cost = self.g_score[self.goal]

            self.info.config(
                text=f"Znaleziono ścieżkę: {self.path} | Koszt: {cost:.2f}"
            )

            self.draw_graph()
            return

        # Sprawdzanie sąsiadów
        for neighbor in self.graph[node]:

            if neighbor in self.closed:
                continue

            new_cost = self.g_score[node] + self.distance(node, neighbor)

            if new_cost < self.g_score.get(neighbor, float("inf")):

                self.g_score[neighbor] = new_cost
                self.came_from[neighbor] = node

                priority = self.get_priority(neighbor)

                heapq.heappush(
                    self.frontier,
                    (priority, self.counter, neighbor, new_cost)
                )

                self.counter += 1

        self.info.config(
            text=f"Sprawdzany wierzchołek: {node} | "
                 f"Koszt dojścia: {self.g_score[node]:.2f}"
        )

        self.draw_graph()

    def run_all(self):
        while not self.finished:
            self.next_step()
            self.root.update()

    # ---------------- ODTWARZANIE ŚCIEŻKI ----------------

    def reconstruct_path(self):
        node = self.goal
        self.path = []

        while node != self.start:
            self.path.append(node)
            node = self.came_from[node]

        self.path.append(self.start)
        self.path.reverse()


# ---------------- URUCHOMIENIE PROGRAMU ----------------

root = tk.Tk()
app = GraphApp(root)
root.mainloop()
