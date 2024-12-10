import constantes
import random
import pygame

from .state_based_agent import StateBasedAgent


class BDIAgent:
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
        self.color = constantes.PURPLE
        self.in_storm = False
        self.shared_info = {}
        self.carrying_resource = False
        self.process = env.process(self.run())

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))

        if (new_x, new_y) not in [
            (obstacle.x, obstacle.y) for obstacle in self.obstacles
        ]:
            self.x, self.y = new_x, new_y
            self.collect_resources()

    def update_beliefs(self, agents):
        """Atualiza as crenças com base nas informações dos outros agentes."""
        for agent in agents:
            if isinstance(agent, StateBasedAgent):
                self.shared_info.update(agent.shared_info)

    def collect_resources(self):
        """Verifica se há recursos metálicos ou cristais na célula atual ou na vizinhança e coleta-os."""
        if self.carrying_resource:
            return

        # Coordenadas da vizinhança
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        for resource in self.grid[:]:
            if not resource.collected and (resource.x, resource.y) in neighbors:
                if resource.type in ["metais", "cristal"]:
                    resource.collected = True
                    self.resources_collected += resource.value
                    self.carrying_resource = True

                    self.grid.remove(resource)
                    break

    def move_towards_goal(self):
        """Move-se para a localização de recursos compartilhados."""
        for (res_x, res_y), status in self.shared_info.items():
            if status == "disponível":
                dx = res_x - self.x
                dy = res_y - self.y
                self.x += 1 if dx > 0 else -1 if dx < 0 else 0
                self.y += 1 if dy > 0 else -1 if dy < 0 else 0
                self.collect_resources()
                break

    def return_to_base(self):
        """Move-se de volta à base para deixar os recursos coletados."""
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)
        self.carrying_resource = False

    def run(self):
        while True:
            if self.carrying_resource:
                yield from self.return_to_base()
            elif self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                self.move_towards_goal()
                if not self.shared_info:
                    self.move_randomly()
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
