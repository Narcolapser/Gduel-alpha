from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty
import joystick

class Controller(BoxLayout):
	def __init__(self,**kwargs):
		super(Controller,self).__init__()
		self.js = joystick.JoyStick()
		self.add_widget(self.js)

class Sun(Widget):
	pass

class Ship(Widget):
	color = ListProperty([1,1,1])

class GameField (Widget):

	def __init__(self,**kwargs):
		super(GameField,self).__init__()
		self.p1 = Ship()
		self.p2 = Ship()
		self.sun = Sun()
		self.add_widget(self.p1)
		self.add_widget(self.p2)
		self.add_widget(self.sun)

	def do_layout(self):
		self.sun.center = self.center

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
	pass

class DuelApp (App):
	def build(self):
		game = Duel()
		return game
	
	def on_pause(self):
		return True
	
	def on_resume(self):
		pass

if __name__ == "__main__":
	app = DuelApp()
	app.run()
