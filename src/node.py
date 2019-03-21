# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
import random
from util import Type

class Node:
	def __init__(self, x, y, landscape, r1=3, r2=5, r3=10, r4=10):
		self.landscape = landscape
		self.adjacent = set()
		self.neighbors = set()
		self.x = x
		self.y = y
		self.agents = set()
		self.type = set([Type.GREEN if random.random() > 0.5 else Type.FOREST])
		self.__plot = None
		self.__local = None
		self.__range = None
		self.__major_road_range = None
		self.lot = None
		self.local_prosperity = 0
		self.plot_range = r1
		self.local_range = r2
		self.explore_range = r3
		self.maroad_range = r4
		self.__water_neighbors = []
		self.__resource_neighbors = []
		self.__built_resources = 0

	def built_resources(self):
		return self.__built_resources

	def water_neighbors(self):
		return self.__water_neighbors

	def resource_neighbors(self):
		return self.__resource_neighbors

	def add_adjacent(self, node):
		self.adjacent.add(node)

	def add_neighbor(self, node):
		self.neighbors.add(node)

	def add_agent(self, agent):
		self.agents.add(agent)

	def remove_agent(self, agent):
		self.agents.discard(agent)

	def add_type(self, t):
		self.type.add(t)

	def rem_type(self, t):
		self.type.discard(t)

	def clear_type(self):
		if self in self.landscape.built:
			self.landscape.built.discard(self)
		self.type.clear()

	def add_prosperity(self, amt):
		self.landscape.prosperity[self.x, self.y] += amt
		self.landscape.updateFlags[self.x, self.y] = 1

	def add_traffic(self, amt):
		self.landscape.traffic[self.x, self.y] += amt
		self.landscape.updateFlags[self.x, self.y] = 1

	def prosperity(self):
		return self.landscape.prosperity[self.x, self.y]

	def traffic(self):
		return self.landscape.traffic[self.x, self.y]

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
			self.get_range()
		return self.__range

	def major_road_range(self):
		if self.__major_road_range is None:
			self.get_range()
		return self.__major_road_range

	def get_local(self):
		local = set([self])
		for i in range(1, self.local_range + 1):
			new_neighbors = set([e for n in local for e in n.adjacent if e not in local if Type.WATER not in e.type])
			if len(new_neighbors) == 0:
				self.__plot = list(local)
				self.__local = list(local)
				break
			local.update(new_neighbors)
			if i == self.plot_range - 1:
				self.__plot = list(local)
			if i == self.local_range - 1:
				self.__local = list(local)

	def get_range(self):
		local = set([self])
		for i in range(1, self.explore_range + 1): #self.maroad_range + 1): maroad_range not used currently
			new_neighbors = set([e for n in local for e in n.neighbors if e not in local])
			if len(new_neighbors) == 0:
				self.__range = list(local)
				self.__water_neighbors = [l for l in self.__range if Type.WATER in l.type]
				self.__resource_neighbors = [l for l in self.__range if (Type.BUILDING in l.type and l.prosperity() > 300) or Type.FOREST in l.type or Type.GREEN in l.type]
				break
			local.update(new_neighbors)

			if i == self.explore_range - 1:
				self.__range = list(local)
				self.__water_neighbors = [l for l in self.__range if Type.WATER in l.type]
				self.__resource_neighbors = [l for l in self.__range if (Type.BUILDING in l.type and l.prosperity() > 300) or Type.FOREST in l.type or Type.GREEN in l.type]
			# if i == self.maroad_range:
			# 	self.__major_road_range = list(local)

		self.__built_resources = self.prosperity()  

	def get_lot(self):
		# finds enclosed green areas
		lot = set([self])
		new_neighbors = set()
		for i in range(5):
			new_neighbors = set([e for n in lot for e in n.adjacent if e not in lot and (Type.GREEN in e.type or Type.FOREST in e.type or Type.BUILDING in e.type)])
			accept = set([n for n in new_neighbors if Type.BUILDING not in n.type])
			if len(new_neighbors) == 0:
				break
			lot.update(accept)
		if len([n for n in new_neighbors if Type.BUILDING not in n.type]) == 0: #neighbors except self
			return lot
		else:
			return None

	def get_neighboring_junctions(self, roadsegments):
		neighboring_junctions = set()
		for rs in roadsegments:
			if rs.rnode1 == self:
				neighboring_junctions.add(rs.rnode2)
			elif rs.rnode2 == self:
				neighboring_junctions.add(rs.rnode1)
		return neighboring_junctions

	def get_connectivity(self, roadsegments):
		return len(self.get_neighboring_junctions(roadsegments))

	def get_local_depth(self, roadsegments, m):
		temp_set = set()
		temp_set.update(self.get_neighboring_junctions(roadsegments))
		count = len(temp_set)

		for i in range(2, m+1):
			temp_adjacents = set()
			for n in temp_set:
				temp_adjacents.update(n.get_neighboring_junctions(roadsegments))
			count += len(temp_adjacents - temp_set) * i
			temp_set.update(temp_adjacents)

		return count


	def get_global_depth(self, roadsegments):
		temp_set = set()
		temp_set.update(self.get_neighboring_junctions(roadsegments))
		count = len(temp_set)
		s = 1

		temp_adjacents = set()
		for n in temp_set:
			temp_adjacents.update(n.get_neighboring_junctions(roadsegments))

		while len(temp_adjacents - temp_set) > 0:
			s += 1
			count += len(temp_adjacents - temp_set) * s
			temp_set.update(temp_adjacents)
			temp_adjacents = set()
			for n in temp_set:
				temp_adjacents.update(n.get_neighboring_junctions(roadsegments))

		return count
