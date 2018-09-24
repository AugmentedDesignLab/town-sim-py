from enum import Enum
import math

class Type(Enum):
	WATER = 1
	FOREST = 2
	GREEN = 3
	BROWN = 4
	BUILDING = 5
	MAJOR_ROAD = 6
	MINOR_ROAD = 7
	BRIDGE = 8 
	CITY_GARDEN = 9
	HIGHWAY = 10
	BYPASS = 11

def get_line(start, end):
	# http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points

def get_pt_avg(points):
	x = sum(x for (x, y) in points) / len(points)
	y = sum(y for (x, y) in points) / len(points)
	return (x, y)

def check_turn_and_endpoint(node, roads, turns, roadnodes):
	neighbors = list(node.adjacent & set(roads))

	if (len(neighbors) == 2):
		left = neighbors[0]
		right = neighbors[1]

		# if point is part of a straight line it is not an endpoint or turn
		# if point is not part of straight line:
		if (node.x, node.y) != get_pt_avg([(left.x, left.y), (right.x, right.y)]):

			primary_road_type = None
			if Type.MAJOR_ROAD in node.type:
				primary_road_type = Type.MAJOR_ROAD
			elif Type.MINOR_ROAD in node.type:
				primary_road_type = Type.MINOR_ROAD
			elif Type.BRIDGE in node.type:
				primary_road_type = Type.BRIDGE
			else:
				print("Unexpected node type.")

			turns.add((node.x, node.y))
			print("found turn")

			'''
			# if neighbors of point are the same type
			if primary_road_type in left.type and primary_road_type in right.type:
				# it is a turn
				turns.add(node)
			# if neighbors of point are different types
			else:
				# it is an endpoint
				roadnodes.add(node)
			'''
	else:
		# if point has 1 or 3+ road-neighbors, it is an endpoint/junction	
		roadnodes.add(node)

def update_adjacents(old_node, new_node, adjacents):
	new_node.adjacent.update(adjacents)
	old_node.adjacent = old_node.adjacent - adjacents
	for n in adjacents:
		n.adjacent.add(new_node)
		n.adjacent.discard(old_node)

def check_overlapping_nodes(nodes):
	nodes_final = set([node for node in nodes])
	
	for node in nodes:
		if node in nodes_final:
			print("check overlap")
			check = node.adjacent.copy()
			while len(check) > 0:
				n = check.pop()
				if n in nodes_final:
					print("found overlap")
					nodes_final.remove(n)
					new_adjacents = n.adjacent - node.adjacent
					new_adjacents.discard(node)
					
					update_adjacents(n, node, new_adjacents)
					node.adjacent.discard(n)

					check.update(new_adjacents)
	
	return nodes_final
