import pygame
import random
import simpy
import constantes
from agentes import (
    SimpleAgent,
    GoalBasedAgent,
    StateBasedAgent,
    CooperativeAgent,
    BDIAgent,
)
from recursos import Resource, storm_cycle


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (constantes.WINDOW_WIDTH, constantes.WINDOW_HEIGHT)
    )
    clock = pygame.time.Clock()
    env = simpy.Environment()

    obstacles = [
        Resource(
            random.randint(0, constantes.GRID_WIDTH - 1),
            random.randint(0, constantes.GRID_HEIGHT - 1),
            "obstacle",
        )
        for _ in range(10)
    ]
    """resources = [
        Resource(
            random.randint(0, constantes.GRID_WIDTH - 1),
            random.randint(0, constantes.GRID_HEIGHT - 1),
            "cristal",
            color=constantes.GREEN,
        )
        for _ in range(10)
    ]
    resources.extend(
        [
            Resource(
                random.randint(0, constantes.GRID_WIDTH - 1),
                random.randint(0, constantes.GRID_HEIGHT - 1),
                "metais",
                color=constantes.PINK,
            )
            for _ in range(8)
        ]
    )"""
    resources = [
        Resource(
            random.randint(0, constantes.GRID_WIDTH - 1),
            random.randint(0, constantes.GRID_HEIGHT - 1),
            "estrutura_antiga",
            2,
            color=constantes.PURPLE,
        )
        for _ in range(5)
    ]

    agents = [
        SimpleAgent(env, 0, 0, resources, 0, 0, obstacles),
        GoalBasedAgent(
            env,
            constantes.GRID_WIDTH - 1,
            constantes.GRID_HEIGHT - 1,
            resources,
            0,
            0,
            obstacles,
        ),
        StateBasedAgent(env, 5, 5, resources, 0, 0, obstacles),
        CooperativeAgent(env, 15, 15, resources, 0, 0, obstacles),
        BDIAgent(env, 20, 10, resources, 0, 0, obstacles),
    ]

    env.process(storm_cycle(env, agents))

    # Tempo máximo da simulação em segundos
    SIMULATION_TIME = 30  # Ajuste este valor conforme necessário
    simulation_step = 0

    running = True
    while running and simulation_step < constantes.FPS * SIMULATION_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.step()
        screen.fill(
            constantes.RED
            if any(agent.in_storm for agent in agents)
            else constantes.WHITE
        )
        # Desenha a área da base (retângulo cinza)
        pygame.draw.rect(
            screen, (169, 169, 169), (0 * 20, 0 * 20, 5 * 20, 5 * 20)
        )  # Ajuste as coordenadas conforme a posição da base
        for resource in resources:
            if not resource.collected:
                pygame.draw.circle(
                    screen,
                    resource.color,
                    (resource.x * 20 + 10, resource.y * 20 + 10),
                    6,
                )
        # Desenha os obstáculos (quadrados cinzas)
        for obstacle in obstacles:
            pygame.draw.rect(
                screen, constantes.BLACK, (obstacle.x * 20, obstacle.y * 20, 20, 20)
            )

        for agent in agents:
            agent.draw(screen)

        pygame.display.flip()
        simulation_step += 1
        clock.tick(constantes.FPS)

    # Imprimir resultados no final da simulação (opcional)
    for agent in agents:
        print(f"Agente {agent.color} coletou {agent.resources_collected} recursos.")

    pygame.quit()


if __name__ == "__main__":
    main()
