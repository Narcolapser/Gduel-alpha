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
from vessel import *

import kivy
kivy.require('1.9.0')

class Controls(BoxLayout):
	remaining_text = StringProperty("3")
	torpedo_limit = NumericProperty(3)
	
	def forward(self):
		self.ship.thrust = True

	def forward_release(self):
		self.ship.thrust = False

	def reverse(self):
		self.ship.brake = True

	def reverse_release(self):
		self.ship.brake = False

	def set_ship(self,ship):
		self.ship = ship
		self.ship.destroy_all()
		self.ship.controller = self
		self.ship.color = self.color
		self.ids.controller.js.pad_callback.append(self.turn)

	def turn(self):
		self.ship.angle = self.ids.controller.js.angle

	def fire(self):
		self.ship.fire_torpedo()
		self.update_remaining()

	def destroy(self):
		self.ship.destroy_all()
		self.update_remaining()
		
	def update_remaining(self):
		self.ship.set_torpedo_limit(self.torpedo_limit)
		self.remaining_text = str(self.ship.torpedo_limit - len(self.ship.torpedos))
	
	def set_torpedo_limit(self,val):
		self.remaining_text = str(val)
		self.torpedo_limit = val

class Controller(BoxLayout):
	def __init__(self,**kwargs):
		super(Controller,self).__init__()
		self.js = joystick.Joystick()
		self.add_widget(self.js)

class GameField (Widget):

	torpedos = ListProperty([])
	debris = ListProperty([])
	game_on = True

	def __init__(self,**kwargs):
		super(GameField,self).__init__()
		starting_speed = 4
		starting_distance = 250
		self.p1 = Ship((-1*starting_distance),0,0,starting_speed,[1,0.25,0.25])
		self.p1.name = "player 1"
		self.p1.angle = 0
		self.p2 = Ship(starting_distance,0,0,(-1*starting_speed),[0.25,0.25,1])
		self.p2.name = "player 2"
		self.p2.angle = 180
		self.sun = Sun()
		self.add_widget(self.p1)
		self.add_widget(self.p2)
		self.add_widget(self.sun)
		self.end_delay = 180 #replace this with an option
		self.end = 180
		self.ending = False


	def update(self):
		if not self.game_on:
			return False
		self._do_thrust(self.p1)
		self._do_gravity(self.p1)
		self.p1.do_trail()
		self._do_thrust(self.p2)
		self._do_gravity(self.p2)
		self.p2.do_trail()
		for torpedo in self.torpedos:
			self._do_gravity(torpedo)
			torpedo.do_trail()
		for d in self.debris:
			self._do_gravity(d)
		
		#check for collisions:
		if self.p1.collide_widget(self.sun):
#			self.game_over(self.p2,self.p1)
			self.ending = True
			self.winner = self.p2
			self.looser = self.p1
		if self.p2.collide_widget(self.sun):
#			self.game_over(self.p1,self.p2)
			self.ending = True
			self.winner = self.p1
			self.looser = self.p2
			
		for torpedo in self.torpedos:
			if self.p1.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.ending = True
				self.winner = self.p2
				self.looser = self.p1
			if self.p2.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.ending = True
				self.winner = self.p1
				self.looser = self.p2
			if self.sun.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.p1.destroyed_torp(torpedo)
				self.p2.destroyed_torp(torpedo)
			for col_torp in self.torpedos:
				if col_torp.collide_widget(torpedo) and torpedo != col_torp:
					self.remove_widget(torpedo)
					self.torpedos.remove(torpedo)
					self.remove_widget(col_torp)
					self.torpedos.remove(col_torp)
					self.p1.destroyed_torp(torpedo)
					self.p2.destroyed_torp(torpedo)
					self.p1.destroyed_torp(col_torp)
					self.p2.destroyed_torp(col_torp)

		if self.ending:
			if self.end_delay == self.end:
				self.looser.explode()
			if self.end <= 0:
				self.game_over(self.winner,self.looser)
				print("Ending game")
			else:
				print(self.end)
				self.end -= 1
	
	def game_over(self,winner,looser):
		self.game_on = False
		App.get_running_app().game_over(winner)

	def _do_gravity(self,obj):
		if obj.exploded:
			return
		dist_x = self.sun.center_x - obj.center_x
		dist_y = self.sun.center_y - obj.center_y
		distance = ((dist_x)**2 + (dist_y)**2)**(0.5)
		m = 20.0
		acc = m/distance
		ax = acc*(dist_x/distance)
		ay = acc*(dist_y/distance)
		obj.vx += ax
		obj.vy += ay
		obj.px += obj.vx
		obj.py += obj.vy
		obj.x += obj.vx
		obj.y += obj.vy
	
	def _do_thrust(self,obj):
		if obj.thrust:
			obj.do_thrust()
		if obj.brake:
			obj.do_brake()

	def do_layout(self):
		self.sun.center = self.center
		for child in self.children:
			if isinstance(child,Sun):
				child.width = 50
				child.height = 50
				continue
			elif isinstance(child,TrailDot):
				continue
			elif isinstance(child,Ship):
				child.width = 20
				child.height = 20
			else:
				child.width = 7
				child.height = 7
			child.center = (self.center_x + child.px, self.center_y + child.py)

	def on_size(self, *args):
		self.do_layout()

	def on_pos(self, *args):
		self.do_layout()

	def add_widget(self, widget):
		super(GameField, self).add_widget(widget)
		self.do_layout()

	def remove_widget(self, widget):
		super(GameField, self).remove_widget(widget)
		self.do_layout()

class Duel (FloatLayout):
	def update(self,val):
		self.ids.gameField.update()
		
	def do_layout(self,val):
		super(Duel,self).do_layout(val)
		self.ids.gameField.center = self.center
		if self.ids.player1Controller:
			self.ids.player1Controller.top = self.top
			self.ids.player1Controller.set_ship(self.ids.gameField.p1)
			try:
				self.ids.player1Controller.ids.controller.js.pad_color = self.ids.player1Controller.color
			except:
				pass
		if self.ids.player2Controller:
			self.ids.player2Controller.set_ship(self.ids.gameField.p2)
			try:
				self.ids.player2Controller.ids.controller.js.pad_color = self.ids.player2Controller.color
			except:
				pass

	def set_torpedo_limit(self,val):
		self.ids.player1Controller.set_torpedo_limit(val)
		self.ids.player2Controller.set_torpedo_limit(val)

class GameHost(BoxLayout):
	popup = None
	def __init__(self,**kwargs):
		super(GameHost,self).__init__(**kwargs)
		self.game = Duel()
		self.add_widget(self.game)
	
	def reset(self,val):
		self.clear_widgets()
		self.game = Duel()
		self.add_widget(self.game)
		if self.popup:
			self.popup.dismiss()
	
	def do_layout(self,val):
		super(GameHost,self).do_layout(val)
	
	def update(self,val):
		if self.game:
			self.game.update(val)

	def set_torpedo_limit(self,val):
		self.game.set_torpedo_limit(val)
