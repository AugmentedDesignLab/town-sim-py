# BSD 3-Clause License
#
# Copyright (c) 2018, Augmented Design Lab
# All rights reserved.
from io import BytesIO
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.image import Image as CoreImage
from kivy.graphics.instructions import Canvas
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as kiImage
from kivy.uix.label import Label
from kivy.uix.slider import Slider 
from multiprocessing import Event, Queue, Process
import numpy as np
from PIL import Image

from simulation import Simulation

Config.set('kivy', 'exit_on_escape', '0')

def button_start(instance):
	global p, queue, stop_request, output_request, pause_request, read_event, output
	global start_btn, pause_btn, stop_btn

	start_btn.disabled = True
	pause_btn.disabled = False
	stop_btn.disabled = False

	if pause_request is not None and pause_request.is_set():
		pause_request.clear()
	else:
		queue = Queue()
		stop_request = Event()
		output_request = Event()
		pause_request = Event()	
		output = Event()

		p = Process(target=run_simulation, args=(queue, stop_request, output_request, pause_request, output, ui.phase2threshold, ui.phase3threshold, ui.gridSize, ui.outputFile, ui.maNum, ui.miNum, ui.byNum, ui.brNum))
		p.daemon = True
		p.start()
		if read_event is not None:
			read_event.cancel()
		read_event = Clock.schedule_interval(read_simulation, 1)

def button_pause(instance):
	global pause_btn, start_btn
	global output_request
	pause_btn.disabled = True
	start_btn.disabled = False

	pause_request.set()
	output_request.set()
        
def button_exit(exit_btn):
	global ui
	ui.stop()
	exit(0)

def button_stop(instance):
	global start_btn, stop_btn, pause_btn
	global stop_request
	start_btn.disabled = False
	stop_btn.disabled = True
	pause_btn.disabled = True

	stop_request.set()

class UI(App):
	global kvbox
	global start_btn, pause_btn, stop_btn, exit_btn
	global p, queue, stop_request, output_request, pause_request, read_event, output
	read_event = pause_request = None

	phase2threshold = 200000
	phase3threshold = 80000
	gridSize = 200
	outputFile = "output.txt"
	maNum = 10
	miNum = 400
	byNum = 2000
	brNum = 5000

#	e1 = Slider(min=-360., max=360.)
#	l1 = Label(text='{}'.format(e1.value))
#	def trackSliderValue1(self, value):
#		l1.text = str(value)
#
#	e1.bind(value=trackSliderValue1)
	kvbox = BoxLayout()
	kvbox.size=[800., 400.]
	pause_btn = Button(text='Pause and Output to File', on_press=button_pause)
	stop_btn = Button(text='End Simulation', on_press=button_stop)
	start_btn = Button(text='Play Simulation', on_press=button_start)
	exit_btn = Button(text='Exit Program', on_press=button_exit)
        
	def build(self):
		layout = BoxLayout()
		layout01 = BoxLayout(orientation='vertical', size_hint_x=0.3)
		layout01.add_widget(start_btn)
		layout01.add_widget(pause_btn)
		pause_btn.disabled = True
		layout01.add_widget(stop_btn)
		stop_btn.disabled = True
#		layout01.add_widget(self.e1)
#		layout01.add_widget(self.l1)
		layout01.add_widget(exit_btn)
		layout.add_widget(layout01)

		layout02 = BoxLayout(orientation='vertical')
		img = np.full((1, 1, 3), 0, np.uint8) # placeholder
		imgIO = BytesIO()
		qr = Image.fromarray(img)
		qr.save(imgIO, format='png')
		imgIO.seek(0)
		imgData = BytesIO(imgIO.read())
		with kvbox.canvas:
			image = kiImage(source='', pos=kvbox.pos, size=kvbox.size)
			image.texture = CoreImage(imgData, ext='png').texture
		layout02.add_widget(kvbox)
		layout.add_widget(layout02)
		return layout

def run_simulation_inner_loop(queue, stop_request, simulation, counter, phase2threshold, phase3threshold, outputFile, maNum, miNum, byNum, brNum):
	p = sum(sum(simulation.landscape.prosperity, []))
	phase = 1
	for i in range(15):
		if output_request.is_set():
			simulation.output(outputFile)
			output.set()
			output_request.clear()
		if stop_request.is_set():
			stop_request.clear()
			return 1
		if pause_request.is_set():
			pass
		if i >= 5 and i < 10 and p > phase2threshold:
			phase = 2
		elif i >= 10 and p > phase3threshold:
			phase = 3
		queue.put(simulation.view('{}-{}-{}'.format(counter, phase, i)))
		simulation.step(phase, maNum=maNum, miNum=miNum, byNum=byNum, brNum=brNum)

def run_simulation(queue, stop_request, output_request, pause_request, output, phase2threshold, phase3threshold, gridSize, outputFile, maNum, miNum, byNum, brNum):
	simulation = Simulation(size=gridSize)
	counter = 0
	while True:
		if output_request.is_set():
			simulation.output(outputFile)
			output.set()
			output_request.clear()
		if pause_request.is_set():
			pass
		counter += 1
		if run_simulation_inner_loop(queue, stop_request, simulation, counter, phase2threshold, phase3threshold, outputFile, maNum, miNum, byNum, brNum) == 1:
			stop_request.clear()
			print("exiting subprocess")
			exit(0)

def read_simulation(dt):
	global queue, kvbox

	if queue.empty() != True:
		img = queue.get()
		imgIO = BytesIO()
		qr = Image.fromarray(img)
		qr.save(imgIO, format='png')
		imgIO.seek(0)
		imgData = BytesIO(imgIO.read())
		with kvbox.canvas:
			kvbox.canvas.clear()
			image = kiImage(source='', pos=kvbox.pos, size=kvbox.size)
			image.texture = CoreImage(imgData, ext='png').texture

def run_kv(o, g, phase2, phase3, ma, mi, by, br):
	global ui
	ui = UI()
	ui.outputFile = o
	ui.gridSize = g
	ui.phase2threshold = phase2
	ui.phase3threshold = phase3
	ui.maNum = ma
	ui.miNum = mi
	ui.byNum = by
	ui.brNum = br
	ui.run()
