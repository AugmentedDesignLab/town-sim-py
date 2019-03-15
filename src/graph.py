# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
import argparse
from multiprocessing import Event, Queue, Process
import sys

from simulation import Simulation

phase2threshold = 200000
phase3threshold = 80000
gridSize = 200
cycles = 15
outputFile = "output.txt"
maNum = 10
miNum = 400
byNum = 2000
brNum = 5000
r1 = 3
r2 = 5
r3 = 10
r4 = 10
buNum = 400
pDecay = 0.75
tDecay = 0.25
corNum = 5

def run_simulation_inner_loop_noui(simulation, counter):
	p = sum(sum(simulation.landscape.prosperity, []))
	phase = 1
	for i in range(cycles):
		if i >= 5 and i < 10 and p > phase2threshold:
			phase = 2
		elif i >= 10 and p > phase3threshold:
			phase = 3
		simulation.step(phase, maNum=maNum, miNum=miNum, byNum=byNum, brNum=brNum)

def run_simulation_noui():
	simulation = Simulation(size=gridSize)
	counter = 0
	for i in range(10):
		counter += 1
		run_simulation_inner_loop_noui(simulation, counter)
	simulation.output(outputFile)
	exit(0)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--noui", action="store_true", help="Suppresses UI if set.")
	parser.add_argument("-o", "--output", type=int, help="Output file name. Default: output.txt.")
	parser.add_argument("-s", "--size", type=int, help="n for nxn grid. Default: 200.")
	parser.add_argument("-c", "--cycles", type=int, help="The number of full cycles to run before ending simulation in commandline. The simulation does not self-terminate when running in UI. Default: 15.")
	parser.add_argument("-p2", "--phase2", type=int, help="Minimum total prosperity to allow calculation for bypass roads. Default: 200000.")
	parser.add_argument("-p3", "--phase3", type=int, help="Minimum total prosperity to allow calculation for minor roads. Default: 80000.") 
	parser.add_argument("-ma", "--major", type=int, help="Minimum local prosperity for a new major road. Default: 10.")
	parser.add_argument("-mi", "--minor", type=int, help="Minimum local prosperity for a new minor road. Default: 400.")
	parser.add_argument("-by", "--bypass", type=int, help="Minimum local traffic for a new bypass segment. Default: 2000.")
	parser.add_argument("-br", "--bridges", type=int, help="Minimum local prosperity to cross water or exit lot. Default: 5000.")
	parser.add_argument("-bu", "--buildings", type=int, help="Minimum local prosperity for a new building node. Default: 400.")
	parser.add_argument("-r1", "--plot", type=int, help="Radial range for plot size. Default: 3.")
	parser.add_argument("-r2", "--local", type=int, help="Radial range for local range. Default: 5.")
	parser.add_argument("-r3", "--explore", type=int, help="Radial range for explore range. Default: 10.")
	parser.add_argument("-r4", "--majorroadrange", type=int, help="Radial range for major road range. Default: 10.")
	parser.add_argument("-dp", "--prosperityDecay", type=float, help="Rate of prosperity decay. Default: 0.75.")
	parser.add_argument("-dt", "--trafficDecay", type=float, help="Rate of traffic-density decay. Default: 0.25.")
	parser.add_argument("-co", "--correction", type=float, help="Correction to grid of new roads. Default: 5.")

	args = parser.parse_args()
	if args.output:
		outputFile = args.output
	if args.size:
		gridSize = args.size
	if args.cycles:
		cycles = args.cycles
	if args.phase2:
		phase2threshold = args.phase2
	if args.phase3:
		phase3threshold = args.phase3
	if args.major:
		maNum = args.major
	if args.minor:
		miNum = args.minor
	if args.bypass:
		byNum = args.bypass
	if args.bridges:
		brNum = args.bridges
	if args.buildings:
		buNum = args.buildings
	if args.plot:
		r1 = args.plot
	if args.local:
		r2 = args.local
	if args.explore:
		r3 = args.explore
	if args.majorroadrange:
		r4 = args.majorroadrange
	if args.prosperityDecay:
		pDecay = args.prosperityDecay
	if args.trafficDecay:
		tDecay = args.trafficDecay
	if args.correction:
		corNum = args.correction

	if args.noui is False:
		sys.argv = sys.argv[0:1]
		import kvui
		kvui.run_kv(outputFile, gridSize, phase2threshold, phase3threshold, maNum, miNum, byNum, brNum, r1, r2, r3, r4, buNum, pDecay, tDecay, corNum)
	else:
		# do no ui things
		print ("This might take a while.")
		run_simulation_noui()


