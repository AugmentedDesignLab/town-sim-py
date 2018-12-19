# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
import copy
import time

from agent import Agent
from landscape import Landscape
from lot import Lot

class Simulation:
	def __init__(self, size=200):
		self.landscape = Landscape(size, size, self)
		self.agents = []
		for i in range(100): #200
			self.add_agent(Agent(self.landscape, self))

	def step(self, phase):
		for agent in copy.copy(self.agents):
			agent.step(self.landscape)
			if agent.water < 0 or agent.resource < 0:
				self.kill(agent)
		self.landscape.step(phase)

	def add_agent(self, agent):
		self.agents.append(agent)

	def kill(self, agent):
		self.agents.remove(agent)
		self.landscape.remove_agent(agent)

	def view(self, step):
		return self.landscape.view(step)

	def output(self, filename):
		self.landscape.output(filename)
