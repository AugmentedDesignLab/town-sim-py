# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
import argparse
from multiprocessing import Event, Queue, Process

from simulation import Simulation

def run_simulation_inner_loop_noui(simulation, counter):
	p = sum(sum(simulation.landscape.prosperity, []))
	phase = 1
	for i in range(15):
		if i >= 5 and i < 10 and p > 200000:
			phase = 2
		elif i >= 10 and p > 80000:
			phase = 3
		simulation.step(phase)

def run_simulation_noui(size=200):
	simulation = Simulation(size=size)
	counter = 0
	for i in range(10):
		counter += 1
		run_simulation_inner_loop_noui(simulation, counter)
	simulation.output("output.txt")
	exit(0)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--noui", action="store_true")
	parser.add_argument("-s", "--size", type=int, help="side length of simulation grid")
        
	args = parser.parse_args()
	if args.noui is False:
		import kvui
		kvui.run_kv()
	else:
		# do no ui things
                print ("This will take a while. I'm not frozen, just slow.")
		run_simulation_noui(args.size)


