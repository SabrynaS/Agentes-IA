import pygame
import random
import simpy

# Configurações do ambiente
GRID_SIZE = 10  # Tamanho da célula
GRID_WIDTH = 30  # Número de células na horizontal
GRID_HEIGHT = 20  # Número de células na vertical
WINDOW_WIDTH = GRID_SIZE * GRID_WIDTH
WINDOW_HEIGHT = GRID_SIZE * GRID_HEIGHT
FPS = 10

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Configurações do agente
AGENT_COLOR = (0, 0, 255)
AGENT_SPEED = 1  # Movimentos por ciclo

# Configurações do recurso
RESOURCE_COLOR = (255, 255, 0)
RESOURCE_VALUE = 10  # Valor do recurso pequeno

class Resource:
    def __init__(self, x, y, resource_type):
        self.x = x
        self.y = y
        self.type = resource_type  # Tipo do recurso
        self.collected = False

        # Definir atributos baseados no tipo
        if self.type == "cristal":
            self.value = 10
            self.size = 1  # Pequeno, 1 agente
        elif self.type == "metal":
            self.value = 20
            self.size = 1  # Médio, 1 agente
        elif self.type == "estrutura":
            self.value = 50
            self.size = 2  # Grande, 2 agentes

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Agente Baseado em Estado
class StateBasedAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.visited_positions = set()  # Memória de áreas visitadas
        self.obstacles = obstacles
        self.process = env.process(self.run())

    def move(self):
        """Move o agente, evitando posições já visitadas e obstáculos."""
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Cima, baixo, esquerda, direita
        random.shuffle(possible_moves)  # Para maior diversidade

        for dx, dy in possible_moves:
            new_x = max(0, min(self.x + dx, GRID_WIDTH - 1))
            new_y = max(0, min(self.y + dy, GRID_HEIGHT - 1))

            # Evita posições já visitadas ou ocupadas por obstáculos
            if (new_x, new_y) not in self.visited_positions and \
                (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
                self.x, self.y = new_x, new_y
                self.visited_positions.add((new_x, new_y))  # Marca como visitada
                break

    def collect_resource(self):
        """Coleta um recurso se o agente estiver na mesma posição."""
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.resources_collected += resource.value  # Aumenta a quantidade de recursos coletados
                break

    def run(self):
        """Ciclo de vida do agente."""
        while True:
            self.move()
            self.collect_resource()
            yield self.env.timeout(1)

# Agente Simples (Movimento aleatório)
class SimpleAgent:
    def __init__(self, env, x, y, grid, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.resources_collected = 0
        self.obstacles = obstacles
        self.process = env.process(self.run())

    def move_randomly(self):
        """Move o agente aleatoriamente pelo ambiente."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])  # Movimentos possíveis: cima, baixo, esquerda, direita
        new_x = max(0, min(self.x + dx, GRID_WIDTH - 1))
        new_y = max(0, min(self.y + dy, GRID_HEIGHT - 1))

        # Verifica se a nova posição não está ocupada por um obstáculo
        if (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
            self.x, self.y = new_x, new_y

    def collect_crystals(self):
        """Coleta cristais se o agente estiver na mesma posição de um cristal."""
        for resource in self.grid:
            if not resource.collected and resource.type == "cristal" and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.resources_collected += resource.value  # Aumenta a quantidade de cristais coletados
                break

    def run(self):
        """Ciclo de vida do agente simples."""
        while True:
            self.move_randomly()
            self.collect_crystals()
            yield self.env.timeout(1)

# Agente Baseado em Objetivos
class GoalBasedAgent:
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.resources_to_collect = [resource for resource in grid if not resource.collected]  # Lista de recursos
        self.obstacles = obstacles
        self.process = env.process(self.run())

    def move_towards_goal(self, resource):
        """Move o agente na direção do recurso mais próximo."""
        dx = resource.x - self.x
        dy = resource.y - self.y
        if dx > 0:
            self.x += 1
        elif dx < 0:
            self.x -= 1
        if dy > 0:
            self.y += 1
        elif dy < 0:
            self.y -= 1

    def collect_resource(self):
        """Coleta o recurso assim que chega na sua posição."""
        for resource in self.grid:
            if not resource.collected and resource.x == self.x and resource.y == self.y:
                resource.collected = True
                self.resources_collected += resource.value  # Aumenta a quantidade de recursos coletados
                break

    def run(self):
        """Ciclo de vida do agente."""
        while True:
            if self.resources_to_collect:
                # Move em direção ao próximo recurso
                next_resource = self.resources_to_collect[0]  # Apenas coleta um recurso por vez
                self.move_towards_goal(next_resource)
                self.collect_resource()

                # Remover o recurso coletado da lista
                if next_resource.collected:
                    self.resources_to_collect.remove(next_resource)

            yield self.env.timeout(1)
def main():
    # Inicializa o Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Inicializa o SimPy
    env = simpy.Environment()

    # Criação dos recursos no grid
    resources = []
    for _ in range(5):
        resources.append(Resource(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), "cristal"))
    for _ in range(3):
        resources.append(Resource(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), "metal"))
    for _ in range(2):
        resources.append(Resource(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), "estrutura"))

    # Criação dos obstáculos no grid
    obstacles = []
    for _ in range(10):  # Adiciona 10 obstáculos aleatórios
        x, y = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
        obstacles.append(Obstacle(x, y))

    # Inicializa os agentes
    base_x, base_y = GRID_WIDTH // 2, GRID_HEIGHT // 2  # Base no centro do grid
    agents = [
        StateBasedAgent(env, base_x, base_y, resources, base_x, base_y, obstacles),
        GoalBasedAgent(env, base_x + 1, base_y, resources, base_x, base_y, obstacles),
        SimpleAgent(env, random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), resources, obstacles)  # Novo Agente Simples
    ]

    # Simulação
    running = True
    simulation_time = 100  # Tempo total permitido
    while running and env.now < simulation_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.step()

        # Renderiza o ambiente
        screen.fill(WHITE)

        # Desenha a base
        pygame.draw.rect(screen, RED, (base_x * GRID_SIZE, base_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Desenha os obstáculos (quadrados vermelhos)
        for obstacle in obstacles:
            pygame.draw.rect(
                screen,
                (255, 0, 0),  # Cor vermelha
                (obstacle.x * GRID_SIZE, obstacle.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            )

        # Desenha os recursos
        for resource in resources:
            if not resource.collected:
                if resource.type == "cristal":
                    color = (0, 255, 255)  # Azul claro
                elif resource.type == "metal":
                    color = (192, 192, 192)  # Cinza metálico
                elif resource.type == "estrutura":
                    color = (255, 165, 0)  # Laranja
                pygame.draw.circle(
                    screen,
                    color,
                    (resource.x * GRID_SIZE + GRID_SIZE // 2, resource.y * GRID_SIZE + GRID_SIZE // 2),
                    GRID_SIZE // 4
                )

        # Desenha os agentes
        for agent in agents:
            pygame.draw.circle(
                screen,
                AGENT_COLOR,
                (agent.x * GRID_SIZE + GRID_SIZE // 2, agent.y * GRID_SIZE + GRID_SIZE // 2),
                GRID_SIZE // 3
            )

        # Atualiza a tela
        pygame.display.flip()

        clock.tick(FPS)

    # Resultado após a simulação
    for idx, agent in enumerate(agents):
        print(f"Agente {idx + 1} coletou {agent.resources_collected} recursos.")

    pygame.quit()

if __name__ == "__main__":
    main()