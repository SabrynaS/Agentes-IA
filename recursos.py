import random


class Resource:
    def __init__(self, x, y, resource_type, required_agents=1, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.type = resource_type
        self.collected = False
        self.value = {"cristal": 10, "estrutura_antiga": 50, "metais": 20}.get(
            resource_type, 0
        )
        self.required_agents = required_agents
        self.color = color


def storm_cycle(env, agents):
    while True:
        yield env.timeout(random.randint(25, 50))
        print("Tempestade iniciada!")
        for agent in agents:
            agent.in_storm = True
        yield env.timeout(5)
        print("Tempestade terminou!")
