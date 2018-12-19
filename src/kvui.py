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

		p = Process(target=run_simulation, args=(queue, stop_request, output_request, pause_request, output))
		p.daemon = True
		p.start()
		if read_event is not None:
			read_event.cancel()
		read_event = Clock.schedule_interval(read_simulation, 5)

def button_pause(instance):
	global pause_btn, start_btn
	global output_request
	pause_btn.disabled = True
	start_btn.disabled = False

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
        
	e1 = Slider(min=-360., max=360.)
	l1 = Label(text='{}'.format(e1.value))
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
		layout01.add_widget(self.e1)
		layout01.add_widget(self.l1)
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

def run_simulation_inner_loop(queue, stop_request, simulation, counter):
	filename = "output.txt"
	p = sum(sum(simulation.landscape.prosperity, []))
	phase = 1
	for i in range(15):
		if stop_request.is_set():
			stop_request.clear()
			return 'stop'
		if i >= 5 and i < 10 and p > 200000:
			phase = 2
		elif i >= 10 and p > 80000:
			phase = 3
		queue.put(simulation.view('{}-{}-{}'.format(counter, phase, i)))
		simulation.step(phase)

def run_simulation(queue, stop_request, output_request, pause_request, output):
	simulation = Simulation()
	counter = 0
	while True:
		if output_request.is_set():
			simulation.output("output.txt")
			output.set()
			output_request.clear()
		if pause_request.is_set():
			pass
		counter += 1
		if run_simulation_inner_loop(queue, stop_request, simulation, counter) == 'stop':
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

def run_kv():
	global ui
	ui = UI()
	ui.run()