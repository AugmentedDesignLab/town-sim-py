import copy
import cv2
import numpy as np
from PIL import Image, ImageTk
from tkinter import Tk, Label

from agent import Agent
from landscape import Landscape
from lot import Lot
import mapgen

class Simulation:
	def __init__(self, tkwindow, label):
		self.landscape = Landscape(200, 200, self, tkwindow, label)
		self.agents = []
		for i in range(10): #200
			self.add_agent(Agent(self.landscape, self))

	def step(self, round):
		for agent in copy.copy(self.agents):
			agent.step(self.landscape)
			if agent.water < 0 or agent.resource < 0:
				self.kill(agent)
		self.landscape.step(round)

	def add_agent(self, agent):
		self.agents.append(agent)

	def kill(self, agent):
		self.agents.remove(agent)
		self.landscape.remove_agent(agent)

	def view(self, step):
		self.landscape.view(step)

	def output(self):
		self.landscape.output()

def mouse_call_back(event, x, y, flags, param):
	# this handles terminating the simulation (?)
	# and exporting to ..JSON?
	# wait until im window is responsive if it is not responding

	global end_sim

	if event == cv2.EVENT_LBUTTONDBLCLK:
		print("mouse double click!")
		end_sim = True

def run(simulation):
	global end_sim

	counter = 0
	while True:
		counter += 1
		round = 1
		print('{}-{}'.format(counter, round))
		for i in range(5):
			if end_sim:
				return
			if i % 1 == 0:
				simulation.view('{}-{}-{}'.format(counter, round, i))
				print(len(simulation.agents))
				print('prosperity: {}'.format(sum(sum(simulation.landscape.prosperity, []))))
	#			print(max(simulation.landscape.prosperity))
	#			print(max(simulation.landscape.traffic))
			simulation.step(round)

		p = sum(sum(simulation.landscape.prosperity, []))

		if p > 200000:
			round = 2
			print('{}-{}'.format(counter, round))

			for i in range(5):
				if end_sim:
					return
				if i % 1 == 0:
					simulation.view('{}-{}-{}'.format(counter, round, i))
					print(len(simulation.agents))
		#			print(max(simulation.landscape.prosperity))
		#			print(max(simulation.landscape.traffic))
				simulation.step(round)

		if p > 80000:
			round = 3
			print('{}-{}'.format(counter, round))

			for i in range(5):
				if end_sim:
					return
				if i % 1 == 0:
					simulation.view('{}-{}-{}'.format(counter, round, i))
					print(len(simulation.agents))
		#			print(max(simulation.landscape.prosperity))
		#			print(max(simulation.landscape.traffic))
				simulation.step(round)

if __name__ == "__main__":
	tkwindow = Tk()
	img = np.full((400, 800, 3), 0, np.uint8)
	image = Image.fromarray(img)
	imgtk = ImageTk.PhotoImage(image=image)
	label = Label(tkwindow, image=imgtk)
	label.pack()

	#cv2.namedWindow('town', 1)

	simulation = Simulation(tkwindow, label)
	end_sim = False

	cv2.setMouseCallback('town', mouse_call_back)

	run(simulation) # mouse left double click to terminate sim
	simulation.output()

	# thought: major roads divide into plots, plots' subdivision becomes minor roads?

	# subdivide long blocks
	# zoning (residential, commericial, rural...)
	# add entertainment value?
	# highways - ring roads are not "completing the circle" # this broke
	# geography

	#! output to json then import to sumo
	#simulation.view("generating terrain")
