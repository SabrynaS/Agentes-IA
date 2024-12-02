import constantes
import random
import pygame


class StateBasedAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0  # Contador de recursos coletados
        self.obstacles = obstacles
        self.color = constantes.GREEN
        self.explored = set()  # Guarda os lugares já visitados
        self.shared_info = {}  # Informações compartilhadas
        self.in_storm = False
        self.process = env.process(self.run())

    def move_exploration(self):
        """Move o agente para uma área não explorada."""
        neighbors = [
            (self.x + dx, self.y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
        ]
        valid_moves = [
            (nx, ny)
            for nx, ny in neighbors
            if 0 <= nx < constantes.GRID_WIDTH
            and 0 <= ny < constantes.GRID_HEIGHT
            and (nx, ny) not in self.explored
        ]
        if valid_moves:
            new_x, new_y = random.choice(valid_moves)
            if (new_x, new_y) not in [
                (obstacle.x, obstacle.y) for obstacle in self.obstacles
            ]:
                self.x, self.y = new_x, new_y
                self.explored.add((new_x, new_y))  # Marca o local como explorado

    def collect_resource(self):
        """Coleta cristais e metais e compartilha a informação."""
        for resource in self.grid:
            if (
                not resource.collected
                and resource.x == self.x
                and resource.y == self.y
                and resource.type
                in ["cristal", "metais"]  # Verifica se é cristal ou metal
            ):
                resource.collected = True
                self.shared_info[(self.x, self.y)] = "coletado"
                self.resources_collected += (
                    resource.value
                )  # Incrementa o contador de recursos
                return True  # Retorna True indicando que um recurso foi coletado
        return False  # Retorna False se nenhum recurso foi coletado

    def return_to_base(self):
        """Retorna à base."""
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
                self.move_exploration()
                if self.collect_resource():
                    yield from self.return_to_base()
                else:
                    # Caso não tenha coletado, continua a exploração
                    self.move_exploration()

            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha o agente na tela."""
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
