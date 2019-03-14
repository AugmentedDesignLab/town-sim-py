# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
from util import Type, get_line, get_pt_avg

class Lot:
	def __init__(self, landscape, points):
		self.landscape = landscape
		# self.neighbors = set() # neighbor lots, not currently used
		self.get_lot(points)

	def get_lot(self, points):
		[pt1, pt2] = points

		(ax, ay) = get_pt_avg(points)
		self.center = (cx, cy) = (int(ax), int(ay))
		center_node = self.landscape.array[cx][cy]

		lot = set([center_node])
		self.border = set()
		while True:
			neighbors = set([e for n in lot for e in n.adjacent if \
				e not in lot and e.lot is None and e.x != pt1[0] and e.x != pt2[0] and e.y != pt1[1] and e.y != pt2[1] \
				and Type.WATER not in e.type])
			if len(neighbors) > 0:
				lot.update(neighbors)
				self.border = neighbors
			else:
				break
		
		for node in lot:
			node.lot = self
		self.nodes = lot

	def get_nodes(self):
		return self.nodes



