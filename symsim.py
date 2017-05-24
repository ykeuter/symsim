from enum import Enum
import numpy as np

class Agent:
    def __init__(self, actions):
        self.actions = actions

    def perceive(self, state):
        i = np.random.randint(len(self.actions))
        return self.actions[i]

    def mate(self, agent2):
        return Agent(self.actions)

class World:
    class Action(Enum):
        UP, DOWN, LEFT, RIGHT, NIL = range(5)

    ACTIONS = list(Action)

    class SituatedAgent:
        def __init__(self, agent, x, y, strength):
            self.agent = agent
            self.x = x
            self.y = y
            self.strength = strength

    def __init__(self, size, productionRate, consumptionRate,
            initStrength, windowSize):
        self.resourceGrid = np.ones(size, size)
        self.agentGrid = np.zeros(size, size)
        self.tempAgentGrid = np.empty([size, size, len(ACTIONS) + 2],
                dtype=np.object)
        self.productionRate = productionRate
        self.consumptionRate = consumptionRate
        self.size = size
        self.windowSize = windowSize

        x1 = np.random.randint(size)
        y1 = np.random.randint(size)
        x2 = np.random.randint(size)
        y2 = np.random.randint(size)
        while x1 == x2 and y1 == y2:
            x2 = np.random.randint(size)
            y2 = np.random.randint(size)
        self.situatedAgents = [SituatedAgent(Agent(ACTIONS), x1, y1,
            initStrength), SituatedAgent(Agent(ACTIONS), x2, y2,
            initStrength)]
        for a in self.situatedAgents:
            self.agentGrid[a.x, a.y] = 1

    def getState2D(self, x, y, a):
        x1 = x - self.windowSize / 2
        x2 = x1 + self.windowSize
        y1 = y - self.windowSize / 2
        y2 = y1 + self.windowSize
        xx1 = max(x1, 0)
        xx2 = min(x2, self.size)
        yy1 = max(y1, 0)
        yy2 = min(y2, self.size)
        s = a[xx1:xx2, yy1:yy2]
        if x1 < 0:
            s = np.concatenate([a[x1:, yy1:yy2], s])
        if x2 > self.size:
            s = np.concatenate([s, a[:x2 - self.size, yy1:yy2]])
        if y1 < 0:
            ss = a[xx1:xx2, y1:]
            if x1 < 0:
                ss = np.concatenate([a[x1:, y1:], ss])
            if x2 > self.size:
                ss = np.concatenate([ss, a[:x2 - self.size, y1:]])
            s = np.concatenate([ss, s] axis=1)
        if y2 > self.size:
            ss = a[xx1:xx2, :y2 - self.size]
            if x1 < 0:
                ss = np.concatenate([a[x1:, :y2 - self.size], ss])
            if x2 > self.size:
                ss = np.concatenate([ss, a[:x2 - self.size, :y2 - self.size]])
            s = np.concatenate([s, ss] axis=1)
        return s

    def getState(self, x, y):
        return np.stack([self.getState2D(x, y, self.resourceGrid),
            self.getState2D(x, y, self.agentGrid)])

    def move(self, x, y, action):
        if action == Action.UP:
            y += 1
        elif action == Action.DOWN:
            y -= 1
        elif action == Action.LEFT:
            x -= 1
        elif action == Action.RIGHT:
            x += 1
        return x % self.size, y % self.size

    def moveBack(self, x, y, action):
        if action == Action.UP:
            y -= 1
        elif action == Action.DOWN:
            y += 1
        elif action == Action.LEFT:
            x += 1
        elif action == Action.RIGHT:
            x -= 1
        return x % self.size, y % self.size

    def breed(self, a):
        for i in xrange(self.size):
            for j in xrange(self.size):
                ag = self.tempAgentGrid[i, j, :len(ACTIONS)]
                idx = ~np.equal(ag, None)
                if np.sum(idx) < 2:
                    break
                elif np.sum(idx) == 2:
                    idx = np.where(idx)
                else:
                    v = np.zeros(len(ag))
                    v[idx] = [x.strength for x in ag[idx]]
                    idx = np.argsort(v)[-2:]
                parents = ag[idx]
                newborn = SituatedAgent(parents[0].agent.mate(parents[1].agent),
                        parents[0].x, parents[0].y,
                        (parents[0].strength + parents[1].strength) / 2)
                self.situatedAgents.append(newborn)
                self.tempAgentGrid[i, j, -2] = newborn
                parents[0].strength /= 2
                parents[1].strength /= 2
                self.tempAgentGrid[i, j, idx] = None
                parents[0].x, parents[0].y = self.moveBack(i, j, idx[0])
                self.tempAgentGrid[parents[0].x, parents[0].y, -1] = parents[0]
                parents[1].x, parents[1].y = self.moveBack(i, j, idx[1])
                self.tempAgentGrid[parents[1].x, parents[1].y, -1] = parents[1]

    def act(self):
        for agent in self.situatedAgents:
            action = agent.agent.perceive(self.getState(agent.x, agent.y))
            agent.x, agent.y = self.move(agent.x, agent.y, action)
            self.tempAgentGrid[agent.x, agent.y, action] = agent

    def battle(self):
        for i in xrange(self.size):
            for j in xrange(self.size):
                ag = self.tempAgentGrid[i, j, :]
                idx = ~np.equal(ag, None)
                if np.sum(idx) < 2:
                    break
                else:
                    ag = ag[idx]
                    v = [x.strength for x in ag]
                    idx = np.argsort(v)[:-1]
                    for a in ag[idx]:
                        a.strength = 0
        self.situatedAgents = filter(lambda a: a.strength > 0,
            self.situatedAgents)

    def consume(self):
        for a in self.situatedAgents:
            a.strength += self.resourceGrid[a.x, a.y] - self.consumptionRate
            self.resourceGrid[a.x, a.y] = 0
        self.situatedAgents = filter(lambda a: a.strength > 0,
            self.situatedAgents)

    def produce(self):
        self.resourceGrid[np.random.rand(self.size, self.size) <
                self.productionRate] = 1

    def step(self):
        # Reset
        self.tempAgentGrid[:,:,:] = None
        # Life cycle
        self.act()
        self.breed()
        self.battle()
        self.consume()
        self.produce()
        # Update
        self.agentGrid[:,:] = 0
        for a in self.situatedAgents:
            self.agentGrid[a.x, a.y] = 1

if __name__ == "__main__":
    SIZE = 10
    WINDOWSIZE = 3
    PRODRATE = .1
    CONSUMRATE = .1
    STRENGTH = 1
    NUMSTEPS = 100

    w = World(SIZE, PRODRATE, CONSUMRATE, STRENGTH, WINDOWSIZE)
    for i in xrange(NUMSTEPS):
        w.step()
        print(i)
