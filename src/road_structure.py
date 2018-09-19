from util import Type

class RoadSegment:
	def __init__(self, rnode1, direction, turns, roadnodes, roads_no_replace):
		self.rnode1 = rnode1
		self.rnode2 = None
		self.type = direction.type
		self.shape = []
		self.find_next_rnode(direction, turns, roadnodes, roads_no_replace)

	def find_next_rnode(self, direction, turns, roadnodes, roads_no_replace):
		check = [direction]
		print("finding next rnode")
		while len(check) > 0:
			check_ = check[0]
			if check_ in turns:
				self.shape.append(check_)
			elif check_ in roadnodes and check_ is not self.rnode1:
				self.rnode2 = check_
				return

			roads_no_replace.remove(check_)
			check = [n for n in check_.adjacent if n in roads_no_replace and n is not self.rnode1]

		print("rnode 2 not found!")

