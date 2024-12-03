import constantes
import random
import pygame


class SimpleAgent:
    def __init__(self, name, env, x, y, grid, base_x, base_y, obstacles):
        self.name = name
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
        directions = [
            (0, 1),  # Cima
            (0, -1),  # Baixo
            (1, 0),  # Direita
            (-1, 0),  # Esquerda
            (1, 1),  # Diagonal inferior direita
            (1, -1),  # Diagonal superior direita
            (-1, 1),  # Diagonal inferior esquerda
            (-1, -1),  # Diagonal superior esquerda
        ]

        # Lista de posições ocupadas pelos obstáculos
        obstacle_positions = [(obstacle.x, obstacle.y) for obstacle in self.obstacles]

        # Tenta encontrar uma direção válida
        random.shuffle(directions)  # Embaralha as direções para mais variedade
        for dx, dy in directions:
            new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
            new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))

            if (new_x, new_y) not in obstacle_positions:
                # Move o agente para a posição válida
                self.x, self.y = new_x, new_y
                return  # Sai do método após um movimento válido

    def collect_crystals(self):
        for resource in self.grid:
            # Verificar se o recurso está na vizinhança
            if (
                not resource.collected
                and resource.type == "cristal"
                and abs(resource.x - self.x) <= 1
                and abs(resource.y - self.y) <= 1
            ):
                # Move o agente até o recurso antes de coletar
                self.x, self.y = resource.x, resource.y
                resource.collected = True
                self.resources_collected += resource.value
                return True  # Recurso coletado
        return False  # Nenhum recurso coletado

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
