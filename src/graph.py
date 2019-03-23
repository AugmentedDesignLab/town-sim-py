# BSD 3-Clause License
#
# Copyright (c) 2019, Augmented Design Lab
# All rights reserved.
import argparse
import numpy as np
import sys

from simulation import Simulation

phase2threshold = 200000
phase3threshold = 80000
gridSize = 100
outputDir = None
maNum = 10
miNum = 400
byNum = 2000
brNum = 1000
r1 = 3
r2 = 5
r3 = 10
r4 = 10
buNum = 400
pDecay = 0.75
tDecay = 0.25
corNum = 5
load_filename = None

def resetParams():
	phase2threshold = 200000
	phase3threshold = 80000
	gridSize = 100
	outputDir = None
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
	load_filename = None

def run_simulation_noui():
	for town in range(10):
		print("start new simulation")
		simulation = Simulation(size=gridSize, r1=r1, r2=r2, r3=r3, r4=r4)
		for cycle in range(50):
			p = np.sum(simulation.landscape.prosperity)
			phase = 1
			for i in range(5):
				simulation.step(phase, maNum=maNum, miNum=miNum, byNum=byNum, brNum=brNum, buNum=buNum, pDecay=pDecay, tDecay=tDecay, corNum=corNum)

			if p > phase2threshold:
				phase = 2
			for i in range(5):
				simulation.step(phase, maNum=maNum, miNum=miNum, byNum=byNum, brNum=brNum, buNum=buNum, pDecay=pDecay, tDecay=tDecay, corNum=corNum)

			if p > phase3threshold:
				phase = 3
			for i in range(5):
				simulation.step(phase, maNum=maNum, miNum=miNum, byNum=byNum, brNum=brNum, buNum=buNum, pDecay=pDecay, tDecay=tDecay, corNum=corNum)
		simulation.landscape.output(outputDir)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--noui", action="store_true", help="Suppresses UI if set.")
	parser.add_argument("-o", "--output", type=str, help="Output directory. Default: current directory.")
	parser.add_argument("-s", "--size", type=int, help="n for nxn grid. Default: 100.")
	parser.add_argument("-c", "--cycles", type=int, help="The number of full cycles to run before ending simulation in commandline. The simulation does not self-terminate when running in UI. Default: 15.")
	parser.add_argument("-p2", "--phase2", type=int, help="Minimum total prosperity to allow calculation for bypass roads. Default: 200000.")
	parser.add_argument("-p3", "--phase3", type=int, help="Minimum total prosperity to allow calculation for minor roads. Default: 80000.") 
	parser.add_argument("-ma", "--major", type=int, help="Minimum local prosperity for a new major road. Default: 10.")
	parser.add_argument("-mi", "--minor", type=int, help="Minimum local prosperity for a new minor road. Default: 400.")
	parser.add_argument("-by", "--bypass", type=int, help="Minimum local traffic for a new bypass segment. Default: 2000.")
	parser.add_argument("-br", "--bridges", type=int, help="Minimum local prosperity to cross water or exit lot. Default: 1000.")
	parser.add_argument("-bu", "--buildings", type=int, help="Minimum local prosperity for a new building node. Default: 400.")
	parser.add_argument("-r1", "--plot", type=int, help="Radial range for plot size. Default: 3.")
	parser.add_argument("-r2", "--local", type=int, help="Radial range for local range. Default: 5.")
	parser.add_argument("-r3", "--explore", type=int, help="Radial range for explore range. Default: 10.")
	parser.add_argument("-r4", "--majorroadrange", type=int, help="Radial range for major road range. Default: 10.")
	parser.add_argument("-dp", "--prosperityDecay", type=float, help="Rate of prosperity decay. Default: 0.75.")
	parser.add_argument("-dt", "--trafficDecay", type=float, help="Rate of traffic-density decay. Default: 0.25.")
	parser.add_argument("-co", "--correction", type=float, help="Correction to grid of new roads. Default: 5.")
	parser.add_argument("-l", "--load", type=str, help="Load file name. Default: None.")

	phase2threshold = 200000
	phase3threshold = 80000
	gridSize = 100
	outputDir = None
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
	load_filename = None

	args = parser.parse_args()
	if args.noui:
		for times in range(10):
			print ("times = {}".format(times))
			# ma
			resetParams()
			for i in [5, 10, 15, 20, 50]:
				maNum = i
				outputDir = "output(s=100,{}={})".format("ma", i)
				run_simulation_noui()
			# mi
			resetParams()
			for i in [100, 200, 400, 800, 1000]:
				miNum = i
				outputDir = "output(s=100,{}={})".format("mi", i)
				run_simulation_noui()
			# by
			resetParams()
			for i in [800, 1000, 2000, 4000, 8000]:
				byNum = i
				outputDir = "output(s=100,{}={})".format("by", i)
				run_simulation_noui()
			# br
			resetParams()
			for i in [5000]:
				brNum = i
				outputDir = "output(s=100,{}={})".format("br", i)
				run_simulation_noui()
			# bu
			resetParams()
			for i in [100, 200, 400, 700, 1000]:
				buNum = i
				outputDir = "output(s=100,{}={})".format("bu", i)
				run_simulation_noui()
			# r1
			resetParams()
			for i in [1, 2, 3, 4, 5]:
				r1 = i
				outputDir = "output(s=100,{}={})".format("r1", i)
				run_simulation_noui()
			# r2
			resetParams()
			for i in [3, 5, 7, 9, 10]:
				r2 = i
				outputDir = "output(s=100,{}={})".format("r2", i)
				run_simulation_noui()
			# r3
			resetParams()
			for i in [5, 7, 10, 15, 20]:
				r3 = i
				outputDir = "output(s=100,{}={})".format("r3", i)
				run_simulation_noui()
			# dp
			resetParams()
			for i in [0.25, 0.5, 0.75, 0.9, 1]:
				pDecay = i
				outputDir = "output(s=100,{}={})".format("dp", i)
				run_simulation_noui()
			# dt
			resetParams()
			for i in [0.25, 0.5, 0.75, 0.9, 1]:
				tDecay = i
				outputDir = "output(s=100,{}={})".format("dt", i)
				run_simulation_noui()
			# co
			resetParams()
			for i in [1, 3, 5, 7, 9]:
				co = i
				outputDir = "output(s=100,{}={})".format("co", i)
				run_simulation_noui()
	else:
		if args.output:
			outputDir = args.output
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
		if args.load:
			load_filename = args.load

		sys.argv = sys.argv[0:1]
		import kvui
		kvui.run_kv(outputDir, gridSize, phase2threshold, phase3threshold, maNum, miNum, byNum, brNum, r1, r2, r3, r4, buNum, pDecay, tDecay, corNum, load_filename=load_filename)
