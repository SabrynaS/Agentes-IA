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
        self.carrying_resource = False  # Adicionando o atributo de controle de recurso
        self.process = env.process(self.run())

    def collect_resources(self):
        """Verifica se há recursos metálicos ou cristais na célula atual ou nas células vizinhas e coleta-os."""
        if self.carrying_resource:
            return

        # Coordenadas da vizinhança (incluindo a célula atual)
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        for resource in self.grid[:]:  # Cria uma cópia da lista para iteração segura
            if not resource.collected and (resource.x, resource.y) in neighbors:
                # Verifica se o recurso é metal ou cristal
                if resource.type in ["metais", "cristal"]:
                    resource.collected = True  # Marca o recurso como coletado
                    self.resources_collected += (
                        resource.value
                    )  # Soma o valor do recurso coletado
                    self.carrying_resource = (
                        True  # Marca que o agente está carregando um recurso
                    )

                    self.grid.remove(resource)  # Remove o recurso da lista de recursos
                    break  # Coleta apenas o primeiro recurso encontrado na vizinhança

    def assist_other_agent(self, agents):
        """Calcula a utilidade de ajudar outros agentes, considerando a possibilidade de coletar recursos durante a assistência."""
        for agent in agents:
            distance = abs(self.x - agent.x) + abs(self.y - agent.y)
            if distance < 10:  # Distância máxima para ajudar
                self.x, self.y = agent.x, agent.y
                self.collect_resources()  # Tenta coletar recursos enquanto ajuda

                # Incrementa o contador de recursos após ajudar
                self.resources_collected += agent.resources_collected
                agent.resources_collected = (
                    0  # Transferir os recursos do agente assistido
                )

                break

    def move_randomly(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))

        if (new_x, new_y) not in [
            (obstacle.x, obstacle.y) for obstacle in self.obstacles
        ]:
            self.x, self.y = new_x, new_y
            self.collect_resources()  # Tenta coletar recursos ao se mover

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
