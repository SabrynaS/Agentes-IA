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
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))
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
                break

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
                self.move_randomly()
                self.collect_crystals()
                yield self.env.timeout(1)

    def collect_resources(self):
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                if resource.required_agents == 1:
                    self.collect_crystals()
                elif resource.required_agents == 2:
                    # Verificar se outro agente está coletando a mesma estrutura
                    if any(
                        agent.x == self.x
                        and agent.y == self.y
                        and agent.collecting_structure
                        for agent in agents
                    ):
                        # Coletar a estrutura
                        resource.collected = True
                        self.resources_collected += resource.value
                        self.collecting_structure = False  # Finalizar a coleta
                    else:
                        # Iniciar a coleta da estrutura
                        self.collecting_structure = True

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
        self.resources_to_collect = [
            resource for resource in grid if not resource.collected
        ]
        self.obstacles = obstacles
        self.color = constantes.PINK
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
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
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
        self.resources_collected = (
            0  # Adiciona o atributo para contar os recursos coletados
        )
        self.obstacles = obstacles
        self.color = (0, 255, 255)  # Ciano
        self.explored = set()
        self.shared_info = {}
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
            self.x, self.y = new_x, new_y
            self.explored.add((new_x, new_y))

    def collect_crystals(self):
        """Coleta cristais e compartilha a informação."""
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.shared_info[(self.x, self.y)] = "coletado"
                self.resources_collected += (
                    resource.value
                )  # Incrementa o contador de recursos
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
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
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
        self.resources_collected = 0  # Initialize resources collected to 0
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


class BDIAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0  # Initialize resources collected to 0
        self.obstacles = obstacles
        self.color = (128, 0, 128)  # Roxo
        self.in_storm = False
        self.shared_info = {}
        self.process = env.process(self.run())

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))
        if (new_x, new_y) not in [
            (obstacle.x, obstacle.y) for obstacle in self.obstacles
        ]:
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
                self.x += 1 if dx > 0 else -1 if dx < 0 else 0
                self.y += 1 if dy > 0 else -1 if dy < 0 else 0
                self.resources_collected += resource.value
                # Incrementa o contador de recursos

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
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
