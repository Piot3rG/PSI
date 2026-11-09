
import random

# ==============================
# DANE PROBLEMU
# ==============================

# Każdy przedmiot: (nazwa, waga, wartość)
items = [
    ("Laptop", 5, 15),
    ("Telefon", 2, 8),
    ("Ksiazka", 3, 10),
    ("Aparat", 4, 12),
    ("Sluchawki", 1, 5),
    ("Tablet", 3, 11),
    ("Kamera", 6, 18),
    ("Zegarek", 1, 6),
    ("Plecak", 2, 7),
    ("Powerbank", 2, 9)
]

CAPACITY = 10

# Parametry algorytmu
POPULATION_SIZE = 50
GENERATIONS = 200
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.02
ELITE_SIZE = 2


# ==============================
# FUNKCJE POMOCNICZE
# ==============================

# Generowanie losowego osobnika
def generate_individual():
    return [random.randint(0, 1) for _ in items]


# Obliczanie wagi plecaka
def calculate_weight(individual):
    return sum(
        individual[i] * items[i][1]
        for i in range(len(items))
    )


# Obliczanie wartości przedmiotów
def calculate_value(individual):
    return sum(
        individual[i] * items[i][2]
        for i in range(len(items))
    )


# Naprawianie osobnika, jeśli przekracza pojemność plecaka
def repair(individual):
    while calculate_weight(individual) > CAPACITY:
        selected = random.choice([
            i for i in range(len(items)) if individual[i] == 1
        ])
        individual[selected] = 0

    return individual


# Funkcja oceny przystosowania
def fitness(individual):
    if calculate_weight(individual) > CAPACITY:
        return 0

    return calculate_value(individual)


# ==============================
# OPERATORY GENETYCZNE
# ==============================

# Selekcja turniejowa
def selection(population):
    tournament = random.sample(population, 3)

    return max(tournament, key=fitness).copy()


# Krzyżowanie jednopunktowe
def crossover(parent1, parent2):
    point = random.randint(1, len(items) - 1)

    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    return child1, child2


# Mutacja bitowa
def mutation(individual):
    for i in range(len(individual)):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]

    return individual


# ==============================
# ALGORYTM GENETYCZNY
# ==============================

def genetic_algorithm():

    # Tworzenie początkowej populacji
    population = [
        repair(generate_individual())
        for _ in range(POPULATION_SIZE)
    ]

    best_history = []

    for generation in range(GENERATIONS):

        # Sortowanie populacji według przystosowania
        population.sort(key=fitness, reverse=True)

        # Zachowanie najlepszych osobników
        new_population = [
            individual.copy()
            for individual in population[:ELITE_SIZE]
        ]

        # Tworzenie nowego pokolenia
        while len(new_population) < POPULATION_SIZE:

            parent1 = selection(population)
            parent2 = selection(population)

            # Krzyżowanie
            if random.random() < CROSSOVER_RATE:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1 = parent1.copy()
                child2 = parent2.copy()

            # Mutacja i naprawa potomków
            child1 = mutation(child1)
            child2 = mutation(child2)

            child1 = repair(child1)
            child2 = repair(child2)

            new_population.append(child1)

            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        population = new_population

        # Zapisywanie najlepszego wyniku z pokolenia
        best = max(population, key=fitness)
        best_history.append(fitness(best))

    # Zwrócenie najlepszego rozwiązania
    best = max(population, key=fitness)

    return best, best_history


# ==============================
# URUCHOMIENIE I WYNIKI
# ==============================

best, history = genetic_algorithm()

print("===== WYNIKI ALGORYTMU GENETYCZNEGO =====")

print("\nWybrane przedmioty:")

for i in range(len(items)):
    if best[i] == 1:
        print(
            items[i][0],
            "- waga:", items[i][1],
            "- wartość:", items[i][2]
        )

print("\nLaczna waga:", calculate_weight(best))
print("Pojemnosc plecaka:", CAPACITY)
print("Laczna wartosc:", calculate_value(best))

print("\nNajlepsze wyniki w kolejnych pokoleniach:")
print("Poczatek:", history[0])
print("Koniec:", history[-1])
