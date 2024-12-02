import constantes
import random
import pygame


class SimpleAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.obstacles = obstacles
        self.color = constantes.BLUE
        self.in_storm = False
        self.process = env.process(self.run())

    def move_randomly(self):
        # Definir um intervalo maior de movimentos aleatórios
        # Movimentos incluem: cima, baixo, esquerda, direita, e diagonais
        # Além disso, podemos usar um valor aleatório para se mover em mais de uma casa, se necessário
        directions = [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),  # Movimentos cardeais
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),  # Movimentos diagonais
        ]

        dx, dy = random.choice(directions)

        # Escolhe um movimento aleatório maior (1 ou 2 casas)
        move_distance = random.choice([1, 2])
        new_x = max(0, min(self.x + dx * move_distance, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy * move_distance, constantes.GRID_HEIGHT - 1))

        # Impede o movimento para áreas com obstáculos
        if (new_x, new_y) not in [
            (obstacle.x, obstacle.y) for obstacle in self.obstacles
        ]:
            self.x, self.y = new_x, new_y

    def collect_crystals(self):
        for resource in self.grid:
            if (
                not resource.collected
                and resource.type == "cristal"
                and resource.x == self.x
                and resource.y == self.y
            ):
                resource.collected = True
                self.resources_collected += resource.value
                return True  # Retorna True quando o cristal é coletado
        return False  # Retorna False se não coletou nada

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                collected = self.collect_crystals()
                if collected:
                    yield from self.return_to_base()  # Retorna à base para deixar o cristal
                else:
                    self.move_randomly()  # Caso contrário, continua se movendo
                yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
