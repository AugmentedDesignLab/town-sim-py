# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
from collections import Counter
import cv2
import datetime
import numpy as np
import pickle
from PIL import Image
import random
from scipy.interpolate import splrep, splev
import sys

from lot import Lot
from node import Node
from road_structure import RoadSegment
from util import Type, get_line, check_turn_and_endpoint, check_overlapping_nodes
from util2 import get_closest_point, get_point_to_close_gap_minor, get_point_to_close_gap_major

class Landscape:
	def __init__(self, x, y, simulation, r1, r2, r3, r4, load_filename=None):
		self.roadnodes = []
		self.roadsegments = set()
		self.x = x
		self.y = y
		self.simulation = simulation

		self.built = set()
		self.roads = []
		self.bypass_roads = [] # roads are bypass
		self.bypass_nodes = [] # bypass nodes are still waiting for more connections

		self.lots = set()

		self.array = [[Node(i, j, self, r1, r2, r3, r4) for j in range(y)] for i in range(x)]
		self.nodes = [node for row in self.array for node in row]

		if load_filename is not None:
			self.load_state(load_filename)
			print('loaded state')
		else:
			self.prosperity = np.zeros((x, y)) 
			self.traffic = np.zeros((x, y)) 
			self.updateFlags = np.zeros((x, y))

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

	def init_geography(self):
		pts = self.get_water_body()
		while len(pts) < 10:
			pts = self.get_water_body()

		for (x, y) in pts:
			node = self.array[x][y]
			node.clear_type()
			node.add_type(Type.WATER)
			for n in node.neighbors:
				n.clear_type()
				n.add_type(Type.WATER)

		self.init_main_st(pts)

	def init_main_st(self, water_pts):
		(x1, y1) = random.choice(water_pts)
		n = self.array[x1][y1]
		n1_options = list(set(n.range()) - set(n.local()))
		n1 = np.random.choice(n1_options, replace=False)
		while Type.WATER in n1.type:
			n1 = np.random.choice(n1_options, replace=False)
		n2_options = list(set(n1.range()) - set(n1.local()))
		n2 = np.random.choice(n2_options, replace=False)
		points = get_line((n1.x, n1.y), (n2.x, n2.y))
		while any(Type.WATER in self.array[x][y].type for (x, y) in points):
			n2 = np.random.choice(n2_options, replace=False)
			points = get_line((n1.x, n1.y), (n2.x, n2.y))

		(x1, y1) = points[0]
		(x2, y2) = points[len(points)-1]
		self.set_type_road(points, Type.MAJOR_ROAD)
		self.roadsegments.add(RoadSegment(self.array[x1][y1], self.array[x2][y2]))
		for (x, y) in points:
			adjacent = self.array[x][y].adjacent
			adjacent = [s for n in adjacent for s in n.adjacent]
			for pt in adjacent:
				if pt not in points:
					self.set_type_building([self.array[pt.x][pt.y]])
		self.init_lots(x1, y1, x2, y2)

	def get_water_body(self):
		# make curvy water body
		widerange = self.x # assuming x and y are same size
		margin = int(0.4 * widerange)
		pts1 = random.sample(range(widerange), 7)
		pts2 = random.sample(range(margin, widerange-margin), 7)
		pts1[0] = 0
		pts1[len(pts1)-1] = widerange
		pts1 = sorted(pts1)
		pts = [pts1, pts2]
		random.shuffle(pts)
		f = splrep(pts1, pts2)
		pts = [(x, splev(x, f)) for x in np.arange(0, self.x, 0.25)]
		pts = [(x, y) for (x, y) in pts]

		# prune not continuous
		pruned_pts = []
		for i in range(len(pts)):
			if pts[i][0] < self.x and pts[i][0] >=0 and pts[i][1] >= 0 and pts[i][1] < self.y:
				if i == 0 or (abs(pts[i-1][0] - pts[i][0]) <=1 and abs(pts[i-1][1] - pts[i][1]) <=1):
					if i == len(pts)-1 or (abs(pts[i+1][0] - pts[i][0]) <=1 and abs(pts[i+1][1] - pts[i][1]) <=1):
						pruned_pts.append((int(pts[i][0]), int(pts[i][1])))

		if random.random() < 0.5:
			pruned_pts = [(y, x) for (x, y) in pruned_pts]

		return pruned_pts

	def init_lots(self, x1, y1, x2, y2):
		(mx, my) = (int(x1 + x2)//2, int(y1 + y2)//2)
		self.add_lot([(mx-25, my-25), (mx+25, my+25)])

	def add_lot(self, points):
		lot = Lot(self, points)
		if lot is not None:
			self.lots.add(lot)
			return True
		return False

	def step(self, phase, maNum, miNum, byNum, brNum, buNum, pDecay, tDecay, corNum):
		#nodes = random.sample(self.nodes, int(len(self.nodes)/4))
		self.prosperity *= pDecay
		self.traffic *= tDecay

		xInd, yInd = np.where(self.updateFlags > 0)
		indices = list(zip(xInd, yInd))
		random.shuffle(indices)
		for (i, j) in indices:
			self.updateFlags[i][j] = 0
			node = self.array[i][j]

			# calculate roads
			if not (Type.GREEN in node.type or Type.FOREST in node.type or Type.BUILDING in node.type):
				return

			node.local_prosperity = sum([n.prosperity() for n in node.local()])
			node.local_traffic = sum([n.traffic() for n in node.range()])

			road_found_far = len(set(node.range()) & set(self.roads))
			road_found_near = len(set(node.plot()) & set(self.roads))

			# major roads
			if node.local_prosperity > maNum and not road_found_far:
				# find closest road node, connect to it 
				if node.local_prosperity > brNum:
					self.set_new_road(i, j, Type.MAJOR_ROAD, leave_lot=True, correction=corNum)
				else:
					self.set_new_road(i, j, Type.MAJOR_ROAD, correction=corNum)
			if node.local_prosperity > buNum and road_found_near:
				self.set_type_building(node.plot())

			if phase >= 2:
			# bypasses
				if node.local_traffic > byNum and not road_found_far:
					self.set_new_bypass(i, j, corNum)

			# minor roads
			if phase >= 3:
				# find closest road node, connect to it 
				if node.local_prosperity > miNum and not road_found_near: 
					# if not len([n for n in node.plot() if Type.BUILDING not in n.type]):
					self.set_new_road(i, j, Type.MINOR_ROAD, correction=corNum)

				# calculate reservations of greenery
				elif Type.FOREST in node.type or Type.GREEN in node.type:
					if len(node.neighbors & self.built):
						lot = node.get_lot()
						if lot is not None:
							if random.random() < 0.5:
								self.set_type_city_garden(lot)
							else:
								self.set_type_building(lot)

	def set_new_bypass(self, x1, y1, correction):
		node = self.array[x1][y1]
		if len(self.bypass_roads) == 0: # should only be true for the first bypass node
			self.bypass_nodes.append(node)
			return 
		point, points = get_closest_point(node, self.lots, self.bypass_roads, Type.BYPASS, True, correction=correction)
		if point is None:
			return 
		(x2, y2) = point
		node2 = self.array[x2][y2]
		if len(set(node2.local()) & set(self.bypass_nodes)) > 0:
			return

		self.roadnodes.append(node)
		self.roadnodes.append(node2)
		self.roadsegments.add(RoadSegment(node, node2))

		self.set_type_bypass(points, node, node2)
	
	def set_new_road(self, x1, y1, road_type, leave_lot=False, correction=5):
		node = self.array[x1][y1]
		point, points = get_closest_point(node, self.lots, self.roads, road_type, leave_lot, correction=correction)
		if point is None:
			return 
		(x2, y2) = point
		self.roadnodes.append(node)
		self.roadnodes.append(self.array[x2][y2])
		self.roadsegments.add(RoadSegment(node, self.array[x2][y2]))

		self.set_type_road(points, road_type)

		point2 = None
		if road_type == Type.MINOR_ROAD:
			point2 = get_point_to_close_gap_minor(x1, y1, self, points)
		elif road_type == Type.MAJOR_ROAD:
			point2 = get_point_to_close_gap_major(node, x1, y1, self, points)

		if point2 is not None:
			(x2, y2) = point2
			self.roadnodes.append(node)
			self.roadnodes.append(self.array[x2][y2])
			self.roadsegments.add(RoadSegment(node, self.array[x2][y2]))

			points = get_line((x1, y1), point2)
			self.set_type_road(points, road_type)

	def set_type_bypass(self, points, node1, node2):
		nodes = []
		for (x, y) in points:
			node = self.array[x][y]
			nodes.append(node)

		if len(set(nodes) & set(self.bypass_roads)) > 2:
			return

		for node in nodes:
			node.clear_type()

			if Type.WATER in node.type:
				node.add_type(Type.BRIDGE)
				node.add_type(Type.BYPASS)
			else:
				node.add_type(Type.MAJOR_ROAD)
				node.add_type(Type.BYPASS)
			for road in self.roads:
				node.add_neighbor(road)
				road.add_neighbor(node)
			self.roads.append(node)
			self.bypass_roads.append(node)

		for node in (node1, node2):
			if node in self.bypass_nodes:
				self.bypass_nodes.remove(node)
			self.traffic[node.x, node.y] = 0
			for n in node.range():
				self.traffic[n.x, n.y] = 0

	def set_type_road(self, points, road_type):
		for (x, y) in points:
			node = self.array[x][y]

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

		img = np.full((self.x * 2, self.y, 3), 0, np.uint8)
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
				elif Type.FOREST in node_type:
					img[i, j] = FOREST_color 
				elif Type.GREEN in node_type:
					img[i, j] = GREEN_color 
				elif Type.WATER in node_type:
					img[i, j] = WATER_color
				elif Type.BROWN in node_type:
					img[i, j] = BROWN_color 

				# if len(self.array[i][j].agents) > 0:
				# 	img[i + self.x, j, 2] = 255

				if self.array[i][j].prosperity() > 0:
					img[i + self.x, j, 0] = self.array[i][j].prosperity() * 5

				if self.array[i][j].traffic() > 0:
					img[i + self.x, j, 1] = self.array[i][j].traffic() * 5

		for lot in self.lots:
			for n in lot.border:
				img[n.x + self.x, n.y] = PLOT_color

		img = cv2.resize(img, (1000, 2000))
		cv2.putText(img, str(step), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

		return img

	def output(self, filename):
		print("saving state...")
		currentDT = datetime.datetime.now()
		self.save_state("{}.p".format(currentDT.strftime("%Y%m%d%H%M%S")))
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

		'''
		space syntax analysis
		=====================
		k local neighborhood: 1 < k < l
		l maximum "shortest distance"
		'''
		with open('stats_' + filename, "w") as file:
			for junction in set([rs.rnode1 for rs in self.roadsegments] + [rs.rnode2 for rs in self.roadsegments]):
				connectivity = junction.get_connectivity(self.roadsegments)
				local_depth = junction.get_local_depth(self.roadsegments, 3)
				global_depth = junction.get_global_depth(self.roadsegments)
				print("({}, {}):  	connectivity: {},  	local depth: {},  	global depth: {}".format(
					junction.x, junction.y, connectivity, local_depth, global_depth), file=file)
		print("Stats saved to file.")

	def save_state(self, filename):
		sys.setrecursionlimit(1000)
		nodearray = [[(self.array[i][j].type) for j in range(self.y)] for i in range(self.x)]
		roadsegments = [(rs.rnode1.x, rs.rnode1.y, rs.rnode2.x, rs.rnode2.y) for rs in self.roadsegments]
		to_store = [nodearray, self.prosperity, self.traffic, roadsegments]
		pickle.dump(to_store, open(filename, "wb"))

	def load_state(self, filename):
		print("trying to load from file")
		# [nodearray, self.prosperity, self.traffic, self.roadnodes, self.roadsegments] = pickle.load(open(filename, "wb"))
		[nodearray, self.prosperity, self.traffic, roadsegments] = pickle.load(open(filename, "rb"))
		print("pickle loaded file")
		for i in range(len(nodearray)):
			for j in range(len(nodearray[0])):
				ntype = nodearray[i][j]
				self.array[i][j].type = ntype
				if Type.MAJOR_ROAD in ntype or Type.MINOR_ROAD in ntype or Type.BRIDGE in ntype or Type.BYPASS in ntype or Type.HIGHWAY in ntype:
					self.roadnodes.append(self.array[i][j])
					# need to make roadnodes neighbor to each other to continue running, but not needed for simply reconstructing
		print("finished loading nodes")
		for rs in roadsegments:
			(x1, y1, x2, y2) = rs
			self.roadsegments.add(RoadSegment(self.array[x1][y1], self.array[x2][y2]))
		print("finished loading road segments")
