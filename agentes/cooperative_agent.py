import pygame
from agentes import state_based_agent
import constantes


class CooperativeAgent:
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
        self.color = constantes.ORANGE
        self.in_storm = False
        self.carrying_resource = False
        self.waiting_for_call = True
        self.target_resource = None
        self.state_based_agent = state_based_agent
        self.process = env.process(self.run())

    def receive_call(self, resource):
        self.waiting_for_call = False
        self.target_resource = resource

    def move_to_resource(self):
        """Move-se para o recurso identificado e espera o outro agente."""
        if not self.target_resource:
            return

        while (self.x, self.y) != (self.target_resource.x, self.target_resource.y):
            dx = self.target_resource.x - self.x
            dy = self.target_resource.y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

        if not self.target_resource.collected:
            self.target_resource.collected = True
            self.resources_collected += self.target_resource.value
            self.grid.remove(self.target_resource)
            self.target_resource = None
            self.carrying_resource = True

        yield from self.return_to_base()

        self.carrying_resource = False
        self.waiting_for_call = True

    def return_to_base(self):
        """Retorna à base, sincronizando com o outro agente."""
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y

            new_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

            if (new_x, new_y) not in [
                (obstacle.x, obstacle.y) for obstacle in self.obstacles
            ]:
                self.x, self.y = new_x, new_y

            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            elif not self.waiting_for_call:
                self.resources_collected += 50
                yield from self.move_to_resource()
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
