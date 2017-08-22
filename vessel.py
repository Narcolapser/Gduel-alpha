from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock
import math
import joystick

import kivy
kivy.require('1.9.0')


class Sun(Widget):
	pass

class Vessel(Widget):
	color = ListProperty([1,1,1])
	angle = NumericProperty(0)
	vx = NumericProperty(0)
	vy = NumericProperty(0)
	px = NumericProperty(0)
	py = NumericProperty(0)
	trail = []
	next_dot = 0
	dot_spacing = 2
	dot_limit = 120
	
	def __init__(self,px,py,vx,vy,color):
		super(Vessel,self).__init__()
		self.px = px
		self.py = py
		self.vx = vx
		self.vy = vy
		self.color = color
	
	def do_trail(self):
		if self.next_dot < self.dot_spacing:
			self.next_dot += 1
			return
		self.next_dot = 0
		if len(self.trail) > self.dot_limit:
			self.parent.remove_widget(self.trail.pop(0))
		dot = TrailDot()
		dot.x = self.center_x
		dot.y = self.center_y
		dot.color = self.color
		self.trail.append(dot)
		self.parent.add_widget(dot)

class TrailDot(Widget):
	color = ListProperty([1,1,1])
	pass

class Torpedo(Vessel):
	pass

class Ship(Vessel):
	name = "Ship"
	thrust = False
	brake = False
	thrust_multiplyer = 0.03
	launch_multiplyer = 5.0
	torpedos = []
	torpedo_limit = 3
	
	def do_thrust(self):
		ax = math.cos(math.radians(self.angle)) * self.thrust_multiplyer
		ay = math.sin(math.radians(self.angle)) * self.thrust_multiplyer
		self.vx += ax
		self.vy += ay
	
	def do_brake(self):
		ax = math.cos(math.radians(self.angle)) * self.thrust_multiplyer * (-1.0)
		ay = math.sin(math.radians(self.angle)) * self.thrust_multiplyer * (-1.0)
		self.vx += ax
		self.vy += ay
	
	def fire(self):
		vx = math.cos(math.radians(self.angle)) * self.launch_multiplyer + self.vx
		vy = math.sin(math.radians(self.angle)) * self.launch_multiplyer + self.vy
		x = self.px + math.cos(math.radians(self.angle)) * self.launch_multiplyer * 5
		y = self.py + math.sin(math.radians(self.angle)) * self.launch_multiplyer * 5
		torp = Torpedo(x,y,vx,vy,self.color)
		self.parent.torpedos.append(torp)
		self.parent.add_widget(torp)
		return torp
	
	def destroy_torp(self,torp):
		try:
			self.parent.remove_widget(torp)
		except ValueError:
			pass
		try:
			self.parent.torpedos.remove(torp)
		except ValueError:
			pass
	
	def fire_torpedo(self):
		if len(self.torpedos) >= self.torpedo_limit:
			return
		torp = self.fire()
		self.torpedos.append(torp)
	
	def destroyed_torp(self,torp):
		try:
			index = self.torpedos.index(torp)
			self.torpedos.pop(index)
			self.destroy_torp(torp)
		except:
			pass
	
	def destroy_all(self):
		for torp in self.torpedos:
			self.destroy_torp(torp)
		self.torpedos = []

