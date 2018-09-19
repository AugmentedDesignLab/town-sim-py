import random
from util import Type

class Node:
	def __init__(self, x, y, landscape):
		self.landscape = landscape
		self.adjacent = set()
		self.neighbors = set()
		self.x = x
		self.y = y
		self.agents = []
		self.type = [Type.GREEN if random.random() > 0.5 else Type.FOREST]
		self.__plot = None
		self.__local = None
		self.__range = None
		self.__major_road_range = None
		self.lot = None

	def add_adjacent(self, node):
		self.adjacent.add(node)

	def add_neighbor(self, node):
		self.neighbors.add(node)

	def add_agent(self, agent):
		self.agents.append(agent)

	def remove_agent(self, agent):
		self.agents.remove(agent)

	def add_type(self, t):
		self.type.append(t)

	def rem_type(self, t):
		self.type.remove(t)

	def clear_type(self):
		if self in self.landscape.built:
			self.landscape.built.remove(self)
		self.type = []

	def add_prosperity(self, amt):
		self.landscape.prosperity[self.x][self.y] += amt

	def prosperity(self):
		return self.landscape.prosperity[self.x][self.y]

	def traffic(self):
		return self.landscape.traffic[self.x][self.y]

	def plot(self):
		if self.__plot is None:
			self.get_local()
		return self.__plot

	def local(self):
		if self.__local is None:
			self.get_local()
		return self.__local

	def range(self):
		if self.__range is None:
			self.get_local()
		return self.__range

	def major_road_range(self):
		if self.__major_road_range is None:
			self.get_local()
		return self.__major_road_range

	def get_local(self, plot = 3, local_range = 5, explore_range = 10, major_road_range = 10):
		local = set([self])
		for i in range(1, local_range + 1):
			local.update(set([e for n in [s for s in local] for e in n.neighbors if Type.WATER not in e.type]))
			if i == plot:
				self.__plot = list(local)
			if i == local_range:
				self.__local = list(local)

		local = set([self])
		for i in range(1, major_road_range + 1):
			local.update(set([e for n in [s for s in local] for e in n.neighbors]))

			if i == explore_range:
				self.__range = list(local)
			if i == major_road_range:
				self.__major_road_range = list(local)

	def get_lot(self):
		lot = set([self])
		for i in range(15):
			neighbors = set([e for n in [s for s in lot] for e in n.neighbors if (Type.GREEN in e.type or Type.FOREST in e.type or Type.BUILDING in e.type)])
			if len(neighbors - lot) == 0:
				break
			lot.update(neighbors)
		neighbors = set([e for n in [s for s in lot] for e in n.neighbors if (Type.GREEN in e.type or Type.FOREST in e.type or Type.BUILDING in e.type)])
		if len(neighbors - lot) == 0:
			return lot
		else:
			return None