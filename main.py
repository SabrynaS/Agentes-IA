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


# Função para gerar as posições para recursos e obstáculos fora da base
def generate_valid_position():

    while True:
        x = random.randint(0, constantes.GRID_WIDTH - 1)
        y = random.randint(0, constantes.GRID_HEIGHT - 1)
        if not (0 <= x < 5 and 0 <= y < 5):  # Verifica se não está dentro da base
            return x, y


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (constantes.WINDOW_WIDTH, constantes.WINDOW_HEIGHT)
    )
    clock = pygame.time.Clock()
    env = simpy.Environment()

    # Criando obstáculos
    # Criando obstáculos
    obstacles = [Resource(*generate_valid_position(), "obstacle") for _ in range(10)]

    # Criando recursos
    resources = [Resource(*generate_valid_position(), "cristal") for _ in range(5)]
    resources.extend([Resource(*generate_valid_position(), "metais") for _ in range(5)])
    resources.extend(
        [Resource(*generate_valid_position(), "estrutura antiga", 2) for _ in range(5)]
    )

    agents = [
        SimpleAgent(env, 0, 0, resources, 0, 0, obstacles),
        GoalBasedAgent(env, 0, 0, resources, 0, 0, obstacles),
        StateBasedAgent(env, 1, 0, resources, 0, 0, obstacles),
        CooperativeAgent(env, 0, 1, resources, 0, 0, obstacles),
        BDIAgent(env, 2, 0, resources, 0, 0, obstacles),
    ]

    env.process(storm_cycle(env, agents))

    SIMULATION_TIME = 120
    simulation_step = 0

    running = True
    while running and simulation_step < constantes.FPS * SIMULATION_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        env.step()
        screen.fill(
            constantes.EARTH
            if not any(agent.in_storm for agent in agents)
            else constantes.RED
        )

        pygame.draw.rect(
            screen, constantes.MOSS_GREEN, (0 * 20, 0 * 20, 5 * 20, 5 * 20)
        )
        for resource in resources:
            if not resource.collected:
                pygame.draw.circle(
                    screen,
                    resource.color,
                    (resource.x * 20 + 10, resource.y * 20 + 10),
                    6,
                )

        for obstacle in obstacles:
            pygame.draw.rect(
                screen, constantes.BLACK, (obstacle.x * 20, obstacle.y * 20, 20, 20)
            )

        for agent in agents:
            agent.draw(screen)

        pygame.display.flip()
        simulation_step += 1
        clock.tick(constantes.FPS)

    for agent in agents:
        print(f"Agente {agent.color} coletou {agent.resources_collected} recursos.")

    pygame.quit()


if __name__ == "__main__":
    main()
