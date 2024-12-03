import constantes
import random
import pygame


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
        self.process = env.process(self.run())

    def assist_other_agent(self, agents):
        """Calcula a utilidade de ajudar outros agentes."""
        for agent in agents:
            distance = abs(self.x - agent.x) + abs(self.y - agent.y)
            if distance < 10:  # Distância máxima para ajudar
                self.x, self.y = agent.x, agent.y
                self.resources_collected += (
                    resource.value
                )  # Incrementa o contador de recursos

                break

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))
        if (new_x, new_y) not in [
            (obstacle.x, obstacle.y) for obstacle in self.obstacles
        ]:
            self.x, self.y = new_x, new_y

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                self.move_randomly()
            yield self.env.timeout(1)

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
