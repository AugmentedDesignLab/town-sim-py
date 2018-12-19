# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
import argparse
from multiprocessing import Event, Queue, Process

from simulation import Simulation

phase2threshold = 200000
phase3threshold = 80000
gridSize = 200

def run_simulation_inner_loop_noui(simulation, counter):
	p = sum(sum(simulation.landscape.prosperity, []))
	phase = 1
	for i in range(15):
		if i >= 5 and i < 10 and p > phase2threshold:
			phase = 2
		elif i >= 10 and p > phase3threshold:
			phase = 3
		simulation.step(phase)

def run_simulation_noui():
	simulation = Simulation(size=gridSize)
	print("gridSize is {}".format(gridSize))
	counter = 0
	for i in range(10):
		counter += 1
		run_simulation_inner_loop_noui(simulation, counter)
	simulation.output("output.txt")
	exit(0)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--noui", action="store_true", help="Suppresses UI if set. Commandline arguments do not affect parameters in simulation when UI is run.")
	parser.add_argument("-s", "--size", type=int, help="n for nxn grid. Default: 200.")
	parser.add_argument("-p2", "--phase2", type=int, help="Minimum total prosperity in the map to allow calculation for bypass roads. Default: 200000.")
	parser.add_argument("-p3", "--phase3", type=int, help="Minimum total prosperity in the map to allow calculation for minor roads. Default: 80000.") 
        
	args = parser.parse_args()
	if args.noui is False:
		# does not allow arguments at the moment
		import kvui
		kvui.run_kv()
	else:
		# do no ui things
		if args.size:
			gridSize = args.size
		if args.phase2:
			phase2threshold = args.phase2
		if args.phase3:
			phase3threshold = args.phase3

		print ("This will take a while. I'm not frozen, just slow.")
		run_simulation_noui()


