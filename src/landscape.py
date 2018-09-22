import cv2
import numpy as np
from PIL import Image, ImageTk
import random
from tkinter import Tk, Canvas, Label

from lot import Lot
import mapgen
from node import Node
from road_structure import RoadSegment
from util import Type, get_line, check_turn_and_endpoint, check_overlapping_nodes
from util2 import get_closest_point, get_point_to_close_gap_minor, get_point_to_close_gap_major

class Landscape:
	def __init__(self, x, y, simulation, tkwindow, label):
		self.x = x
		self.y = y
		self.simulation = simulation
		self.tkwindow = tkwindow
		self.label = label
		self.array = [[Node(i, j, self) for j in range(y)] for i in range(x)]
		self.nodes = [node for row in self.array for node in row]
		self.prosperity = [[0 for j in range(y)] for i in range(x)]
		self.traffic = [[0 for j in range(y)] for i in range(x)]

		self.built = set()
		self.roads = []
		self.bypass_roads = [] # roads are bypass
		self.bypass_nodes = [] # bypass nodes are still waiting for more connections

		self.lots = set()

		self.init_geography()

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

		self.init_lots()
					
	def add_agent(self, agent):
		self.array[agent.x][agent.y].add_agent(agent)

	def remove_agent(self, agent):
		self.array[agent.x][agent.y].remove_agent(agent)

	def add_traffic(self, x, y, amt):
		self.traffic[x][y] += amt

	def traffic(self, x, y):
		return self.traffic[x][y]

	def init_geography(self):
		for i in range(145, 148):
			for j in range(0, 200):
				self.array[i][j].clear_type()
				self.array[i][j].add_type(Type.WATER)

		for i in range(135, 140):
			for j in range(115, 135):
				self.set_type_building([self.array[i][j]])

		self.set_type_road([(137, i) for i in range(115, 135)], Type.MAJOR_ROAD)

	def init_lots(self):
		self.lots.add(Lot(self, [(100, 100), (100, 150), (144, 150), (144, 100)]))

	def step(self, round):

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
				if round == 1:
					if (local_prosperity > 5000) and (len(list(set(node.range()) & set(self.roads))) == 0): #change to major road range for better effect
						# find closest road node, connect to it 
						self.set_new_road(i, j, Type.MAJOR_ROAD, True)
					elif (local_prosperity > 10) and (len(list(set(node.range()) & set(self.roads))) == 0):
						# find closest road node, connect to it 
						self.set_new_road(i, j, Type.MAJOR_ROAD)
					if local_prosperity > 400 and (len(list(set(node.plot()) & set(self.roads))) != 0):
						self.set_type_building(node.plot())

				elif round == 2:
				# bypasses
					if (local_traffic > 2000) and (len(list(set(node.range()) & set(self.roads))) == 0):
						#print("match conditions for adding bypass")
						self.set_new_bypass(i, j)

				# minor roads
				elif round == 3:
					if (local_prosperity > 400) and (len(list(set(node.plot()) & set(self.roads))) == 0): 
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
					node2 = n
					break

			points = get_line((x1, y1), (x2, y2))
			self.set_type_bypass(points, node, self.array[x2][y2])
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
			#print(points)
			if road_type == Type.MINOR_ROAD:
				self.set_type_road(points, road_type)
				points = get_point_to_close_gap_minor(x1, y1, self, points)
				if points is not None:
					self.set_type_road(points, road_type)
			elif road_type == Type.MAJOR_ROAD:
				self.set_type_road(points, road_type)
				points = get_point_to_close_gap_major(node, x1, y1, self, points)
				if points is not None:
					self.set_type_road(points, road_type)
			else:
				self.set_type_road(points[1:len(points) - 1], road_type)

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
		WATER_color = (255, 234, 167)
		FOREST_color = (0, 184, 148)
		GREEN_color = (85, 239, 196)
		BROWN_color = (178, 190, 195)
		BUILDING_color = (200, 247, 238)
		MAJOR_ROAD_color = (0, 0, 0)
		MINOR_ROAD_color = (80, 80, 80)
		BRIDGE_color = (19,69,139)
		CITY_GARDEN_color = (45, 136, 45)
		HIGHWAY_color = (0, 0, 255) # same as plot, but when I look at highways I probably don't want to show plot
		BYPASS_color = (183, 159, 0)
		AGENT_color = (0, 0, 255)
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
					img[i, j + self.y, 2] = self.array[i][j].prosperity() * 5

				if self.array[i][j].traffic() > 0:
					img[i, j + self.y, 1] = self.array[i][j].traffic() * 5

		for lot in self.lots:
			for (x, y) in lot.border:
				img[x, y + self.y] = PLOT_color

		#img = cv2.resize(img, (2000, 1000))
		img = cv2.resize(img, (800, 400))
		cv2.putText(img, str(step), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

		print("visualizing... ")

		image = Image.fromarray(img)
		imgtk = ImageTk.PhotoImage(image=image)
		self.label.configure(image=imgtk)
		self.tkwindow.update()

		#cv2.imshow('town', img)
		#cv2.waitKey(0)
		#cv2.waitKey(1)

	def output(self):
		turns = set()
		roadnodes = set()
		road_segments = set()

		for node in self.roads:
			check_turn_and_endpoint(node, self.roads, turns, roadnodes)

		# check for overlapping nodes
		roadnodes = check_overlapping_nodes(roadnodes)

		roads_no_replace = set(self.roads)
		for rnode in roadnodes:
			for node in (rnode.adjacent & roads_no_replace):
				rs = RoadSegment(rnode, node, turns, roadnodes, roads_no_replace)
				if rs.rnode2 is not None:
					road_segments.add(rs)

		for rs in road_segments:
			print("{},{},{}".format(
				(rs.rnode1.x, rs.rnode1.y),
				(rs.rnode2.x, rs.rnode2.y),
				rs.shape))