import pygame
import random
import simpy

# Configurações do ambiente
GRID_WIDTH = 30
GRID_HEIGHT = 20
WINDOW_WIDTH = GRID_WIDTH * 20
WINDOW_HEIGHT = GRID_HEIGHT * 20
FPS = 10

# Cores
BLUE = (0, 0, 255)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

class Resource:
    def __init__(self, x, y, resource_type):
        self.x = x
        self.y = y
        self.type = resource_type
        self.collected = False
        self.value = 10 if resource_type == "cristal" else 0

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
        self.color = BLUE
        self.in_storm = False
        self.process = env.process(self.run())

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, GRID_HEIGHT - 1))
        if (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
            self.x, self.y = new_x, new_y

    def collect_crystals(self):
        for resource in self.grid:
            if not resource.collected and resource.type == "cristal" and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.resources_collected += resource.value
                break

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                self.move_randomly()
                self.collect_crystals()
                yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)

class GoalBasedAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.resources_to_collect = [resource for resource in grid if not resource.collected]
        self.obstacles = obstacles
        self.color = PINK
        self.in_storm = False
        self.process = env.process(self.run())

    def move_towards_goal(self, resource):
        dx = resource.x - self.x
        dy = resource.y - self.y
        if dx != 0:
            self.x += 1 if dx > 0 else -1
        elif dy != 0:
            self.y += 1 if dy > 0 else -1

    def collect_resource(self):
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.resources_collected += resource.value
                break

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            elif self.resources_to_collect:
                next_resource = self.resources_to_collect[0]
                self.move_towards_goal(next_resource)
                self.collect_resource()
                if next_resource.collected:
                    self.resources_to_collect.remove(next_resource)
            else:
                self.move_randomly()
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)

class StateBasedAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.obstacles = obstacles
        self.color = (0, 255, 255)  # Ciano
        self.explored = set()
        self.shared_info = {}
        self.in_storm = False
        self.process = env.process(self.run())

    def move_exploration(self):
        """Move o agente para uma área não explorada."""
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
        ]
        valid_moves = [
            (nx, ny)
            for nx, ny in neighbors
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and (nx, ny) not in self.explored
        ]
        if valid_moves:
            new_x, new_y = random.choice(valid_moves)
            self.x, self.y = new_x, new_y
            self.explored.add((new_x, new_y))

    def collect_crystals(self):
        """Coleta cristais e compartilha a informação."""
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.shared_info[(self.x, self.y)] = "coletado"
                break

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                self.move_exploration()
                self.collect_crystals()
            yield self.env.timeout(1)

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)


class CooperativeAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.obstacles = obstacles
        self.color = (255, 140, 0)  # Laranja
        self.in_storm = False
        self.process = env.process(self.run())

    def assist_other_agent(self, agents):
        """Calcula a utilidade de ajudar outros agentes."""
        for agent in agents:
            distance = abs(self.x - agent.x) + abs(self.y - agent.y)
            if distance < 5:  # Distância máxima para ajudar
                self.x, self.y = agent.x, agent.y
                break

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, GRID_HEIGHT - 1))
        if (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
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
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)


class BDIAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.obstacles = obstacles
        self.color = (128, 0, 128)  # Roxo
        self.in_storm = False
        self.shared_info = {}
        self.process = env.process(self.run())

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, GRID_HEIGHT - 1))
        if (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
            self.x, self.y = new_x, new_y

    def update_beliefs(self, agents):
        """Atualiza as crenças com base nas informações dos outros agentes."""
        for agent in agents:
            if isinstance(agent, StateBasedAgent):
                self.shared_info.update(agent.shared_info)

    def move_towards_goal(self):
        """Move-se para a localização de recursos compartilhados."""
        for (res_x, res_y), status in self.shared_info.items():
            if status == "disponível":
                dx = res_x - self.x
                dy = res_y - self.y
                self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
                self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
                break

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                self.move_towards_goal()  # Mover para o objetivo compartilhado
                if not self.shared_info:  # Se não houver recursos, mover aleatoriamente
                    self.move_randomly()
            yield self.env.timeout(1)

    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += (1 if dx > 0 else -1 if dx < 0 else 0)
            self.y += (1 if dy > 0 else -1 if dy < 0 else 0)
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)


def storm_cycle(env, agents):
    while True:
        yield env.timeout(random.randint(25, 50))
        print("Tempestade iniciada!")
        for agent in agents:
            agent.in_storm = True
        yield env.timeout(5)
        print("Tempestade terminou!")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    env = simpy.Environment()

    obstacles = [Resource(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), "obstacle") for _ in range(10)]
    resources = [Resource(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), "cristal") for _ in range(10)]
    
    agents = [
    SimpleAgent(env, 0, 0, resources, 0, 0, obstacles),
    GoalBasedAgent(env, GRID_WIDTH - 1, GRID_HEIGHT - 1, resources, 0, 0, obstacles),
    StateBasedAgent(env, 5, 5, resources, 0, 0, obstacles),
    CooperativeAgent(env, 15, 15, resources, 0, 0, obstacles),
    BDIAgent(env, 20, 10, resources, 0, 0, obstacles),
    ]


    env.process(storm_cycle(env, agents))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.step()
        screen.fill(RED if any(agent.in_storm for agent in agents) else WHITE)
 # Desenha a área da base (retângulo cinza)
        pygame.draw.rect(screen, (169, 169, 169), (0 * 20, 0 * 20, 5 * 20, 5 * 20))  # Ajuste as coordenadas conforme a posição da base        
        for resource in resources:
            if not resource.collected:
                pygame.draw.circle(screen, GREEN, (resource.x * 20 + 10, resource.y * 20 + 10), 6)
# Desenha os obstáculos (quadrados cinzas)
        for obstacle in obstacles:
            pygame.draw.rect(screen, BLACK, (obstacle.x * 20, obstacle.y * 20, 20, 20))

        for agent in agents:
            agent.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
