import constantes
import random
import pygame


class GoalBasedAgent:
    def __init__(self, name, env, x, y, grid, base_x, base_y, obstacles):
        self.name = name
        self.env = env
        self.x = x
        self.y = y
        self.grid = grid
        self.base_x = base_x
        self.base_y = base_y
        self.resources_collected = 0
        self.resources_to_collect = [
            resource
            for resource in grid
            if not resource.collected and resource.type in ["cristal", "metal"]
        ]
        self.obstacles = obstacles
        self.color = constantes.PINK
        self.in_storm = False
        self.previous_position = None  # Guardar a posição anterior
        self.process = env.process(self.run())

    def move_towards_goal(self, resource):
        dx = resource.x - self.x
        dy = resource.y - self.y

        # Movimentos preferidos (direção do recurso)
        preferred_moves = []
        if dx != 0:
            # Garante que o movimento no eixo X não ultrapasse os limites
            new_x = self.x + (1 if dx > 0 else -1)
            if 0 <= new_x < constantes.GRID_WIDTH:  # Verificação dos limites
                preferred_moves.append((new_x, self.y))  # Eixo X
        if dy != 0:
            # Garante que o movimento no eixo Y não ultrapasse os limites
            new_y = self.y + (1 if dy > 0 else -1)
            if 0 <= new_y < constantes.GRID_HEIGHT:  # Verificação dos limites
                preferred_moves.append((self.x, new_y))  # Eixo Y

        # Alternativas (diagonais e vizinhos)
        alternative_moves = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1),
            (self.x + 1, self.y + 1),
            (self.x + 1, self.y - 1),
            (self.x - 1, self.y + 1),
            (self.x - 1, self.y - 1),
        ]

        # Filtrar movimentos alternativos que não ultrapassem os limites
        alternative_moves = [
            move
            for move in alternative_moves
            if 0 <= move[0] < constantes.GRID_WIDTH
            and 0 <= move[1] < constantes.GRID_HEIGHT
        ]

        # Combina movimentos preferidos e alternativos
        all_moves = preferred_moves + [
            move for move in alternative_moves if move not in preferred_moves
        ]

        # Filtrar movimentos válidos (não colidir com obstáculos e evitar retorno imediato)
        valid_moves = [
            move
            for move in all_moves
            if move not in [(obstacle.x, obstacle.y) for obstacle in self.obstacles]
            and move != self.previous_position  # Evitar retorno imediato
        ]

        # Se houver movimentos válidos, escolher o primeiro
        if valid_moves:
            self.previous_position = (self.x, self.y)  # Atualiza a posição anterior
            self.x, self.y = valid_moves[0]
        else:
            print(
                f"Bloqueado em ({self.x}, {self.y}). Nenhuma posição válida encontrada."
            )

    def collect_resource(self):
        """Coleta recursos (cristais e metais) na posição atual ou na vizinhança."""
        # Coordenadas da vizinhança (incluindo a célula atual)
        neighbors = [
            (self.x + dx, self.y + dy)
            for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        ]

        for resource in self.grid:
            if (
                not resource.collected
                and (resource.x, resource.y) in neighbors
                and resource.type in ["cristal", "metais"]
            ):
                resource.collected = True
                self.resources_collected += (
                    resource.value
                )  # Incrementa o contador de recursos

                # Atualiza a posição do agente para o local do recurso coletado
                self.x, self.y = resource.x, resource.y

                # Remove o recurso da lista de recursos a coletar
                if resource in self.resources_to_collect:
                    self.resources_to_collect.remove(resource)

                return True  # Indica que um recurso foi coletado

        return False  # Retorna False se nenhum recurso foi coletado
    
    def return_to_base(self):
        while self.x != self.base_x or self.y != self.base_y:
            dx = self.base_x - self.x
            dy = self.base_y - self.y

            # Lista de obstáculos como tuplas
            obstacle_positions = [(o.x, o.y) for o in self.obstacles]

            # Lista de alternativas de movimento (priorizando a direção da base)
            possible_moves = [
                (self.x + (1 if dx > 0 else -1 if dx < 0 else 0), self.y),  # Movimento em X
                (self.x, self.y + (1 if dy > 0 else -1 if dy < 0 else 0)),  # Movimento em Y
                (self.x + 1, self.y),  # Movimento lateral
                (self.x - 1, self.y),
                (self.x, self.y + 1),
                (self.x, self.y - 1),
            ]

            # Filtrar movimentos válidos
            valid_moves = [
                (nx, ny)
                for nx, ny in possible_moves
                if 0 <= nx < constantes.GRID_WIDTH
                and 0 <= ny < constantes.GRID_HEIGHT
                and (nx, ny) not in obstacle_positions
            ]

            if valid_moves:
                # Escolher o moviento que mais aproxima da base
                best_move = min(valid_moves, key=lambda pos: abs(self.base_x - pos[0]) + abs(self.base_y - pos[1]))
                self.x, self.y = best_move
            else:
                yield self.env.timeout(1) 

            
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            elif self.resources_to_collect:
                next_resource = self.resources_to_collect[0]
                self.move_towards_goal(next_resource)
                if self.collect_resource():  # Se um recurso foi coletado
                    yield from self.return_to_base()  # Retorna à base após coletar
                else:
                    # Caso não tenha coletado, continua a busca
                    pass
            else:
                self.move_towards_goal()  # Opção de mover aleatoriamente se não houver recursos
            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha o agente na tela."""
        pygame.draw.circle(screen, self.color, (self.x * 20 + 10, self.y * 20 + 10), 8)
