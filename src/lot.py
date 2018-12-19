# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
from util import Type, get_line, get_pt_avg

def get_border_pts(points):
	border = set()
	l = len(points)
	for i in range(l):
		border.update(set(get_line(points[i], points[(i + 1) % l])))
	return border

class Lot:
	def __init__(self, landscape, points):
		self.landscape = landscape
		self.neighbors = set() # neighbor lots, not currently used
		self.points = points
		self.get_lot()


	def get_lot(self):
		self.border = get_border_pts(self.points)

		(ax, ay) = get_pt_avg(self.points)
		self.center = (cx, cy) = (int(ax), int(ay))
		center_node = self.landscape.array[cx][cy]

		lot = set([center_node])
		while True:
			neighbors = set([e for n in [s for s in lot] for e in n.adjacent if \
				e not in lot and (e.x, e.y) not in self.border])
			if len(neighbors) > 0:
				lot.update(neighbors)
			else:
				break

		'''
		for (x, y) in self.border:
			try:
				lot.add(self.landscape.array[x][y])
			except:
				print(x)
				print(y)
				exit(1)
		'''
		lot.update(set([self.landscape.array[x][y] for (x, y) in self.border]))
		
		for node in lot:
			node.lot = self
		self.nodes = lot
		#print("new lot created with {} nodes!".format(len(self.nodes)))

	def get_nodes(self):
		return self.nodes



