# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
import math

from lot import Lot
from util import Type, get_line

def get_closest_point(node, lots, road_segments, road_type, leave_lot, correction=5):
	# check if road can leave lot
	(x, y) = (node.x, node.y)
	nodes = road_segments
	
	# if not leave_lot:
	# 	if node.lot is None:
	# 		return None
	# 	nodes = set(road_segments) & node.lot.get_nodes()

	# filter out bridges
	nodes = [n for n in nodes if Type.BRIDGE not in n.type]

	if len(nodes) == 0:
		print("leave_lot = {} no road segments".format(leave_lot))

		return None, None

	dists = [math.hypot(n.x - x, n.y - y) for n in nodes]
	node2 = nodes[dists.index(min(dists))]
	(x2, y2) = (node2.x, node2.y)

	# if node.lot is not None and road_type is not Type.MINOR_ROAD:
	# 	if abs(x - x2) < correction:
	# 		x = x2
	# 		node = node.landscape.array[x][y]
	# 	elif abs(y - y2) < correction:
	# 		y = y2
	# 		node = node.landscape.array[x][y]

	if node.lot is None:
		if road_type is not Type.MINOR_ROAD and abs(x2 - x) > 10 and abs(y2 - y) > 10:
			if node2.lot is not None:
				(cx2, cy2) = node2.lot.center
				(x, y) = (x + x - cx2, y + y - cy2)

				if x >= node.landscape.x:
					x = node.landscape.x - 1
				if x < 0:
					x = 0
				if y >= node.landscape.y:
					y = node.landscape.y - 1
				if y < 0:
					y = 0

		# else:
		# 	(x2, y2) = (node2.x, node2.y)
				
			if abs(x2 - x) > 10 and abs(y2 - y) > 10: # and road_type is Type.MAJOR_ROAD:
				if not node.landscape.add_lot([(x2, y2), (x, y)]):
					print("leave_lot = {} add lot failed".format(leave_lot))

					return None, None
		# else:
		# 	print("leave_lot = {} proposed lot is too small{} or road is not MAJOR_ROAD{}".format(leave_lot, abs(x2 - x) > 10 and abs(y2 - y) > 10, road_type is Type.MAJOR_ROAD))

		# 	return None
		else:
			return None, None

	points = get_line((x, y), (node2.x, node2.y))
	if len(points) <=2:
		return None, None

	if not leave_lot:
		for (i, j) in points:
			if Type.WATER in node.landscape.array[i][j].type:
				return None, None

	return (node2.x, node2.y), points

def get_point_to_close_gap_minor(x1, y1, landscape, points):
	# connects 2nd end of minor roads to the nearest major or minor road

	(x_, y_) = points[1]
	x = x1 - x_
	y = y1 - y_
	(x2, y2) = (x1 + x, y1 + y)
	while True:
		if x2 >= landscape.x or y2 >= landscape.y or x2 < 0 or y2 < 0:
			break
		landtype = landscape.array[x2][y2].type
		if Type.GREEN in landtype or Type.FOREST in landtype or Type.WATER in landtype:
			break
		if Type.MAJOR_ROAD in landtype or Type.MINOR_ROAD in landtype and Type.BYPASS not in landtype:
			return (x2, y2)
		(x2, y2) = (x2 + x, y2 + y)

	return None

def get_point_to_close_gap_major(node, x1, y1, landscape, points):
	# extends a major road to the edge of a lot
	if node.lot is None:
		return None

	(x_, y_) = points[1]
	x = x1 - x_
	y = y1 - y_
	(x2, y2) = (x1 + x, y1 + y)

	border = node.lot.border

	while True:
		if x2 >= landscape.x or y2 >= landscape.y or x2 < 0 or y2 < 0:
			break
		landtype = landscape.array[x2][y2].type
		if Type.WATER in landtype:
			break
		if (x2, y2) in border:
			landtype = landscape.array[x2][y2].type
			return (x2, y2)
#		elif Type.MAJOR_ROAD in landtype:
#			return get_line((x1, y1), (x2, y2))
		(x2, y2) = (x2 + x, y2 + y)

	return None
