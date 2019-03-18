# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
import copy
import random
import time

from agent import Agent
from landscape import Landscape
from lot import Lot
import gc

class Simulation:
	def __init__(self, size=200, r1=3, r2=5, r3=10, r4=10, load_filename=None):
		self.landscape = Landscape(size, size, self, r1, r2, r3, r4, load_filename)
		if not load_filename:
			self.agents = []
			for i in range(100): #200
				self.add_agent(Agent(self.landscape, self))

	def step(self, phase, maNum=10, miNum=400, byNum=2000, brNum=5000, buNum=400, pDecay=0.75, tDecay=0.25, corNum=5):
		self.landscape.step(phase, maNum, miNum, byNum, brNum, buNum, pDecay, tDecay, corNum)
		killlist = []
		for agent in self.agents:
			agent.step(self.landscape)
			if agent.water < 0 or agent.resource < 0:
				killlist.append(agent)
		for agent in killlist:
			self.kill(agent)
		gc.collect()

	def add_agent(self, agent):
		self.agents.append(agent)

	def kill(self, agent):
		self.agents.remove(agent)
		self.landscape.remove_agent(agent)

	def view(self, step):
		return self.landscape.view(step)

	def output(self, filename):
		self.landscape.output(filename)
