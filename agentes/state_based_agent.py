import constantes
import random
import pygame


class StateBasedAgent:
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
        self.color = constantes.GREEN
        self.explored = set()  
        self.shared_info = {} 
        self.in_storm = False
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
            and (nx, ny) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
        ]
        
        # Se houver movimentos válidos, escolha um deles
        if valid_moves:
            new_x, new_y = random.choice(valid_moves)
            self.x, self.y = new_x, new_y
            self.explored.add((new_x, new_y))
        else:
            # Tenta mover para qualquer vizinho não bloqueado se estiver preso
            fallback_moves = [
                (nx, ny)
                for nx, ny in neighbors
                if 0 <= nx < constantes.GRID_WIDTH
                and 0 <= ny < constantes.GRID_HEIGHT
                and (nx, ny) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
            ]
            if fallback_moves:
                self.x, self.y = random.choice(fallback_moves)
                
    def collect_resource(self):
        """Coleta cristais e metais e compartilha a informação."""
        for resource in self.grid:
            if (
                not resource.collected
                and resource.x == self.x
                and resource.y == self.y
                and resource.type in ["cristal", "metais"]
            ):
                resource.collected = True 
                self.shared_info[(self.x, self.y)] = "coletado"
                self.resources_collected += resource.value  # Incrementa o total de recursos coletados
                return True 
        return False 


    def return_to_base(self):
        """Retorna à base, considerando obstáculos."""
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            
            # Movimenta em direção à base, considerando obstáculos
            new_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)
            
            if (new_x, new_y) not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]:
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
                    print(f"{self.name} coletou um recurso e está retornando à base.")
                    yield from self.return_to_base()
                else:
                    self.move_exploration()

            yield self.env.timeout(1)


    def draw(self, screen):
        """Desenha o agente na tela."""
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
