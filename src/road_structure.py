from util import Type

class RoadSegment:
	def __init__(self, rnode1, rnode2):
		self.rnode1 = rnode1
		self.rnode2 = rnode2
		#self.type = direction.type
		self.shape = []

	def merge(self, rs2, match, rs_list):
		if self.rnode1 == match:
			self.shape.reverse()
			self.rnode1 = self.rnode2
		self.shape.append((match.x, match.y))
		if rs2.rnode2 == match:
			rs2.shape.reverse()
			rs2.rnode2 = rs2.rnode1
		self.shape.extend(rs2.shape)
		self.rnode2 = rs2.rnode2
		rs_list.discard(rs2)
