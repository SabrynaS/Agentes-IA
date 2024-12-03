import random

import pygame
import constantes


class StateBasedAgent:
    def __init__(self, name, env, x, y, grid, base_x, base_y, obstacles, cooperative_agent):
        self.name = name
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.obstacles = obstacles
        self.color = constantes.GREEN
        self.explored = set()
        self.shared_info = {}
        self.in_storm = False
        self.cooperative_agent = cooperative_agent  # Referência ao agente cooperativo
        self.process = env.process(self.run())

    def move_exploration(self):
        """Move o agente para uma área não explorada ou tenta escapar de situações bloqueadas."""
        neighbors = [
            (self.x + dx, self.y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
        ]
        valid_moves = [
            (nx, ny)
            for nx, ny in neighbors
            if 0 <= nx < constantes.GRID_WIDTH
            and 0 <= ny < constantes.GRID_HEIGHT
            and (nx, ny) not in self.explored
            and (nx, ny)
            not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
        ]

        if valid_moves:
            new_x, new_y = random.choice(valid_moves)
            self.x, self.y = new_x, new_y
            self.explored.add((new_x, new_y))
        else:
            fallback_moves = [
                (nx, ny)
                for nx, ny in neighbors
                if 0 <= nx < constantes.GRID_WIDTH
                and 0 <= ny < constantes.GRID_HEIGHT
                and (nx, ny)
                not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
            ]
            if fallback_moves:
                self.x, self.y = random.choice(fallback_moves)

    def alert_cooperative_agent(self, resource):
        """Envia um alerta ao agente cooperativo para ir até o recurso."""
        if resource:
            self.cooperative_agent.receive_call(resource)

    def collect_resource(self):
        """Coleta recursos (cristais e metais) ou envia alerta para 'estrutura antiga'."""
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        for resource in self.grid:
            if not resource.collected and (resource.x, resource.y) in neighbors:
                if resource.type in ["cristal", "metais"]:
                    resource.collected = True
                    self.shared_info[(resource.x, resource.y)] = "coletado"
                    self.resources_collected += resource.value
                    self.x, self.y = resource.x, resource.y
                    return True  # Recurso coletado
                elif resource.type == "estrutura antiga":
                    self.shared_info[(resource.x, resource.y)] = "estrutura antiga"
                    self.alert_cooperative_agent(resource)  # Envia alerta
                    return False  # Para a coleta e espera

        return False

    def return_to_base(self):
        """Retorna à base, considerando obstáculos."""
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y

            new_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

            if (new_x, new_y) not in [
                (obstacle.x, obstacle.y) for obstacle in self.obstacles
            ]:
                self.x, self.y = new_x, new_y
            else:
                self.move_exploration()

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
                    self.move_exploration()

            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha o agente na tela."""
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)