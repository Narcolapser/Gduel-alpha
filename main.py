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

from kivy.config import Config
Config.set('graphics', 'width', '768')
Config.set('graphics', 'height', '1024')

class Controls(BoxLayout):
	remaining_text = StringProperty("3")
	
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
		self.remaining_text = str(self.ship.torpedo_limit - len(self.ship.torpedos))

class Controller(BoxLayout):
	def __init__(self,**kwargs):
		super(Controller,self).__init__()
		self.js = joystick.Joystick()
		self.add_widget(self.js)

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

class GameField (Widget):

	torpedos = ListProperty([])
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
		
		#check for collisions:
		if self.p1.collide_widget(self.sun):
			self.game_over(self.p2,self.p1)
		if self.p2.collide_widget(self.sun):
			self.game_over(self.p1,self.p2)
			
		for torpedo in self.torpedos:
			if self.p1.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.game_over(self.p2,self.p1)
			if self.p2.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.game_over(self.p1,self.p2)
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
	
	def game_over(self,winner,looser):
		self.game_on = False
		App.get_running_app().game_over(winner)

	def _do_gravity(self,obj):
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

class DuelApp (App):
	def build(self):
		game = GameHost()
		self.game = game
		Clock.schedule_interval(game.update,1/60.0)
		return game
	
	def game_over(self,winner):
		if winner.name == 'player 1':
			winner_color = "Red"
		elif winner.name == 'player 2':
			winner_color = "Blue"
		else:
			winner_color = "you tied!"
			print(winner.name)
		content = Button(text='Congratulations {0}!\n\nPlay again!'.format(winner_color))
		popup = Popup(title='winner: '+winner.name,content=content, auto_dismiss=False)
		self.game.popup = popup
		content.bind(on_press=self.game.reset)
		popup.open()
	
	def on_pause(self):
		return True
	
	def on_resume(self):
		pass

if __name__ == "__main__":
	app = DuelApp()
	app.run()
