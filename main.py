from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
import math
import joystick

class Controls(BoxLayout):
	
	def forward(self):
		print("Forward {0}!".format(self.ship.name))
		self.ship.thrust = True

	def forward_release(self):
		print("Forward_release {0}!".format(self.ship.name))
		self.ship.thrust = False
		
	def reverse_release(self):
		print("Reverse {0}!".format(self.ship.name))

	def reverse(self):
		print("Reverse_release {0}!".format(self.ship.name))
	
	def set_ship(self,ship):
		self.ship = ship
#		self.ids.controller.bind(self.ids.controller.js.pad_move,self.turn)
#		self.ids.controller.js.bind(on_pad_move=self.turn)
		self.ids.controller.js.pad_callback.append(self.turn)
	
	def turn(self):
#		print("Turning ship of {0}.".format(self.ship.name))
		self.ship.angle = self.ids.controller.js.angle
	
	def fire1(self):
		self.ship.fire1()

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
	
	def __init__(self,px,py,vx,vy,color):
		super(Vessel,self).__init__()
		self.px = px
		self.py = py
		self.vx = vx
		self.vy = vy
		self.color = color

class Ship(Vessel):
	name = "Ship"
	thrust = False
	brake = False
	thrust_multiplyer = 0.03
	launch_multiplyer = 1.0
	
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
	
	def fire1(self):
		vx = math.cos(math.radians(self.angle)) * self.launch_multiplyer + self.vx
		vy = math.sin(math.radians(self.angle)) * self.launch_multiplyer + self.vy
		x = self.px + math.cos(math.radians(self.angle)) * self.launch_multiplyer * 20
		y = self.py + math.sin(math.radians(self.angle)) * self.launch_multiplyer * 20
		print(x,y,vx,vy)
		torp = Torpedo(x,y,vx,vy,self.color)
#		print(torp.px,torp.py,torp.vx,torp.vy)
		self.parent.torpedos.append(torp)
		self.parent.add_widget(torp)

class Torpedo(Vessel):
	pass
#	def __init__(self,px,py,vx,vy):
#		super(Torpedo,self).__init__(px,py,vx,vy)
#		self.x = px
#		self.y = py

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
#		self._do_thrust(self.p1)
#		self._do_gravity(self.p1)
#		self._do_thrust(self.p2)
#		self._do_gravity(self.p2)


	def update(self):
		if not self.game_on:
			return False
		self._do_thrust(self.p1)
		self._do_gravity(self.p1)
		self._do_thrust(self.p2)
		self._do_gravity(self.p2)
		for torpedo in self.torpedos:
			self._do_gravity(torpedo)
		
		#check for collisions:
		if self.p1.collide_widget(self.sun):
			self.game_over(self.p2,self.p1)
		if self.p2.collide_widget(self.sun):
			self.game_over(self.p1,self.p2)
			
		#print(len(self.torpedos))
		for torpedo in self.torpedos:
#			print(torpedo.x,torpedo.y)
			if self.p1.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.game_over(self.p2,self.p1)
			if self.p2.collide_widget(torpedo):
				self.remove_widget(torpedo)
				self.torpedos.remove(torpedo)
				self.game_over(self.p1,self.p2)
	
	def game_over(self,winner,looser):
		self.game_on = False
#		self.remove_widget(looser)
#		self.clear_widgets()
#		App.get_running_app().game_over(winner)

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
			elif isinstance(child,Ship):
				child.width = 20
				child.height = 20
			else:
				child.width = 7
				child.height = 7
			child.center = (self.center_x + child.px, self.center_y + child.py)
#		self.p1.center = (self.center_x + self.p1.px, self.center_y + self.p1.py)
#		self.p2.center = (self.center_x + self.p2.px, self.center_y + self.p2.py)

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

class Duel (BoxLayout):
	def update(self,val):
		self.ids.gameField.update()
		
	def do_layout(self,val):
		super(Duel,self).do_layout(val)
		if self.ids.player1Controller:
			self.ids.player1Controller.set_ship(self.ids.gameField.p1)
		if self.ids.player2Controller:
			self.ids.player2Controller.set_ship(self.ids.gameField.p2)

class DuelApp (App):
	def build(self):
		game = Duel()
		self.game = game
		Clock.schedule_interval(game.update,1/60.0)
		return game
	
	def game_over(self,winner):
		self.game.clear_widgets()
		l = Label(text="Congratulations {0}!".format(winner.name))
		l.center = self.game.center
		self.game.add_widget(l)
	
	def on_pause(self):
		return True
	
	def on_resume(self):
		pass

if __name__ == "__main__":
	app = DuelApp()
	app.run()
