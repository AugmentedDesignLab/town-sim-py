# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
from collections import Counter
import cv2
import numpy as np
from PIL import Image
import random

from lot import Lot
from node import Node
from road_structure import RoadSegment
from util import Type, get_line, check_turn_and_endpoint, check_overlapping_nodes
from util2 import get_closest_point, get_point_to_close_gap_minor, get_point_to_close_gap_major

class Landscape:
	def __init__(self, x, y, simulation):
		self.roadnodes = []
		self.roadsegments = set()
		self.x = x
		self.y = y
		self.simulation = simulation
		self.array = [[Node(i, j, self) for j in range(y)] for i in range(x)]
		self.nodes = [node for row in self.array for node in row]
		self.prosperity = [[0 for j in range(y)] for i in range(x)]
		self.traffic = [[0 for j in range(y)] for i in range(x)]

		self.built = set()
		self.roads = []
		self.bypass_roads = [] # roads are bypass
		self.bypass_nodes = [] # bypass nodes are still waiting for more connections

		self.lots = set()

		#make neighbors; a node should not be its own neighbor
		for i in range(x):
			for j in range(y):
				node = self.array[i][j]
				if i > 0:
					node.add_adjacent(self.array[i - 1][j])
					node.add_neighbor(self.array[i - 1][j])
				if j > 0:
					node.add_adjacent(self.array[i][j - 1])
					node.add_neighbor(self.array[i][j - 1])
				if i + 1 < x:
					node.add_adjacent(self.array[i + 1][j])
					node.add_neighbor(self.array[i + 1][j])
				if j + 1 < y:
					node.add_adjacent(self.array[i][j + 1])
					node.add_neighbor(self.array[i][j + 1])
				if i > 0 and j > 0:
					node.add_adjacent(self.array[i - 1][j - 1])
					node.add_neighbor(self.array[i - 1][j - 1])		
				if i + 1 < x and j > 0:
					node.add_adjacent(self.array[i + 1][j - 1])
					node.add_neighbor(self.array[i + 1][j - 1])
				if i > 0 and j + 1 < y:
					node.add_adjacent(self.array[i - 1][j + 1])
					node.add_neighbor(self.array[i - 1][j + 1])
				if i + 1 < x and j + 1 < y:
					node.add_adjacent(self.array[i + 1][j + 1])
					node.add_neighbor(self.array[i + 1][j + 1])

		self.init_geography()
					
	def add_agent(self, agent):
		self.array[agent.x][agent.y].add_agent(agent)

	def remove_agent(self, agent):
		self.array[agent.x][agent.y].remove_agent(agent)

	def add_traffic(self, x, y, amt):
		self.traffic[x][y] += amt

	def traffic(self, x, y):
		return self.traffic[x][y]

	def init_geography(self):
		# TODO
		# random.choices is better in python3.7
		[x1, x2] = random.sample(range(self.x), k=2)
		[y1, y2] = random.sample(range(self.y), k=2)
		(x1, x2) = self.init_main_st(x1, y1, x2, y2)

		pos = random.choice([x for x in range(self.x) if x not in range(x1, x2+1) and (abs(x-x1) < 25 and abs(x-x2) < 25) ])
		if pos + 3 in range(x1, x2+1):
			pos = range(pos, pos+3)
		else:
			pos = range(pos-3, pos)
		for i in pos:
			for j in range(self.y):
				self.array[i][j].clear_type()
				self.array[i][j].add_type(Type.WATER)

	def init_main_st(self, x1, y1, x2, y2):
		points = get_line((x1, y1), (x2, y2))
		endpt = min(20, len(points))
		points = points[0:endpt]
		(x1, y1) = points[0]
		(x2, y2) = points[endpt-1]
		self.set_type_road(points, Type.MAJOR_ROAD)
		self.roadsegments.add(RoadSegment(self.array[x1][y1], self.array[x2][y2]))
		for (x, y) in points:
			adjacent = self.array[x][y].adjacent
			adjacent = [s for n in adjacent for s in n.adjacent]
			for pt in adjacent:
				if pt not in points:
					self.set_type_building([self.array[pt.x][pt.y]])
		self.init_lots(x1, y1, x2, y2)
		return (x1, x2)

	def init_lots(self, x1, y1, x2, y2):
		(mx, my) = (int(x1 + x2)//2, int(y1 + y2)//2)
		mx1 = max(mx-25, 0)
		mx2 = min(mx+25, self.x-1)
		my1 = max(my-25, 0)
		my2 = min(my+25, self.y-1)

		self.lots.add(Lot(self, [(mx1, my1), (mx1, my2), (mx2, my2), (mx2, my1)]))

	def step(self, phase, maNum, miNum, byNum, brNum):
		#nodes = random.sample(self.nodes, int(len(self.nodes)/4))
		random.shuffle(self.nodes)
		for node in self.nodes:
			(i, j) = (node.x, node.y)
			if self.prosperity[i][j] > 0:
				self.prosperity[i][j] *= 0.75
			if self.traffic[i][j] > 0:
				self.traffic[i][j] *= 0.25

			# calculate roads
			if Type.GREEN in node.type or Type.FOREST in node.type \
				or Type.BUILDING in node.type:

				local_prosperity = sum([n.prosperity() for n in node.local()])
				local_traffic = sum([n.traffic() for n in node.range()])

				# major roads
				if phase == 1:
					if (local_prosperity > brNum) and (len(list(set(node.range()) & set(self.roads))) == 0): #change to major road range for better effect
						# find closest road node, connect to it 
						self.set_new_road(i, j, Type.MAJOR_ROAD, True)
					elif (local_prosperity > maNum) and (len(list(set(node.range()) & set(self.roads))) == 0):
						# find closest road node, connect to it 
						self.set_new_road(i, j, Type.MAJOR_ROAD)
					if local_prosperity > 400 and (len(list(set(node.plot()) & set(self.roads))) != 0):
						self.set_type_building(node.plot())

				elif phase == 2:
				# bypasses
					if (local_traffic > byNum) and (len(list(set(node.range()) & set(self.roads))) == 0):
						#print("match conditions for adding bypass")
						self.set_new_bypass(i, j)

				# minor roads
				elif phase == 3:
					if (local_prosperity > miNum) and (len(list(set(node.plot()) & set(self.roads))) == 0): 
						buildable = True
						for node in node.plot():
							if Type.BUILDING not in node.type:
								buildable = False
								break
						if buildable:
							# find closest road node, connect to it 
							self.set_new_road(i, j, Type.MINOR_ROAD)

					# calculate reservations of greenery
					if Type.FOREST in node.type or Type.GREEN in node.type:
						for n in node.neighbors:
							if n in self.built:
								lot = node.get_lot()
								if lot is not None:
									if random.random() < 0.1:
										self.set_type_city_garden(lot)
									else:
										self.set_type_building(lot)
								break

	def set_new_bypass(self, x1, y1):
		node = self.array[x1][y1]
		point = get_closest_point(node, self.lots, self.bypass_roads, Type.BYPASS, True)
		if point is not None:
			(x2, y2) = point
			node2 = self.array[x2][y2]
			for n in node2.local():
				if n in self.bypass_nodes:
					#node2 = n
					break

			points = get_line((x1, y1), (node2.x, node2.y))
			self.roadnodes.append(node)
			self.roadnodes.append(node2)
			self.roadsegments.add(RoadSegment(node, node2))

			self.set_type_bypass(points, node, node2)
		elif len(self.bypass_roads) == 0: # should only be true for the first bypass node (?)
			points = [(x1, y1)]
			self.set_type_bypass(points, node)
	
	def set_new_road(self, x1, y1, road_type, leave_lot = False):
		#print("try set road")
		node = self.array[x1][y1]
		point = get_closest_point(node, self.lots, self.roads, road_type, leave_lot)
		if point is not None:
			(x2, y2) = point
			points = get_line((x1, y1), (x2, y2))
			self.roadnodes.append(node)
			self.roadnodes.append(self.array[x2][y2])
			self.roadsegments.add(RoadSegment(node, self.array[x2][y2]))
			#print(points)
			self.set_type_road(points, road_type)
			if road_type == Type.MINOR_ROAD:
				point2 = get_point_to_close_gap_minor(x1, y1, self, points)
				if point2 is not None:
					(x2, y2) = point2
					self.roadnodes.append(node)
					self.roadnodes.append(self.array[x2][y2])
					self.roadsegments.add(RoadSegment(node, self.array[x2][y2]))

					points = get_line((x1, y1), point2)
					self.set_type_road(points, road_type)
			elif road_type == Type.MAJOR_ROAD:
				point2 = get_point_to_close_gap_major(node, x1, y1, self, points)
				if point2 is not None:
					(x2, y2) = point2
					self.roadnodes.append(node)
					self.roadnodes.append(self.array[x2][y2])
					self.roadsegments.add(RoadSegment(node, self.array[x2][y2]))

					points = get_line((x1, y1), point2)
					self.set_type_road(points, road_type)

	def set_type_bypass(self, points, node1, node2 = None):
		nodes = []
		for (x, y) in points:
			node = self.array[x][y]
			nodes.append(node)

		if len(list(set(nodes) & set(self.bypass_roads))) > 3:
			return

		for node in nodes:
			if Type.WATER in node.type:
				node.clear_type()
				node.add_type(Type.BRIDGE)
				node.add_type(Type.BYPASS)
			else:
				node.clear_type()
				node.add_type(Type.MAJOR_ROAD)
				node.add_type(Type.BYPASS)
			for road in self.roads:
				node.add_neighbor(road)
				road.add_neighbor(node)
			self.roads.append(node)
			self.bypass_roads.append(node)

		if node2 is not None:
			for node in (node1, node2):
				if node in self.bypass_nodes:
					self.bypass_nodes.remove(node)
					self.traffic[node.x][node.y] = 0
					for n in node.range():
						self.traffic[n.x][n.y] = 0
		
		#print("bypass added")

	def set_type_road(self, points, road_type):
		for (x, y) in points:
			node = self.array[x][y]

			#if node.lot is None:
			#	print ("setting road in non lot")
			if Type.WATER in node.type:
				node.clear_type()
				node.add_type(Type.BRIDGE)
			else:
				node.clear_type()
				node.add_type(road_type)
			for road in self.roads:
				node.add_neighbor(road)
				road.add_neighbor(node)
			self.roads.append(node)

	def set_type_building(self, nodes):
		for node in nodes:
			if Type.GREEN in node.type or \
				Type.BROWN in node.type or \
				Type.FOREST in node.type:
				node.clear_type()
				node.add_type(Type.BUILDING)
				self.built.add(node)

	def set_type_city_garden(self, nodes):
		for node in nodes:
			node.clear_type()
			node.add_type(Type.CITY_GARDEN)

	def view(self, step):
		WATER_color = (167, 234, 255)
		FOREST_color = (148, 184, 0)
		GREEN_color = (196, 239, 85)
		BROWN_color = (195, 190, 178)
		BUILDING_color = (238, 247, 200)
		MAJOR_ROAD_color = (0, 0, 0)
		MINOR_ROAD_color = (80, 80, 80)
		BRIDGE_color = (139,69,19)
		CITY_GARDEN_color = (45, 136, 45)
		HIGHWAY_color = (255, 0, 0) # same as plot, but when I look at highways I probably don't want to show plot
		BYPASS_color = (0, 159, 183)
		AGENT_color = (255, 0, 0)
		PLOT_color = (255, 0, 255)

		img = np.full((self.x, self.y * 2, 3), 0, np.uint8)
		for i in range(self.x):
			for j in range(self.y):
				node_type = self.array[i][j].type
				if Type.BUILDING in node_type:
					img[i, j] = BUILDING_color
				elif Type.MAJOR_ROAD in node_type:
					img[i, j] = MAJOR_ROAD_color
				elif Type.MINOR_ROAD in node_type:
					img[i, j] = MINOR_ROAD_color
				elif Type.BYPASS in node_type:
					img[i, j] = BYPASS_color
				elif Type.CITY_GARDEN in node_type:
					img[i, j] = CITY_GARDEN_color
				elif Type.BRIDGE in node_type:
					img[i, j] = BRIDGE_color
				#elif len(self.array[i][j].agents) > 0:
				#	img[i, j] = AGENT_color
				elif Type.FOREST in node_type:
					img[i, j] = FOREST_color 
				elif Type.GREEN in node_type:
					img[i, j] = GREEN_color 
				elif Type.WATER in node_type:
					img[i, j] = WATER_color
				elif Type.BROWN in node_type:
					img[i, j] = BROWN_color 

				if self.array[i][j].prosperity() > 0:
					img[i, j + self.y, 0] = self.array[i][j].prosperity() * 5

				if self.array[i][j].traffic() > 0:
					img[i, j + self.y, 1] = self.array[i][j].traffic() * 5

		for lot in self.lots:
			for (x, y) in lot.border:
				img[x, y + self.y] = PLOT_color

		img = cv2.resize(img, (2000, 1000))
		cv2.putText(img, str(step), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

		return img

	def output(self, filename):
		print("Calculating nodes...")
		rns = [(rn.x, rn.y) for rn in set(self.roadnodes)]
		counted = Counter()
		for rn in self.roadnodes:
			counted[rns.index((rn.x, rn.y))] += 1
		print("Calculating turns...")
		turns = set()
		for (x, y) in rns:
			if counted[rns.index((x, y))] == 2:
				turns.add(self.array[x][y])
		print("Reconstructing roads...")
		for turn in turns:
			rsarray = [rs for rs in self.roadsegments if rs.rnode1 == turn or rs.rnode2 == turn]
			if len(rsarray) > 2:
				rs1 = rsarray[0]
				rs2 = rsarray[1]
				rs1.merge(rs2, turn, self.roadsegments)
		with open(filename, "w") as file:
			for rs in self.roadsegments:
				print("{},{},{}".format(
					(rs.rnode1.x, rs.rnode1.y),
					(rs.rnode2.x, rs.rnode2.y),
					rs.shape), file=file)
		print("Output saved to file.")
