import copy
import cv2
from multiprocessing import Queue, Process
import numpy as np
from PIL import Image, ImageTk
import time
from tkinter import Tk, Label, Button

from agent import Agent
from landscape import Landscape
from lot import Lot
import mapgen

class Simulation:
	def __init__(self):
		self.landscape = Landscape(200, 200, self)
		self.agents = []
		for i in range(100): #200
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
		return self.landscape.view(step)

	def output(self, filename):
		self.landscape.output(filename)

def run_sim(queue, stop_request, output):
	simulation = Simulation()
	filename = "output.txt"

	counter = 0
	while True:
		counter += 1
		round = 1
		print('{}-{}'.format(counter, round))
		for i in range(5):
			if stop_request.empty() is False:
				queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
				simulation.output(filename)
				output.put(True)
				return
			if i % 1 == 0:
				queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
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
				if stop_request.empty() is False:
					queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
					simulation.output(filename)
					output.put(True)
					return
				if i % 1 == 0:
					queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
					print(len(simulation.agents))
		#			print(max(simulation.landscape.prosperity))
		#			print(max(simulation.landscape.traffic))
				simulation.step(round)

		if p > 80000:
			round = 3
			print('{}-{}'.format(counter, round))

			for i in range(5):
				if stop_request.empty() is False:
					queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
					simulation.output(filename)
					output.put(True)
					return
				if i % 1 == 0:
					queue.put(simulation.view('{}-{}-{}'.format(counter, round, i)))
					print(len(simulation.agents))
		#			print(max(simulation.landscape.prosperity))
		#			print(max(simulation.landscape.traffic))
				simulation.step(round)

def output_sim(tkwindow, output):
	global p

	if output.empty():
		tkwindow.after(500, output_sim, tkwindow, output)
	else:
		print("output done")
		p.terminate()
		while p.is_alive():
			time.sleep(0.1)
		print("Simulation is alive: {}".format(p.is_alive()))

def read_sim(tkwindow, label, queue):
	DELAY = 500

	if queue.empty():
		pass

	else:
		img = queue.get()
		image = Image.fromarray(img)
		imgtk = ImageTk.PhotoImage(image=image)
		label.config(image=imgtk)
		label.image = imgtk
		tkwindow.update()
	tkwindow.after(DELAY, read_sim, tkwindow, label, queue)

def button_start(tkwindow, label, start_button, end_button):
	global p

	queue = Queue()
	stop_request = Queue()
	output = Queue()
	end_button.stop_request = stop_request
	end_button.output = output

	DELAY = 500

	#print("Start click!")
	end_button.config(state = 'normal')
	start_button.config(state = 'disabled')

	p = Process(target=run_sim, args=(queue, stop_request, output))
	p.start()
	tkwindow.after(DELAY, read_sim, tkwindow, label, queue)

def button_stop(tkwindow, start_button, end_button):
	global p

	DELAY = 500

	#print("Stop click!")
	start_button.config(state = 'normal')
	end_button.config(state = 'disabled')
	end_button.stop_request.put(True)
	print("processing output...")
	tkwindow.after(DELAY, output_sim, tkwindow, end_button.output)

def button_exit():
	tkwindow.destroy()
	exit(0)

if __name__ == "__main__":
	end_sim = False

	tkwindow = Tk()
	img = np.full((1, 1, 3), 205, np.uint8) # placeholder
	image = Image.fromarray(img)
	imgtk = ImageTk.PhotoImage(image=image)
	label = Label(tkwindow, image=imgtk)
	label.image = imgtk
	label.grid(row = 0, column = 1, rowspan = 8)
	start = Button(width = 15, height = 1, text = "Start")
	start.grid(row = 2, column = 0, padx = 10)
	hide = Button(width = 15, height = 1, text = "Run in background", state = 'disabled')
	hide.grid(row = 4, column = 0, padx = 10)
	end = Button(width = 15, height = 1, text = "Stop and save", state = 'disabled')
	end.grid(row = 3, column = 0, padx = 10)

	start.config(command = lambda: button_start(tkwindow, label, start, end))
	end.config(command = lambda: button_stop(tkwindow, start, end))

	quit = Button(width = 15, height = 1, text = "Exit program", command = button_exit)
	quit.grid(row = 5, column = 0, padx = 10)

	tkwindow.mainloop()

	# thought: major roads divide into plots, plots' subdivision becomes minor roads?

	# subdivide long blocks
	# zoning (residential, commericial, rural...)
	# add entertainment value?
	# highways - ring roads are not "completing the circle" # this broke
	# geography

	#! output to json then import to sumo
	#simulation.view("generating terrain")

	#! clean code
	#! fix bugs...
