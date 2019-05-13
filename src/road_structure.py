# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
from util import Type

class RoadSegment:
	def __init__(self, rnode1, rnode2, nodes, type, rs_list):
		self.rnode1 = rnode1
		self.rnode2 = rnode2
		self.type = type
		self.shape = []
		self.nodes = nodes

	def merge(self, rs2, match, rs_list, roadnodes):
		if self.type != rs2.type:
			return
		if self.rnode1 == match:
			self.shape.reverse()
			self.rnode1 = self.rnode2
		self.shape.append((match.x, match.y))
		self.nodes.append((match.x, match.y))
		if rs2.rnode2 == match:
			rs2.shape.reverse()
			rs2.rnode2 = rs2.rnode1
		self.shape.extend(rs2.shape)
		self.nodes.extend(rs2.nodes)
		self.rnode2 = rs2.rnode2
		rs_list.discard(rs2)
		roadnodes.remove(match)
		roadnodes.remove(match)
		
	def split(self, node, rs_list, roadnodes):
		roadnodes.append(node)
		roadnodes.append(node)
	
		i = 0
		while i < len(self.nodes) - 1:
			if self.nodes[i] == (node.x, node.y):
				break
			i += 1
		nodes1 = self.nodes[:i]
		nodes2 = self.nodes[i+1:]

		new_rs = RoadSegment(node, self.rnode2, nodes2, self.type, roadnodes)
		rs_list.add(new_rs)

		self.nodes = nodes1
		self.rnode2 = node
