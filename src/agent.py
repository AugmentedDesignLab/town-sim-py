# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
import random
from util import Type, get_pt_avg

class Agent:
	water_max = 100
	resource_max = 1000

	def __init__(self, landscape, simulation, x = None, y = None):
		self.simulation = simulation
		self.landscape = landscape
		if x != None and y != None:
			self.x = x
			self.y = y
			self.node = landscape.array[x][y]
		else:
			node = random.choice(list(landscape.built))
			self.x = node.x
			self.y = node.y
			self.node = node
		self.node.add_agent(self)
		self.water = 10
		self.resource = 10

	def move(self, node):
		(ax, ay) = get_pt_avg([(self.x, self.y), (node.x, node.y)])
		(mid_x, mid_y) = (int(ax), int(ay))
		if len(set(self.landscape.array[mid_x][mid_y].local()) & set(self.landscape.bypass_roads)) == 0:
			self.landscape.add_traffic(mid_x, mid_y, 10)
		self.x = node.x
		self.y = node.y
		self.node.remove_agent(self)
		self.node = node
		node.add_agent(self)

	def step(self, landscape):
		self.water -= 1
		self.resource -= 1

		self.work()
		if len(self.node.agents) > 1:
			self.trade(random.choice(self.node.agents))
		self.rest(landscape)
		
		if self.water > 10 and self.resource > 10 and random.random() < 0.5:
			agent = Agent(landscape, self.simulation, self.x, self.y)
			self.water = agent.water = self.water / 2
			self.resource = agent.resource = self.resource / 2
			self.simulation.add_agent(agent)

	def water_price(self):
		if self.water < 4 or self.resource == 0:
			return float('inf')
		try:
			return (self.water_max / self.water) / (self.resource / self.resource_max) 
		except:
			print('error')
			return float('inf')

	def resource_price(self):
		if self.resource < 4 or self.water == 0:
			return float('inf')
		try:
			return (self.resource_max / self.resource) / (self.water / self.water_max)
		except:
			print('error_resource price')
			return float('inf')

	def traded_water(self, customer, paid, amt):
		self.water -= amt
		customer.water += amt
		self.resource += paid
		customer.resource -= paid

	def traded_resource(self, customer, paid, amt):
		self.resource -= amt
		customer.resource += amt
		self.water += paid
		customer.resource -= paid

	def trade(self, other):
		#trade price will be average of buy and sell value
		#print("trying to trade")
		if self is other:
			return
		if self.water > 4:
			p = self.water_price() 
			if p < other.water_price():
				amt = min(self.water - 4, other.water_max - other.water)
				if amt > 0:
					self.traded_water(other, p * amt, amt)
		if self.resource > 4:
			p = self.resource_price()
			if p < other.resource_price():
				amt = min(self.resource - 4, other.resource_max - other.resource)
				if amt > 0:
					self.traded_resource(other, p * amt, amt)

	def work(self):
		local = self.node.range()
		prioritize_water = True if self.water <= 2 else False
		
		if prioritize_water:
			places = self.node.water_neighbors()
			if len(places) > 0:
				place = random.choice(places)
				place.add_prosperity(10)
				self.move(place)
				gathered = max(self.water_max - self.water, 10)
				self.water += gathered
		else:
			places = self.node.resource_neighbors()
			if len(places) > 0:
				place = random.choice(places)
				if Type.BUILDING in place.type:
					place.add_prosperity(1)
				else:
					place.add_prosperity(10)
				self.move(place)
				gathered = max(self.resource_max - self.resource, 1 if Type.GREEN in place.type else 10)
				self.resource += gathered

	def rest(self, landscape):
		reachable_built = [node for node in self.node.range() if node in landscape.built]
		if len(reachable_built) == 0:
			self.simulation.kill(self)
			return
		else:
			node = random.choice(reachable_built)
			self.move(node)
			node.add_prosperity(10)
