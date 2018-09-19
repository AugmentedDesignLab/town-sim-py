import math

from lot import Lot
from util import Type, get_line

def get_closest_point(node, lots, road_segments, road_type, leave_lot):
	# check if road can leave lot
	(x, y) = (node.x, node.y)
	nodes = None
	
	if not leave_lot:
		if node.lot is not None:
			nodes = [n for n in road_segments if n in node.lot.get_nodes()]
	else:
		nodes = road_segments
	
	if nodes is None or len(nodes) == 0:
		return None

	# filter out bridges
	nodes = [n for n in nodes if Type.BRIDGE not in n.type]

	dists = [math.hypot(n.x - x, n.y - y) for n in nodes]
	node2 = nodes[dists.index(min(dists))]
	(x2, y2) = (node2.x, node2.y)


	if road_type is not Type.MINOR_ROAD and not leave_lot and node.lot is not None:
		if abs(x - x2) < 5:
			x = x2
		elif abs(y - y2) < 5:
			y = y2
	node = node.landscape.array[x][y]

	if node.lot is None:
		if node2.lot is not None:
			(x2, y2) = node2.lot.center
			(x, y) = (x + x - x2, y + y - y2)

			if x >= node.landscape.x:
				x = node.landscape.x - 1
			if x < 0:
				x = 0
			if y >= node.landscape.y:
				y = node.landscape.y - 1
			if y < 0:
				y = 0

			#if abs(x2 - x) > 5 and abs(y2 - y) > 5:
				# should add a check for out of range
				# should make new lot only for parts where there was no old lot?
		else:
			(x2, y2) = (node2.x, node2.y)
			#if abs(x2 - x) > 5 and abs(y2 - y) > 5:
			
		if abs(x2 - x) > 10 and abs(y2 - y) > 10 and road_type is Type.MAJOR_ROAD:
			node.landscape.lots.add(Lot(node.landscape, [(x2, y2), (x2, y), (x, y), (x, y2)]))
		else:
			return None
	else:
		#print("lot already exists with {} nodes".format(len(node.lot.get_nodes())))
		pass

	return node2.x, node2.y

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
			return get_line((x1, y1), (x2, y2))
		(x2, y2) = (x2 + x, y2 + y)

	return None

def get_point_to_close_gap_major(node, x1, y1, landscape, points):
	# extends a major road to the edge of a lot
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
			return get_line((x1, y1), (x2, y2))
#		elif Type.MAJOR_ROAD in landtype:
#			return get_line((x1, y1), (x2, y2))
		(x2, y2) = (x2 + x, y2 + y)

	return None