from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock
import math
import joystick
from vessel import *
from game import *

import kivy
kivy.require('1.9.0')

from kivy.config import Config
Config.set('graphics', 'width', '768')
Config.set('graphics', 'height', '1024')

Config.read("duel.ini")
# set config
# Config.write()

class GameScreen(Screen):
	def run(self):
		print("RUN!")
		game = GameHost()
		self.game = game
		self.add_widget(self.game)
		Clock.schedule_interval(game.update,1/60.0)

class VictoryScreen(Screen):
	def __init__(self,winner=None,**kwargs):
		self.winner = winner
		if winner.name == 'player 1':
			self.winner_color = "Red"
		elif winner.name == 'player 2':
			self.winner_color = "Blue"
		else:
			self.winner_color = "you tied!"
		super(VictoryScreen,self).__init__(**kwargs)

	def again(self):
		gs = GameScreen(name='game_screen')
		self.parent.add_widget(gs)
		gs.run()
		self.parent.current = 'game_screen'
		self.parent.remove_widget(self)
	
	def menu(self):
		self.parent.current = 'main_menu'
		self.parent.remove_widget(self)

class RulesScreen(Screen):
	torpedo_count = NumericProperty(3)
	def __init__(self,**kwargs):
		super(RulesScreen,self).__init__(**kwargs)
		try:
			self.torpedo_count = Config.getint('duel','torpedo_count')
		except:
			pass
	
	def update_torpedo(self):
		Config.set('duel','torpedo_count',self.torpedo_count)
	
	def menu(self):
		self.parent.current = 'main_menu'
		self.parent.remove_widget(self)

class ShipScreen(Screen):
	pass

class MainMenuScreen(Screen):
	def new_game(self):
		gs = GameScreen(name='game_screen')
		self.parent.add_widget(gs)
		gs.run()
		self.parent.current = 'game_screen'
	
	def game_rules(self):
		rs = RulesScreen(name='rules_screen')
		self.parent.add_widget(rs)
		self.parent.current = 'rules_screen'

class DuelScreenManager(ScreenManager):
	
	def game_over(self,winner):
		victory = VictoryScreen(name='victory',winner=winner)
		gs = self.get_screen('game_screen')
		self.add_widget(victory)
		self.current = 'victory'
		self.remove_widget(gs)
		

class DuelApp (App):
	def build(self):
		self.sm = DuelScreenManager()
		self.main_menu_screen = MainMenuScreen(name='main_menu')
		self.sm.add_widget(self.main_menu_screen)
		self.build_config(self.config)
		return self.sm

	def game_over(self,winner):
		self.sm.game_over(winner)

	def on_pause(self):
		return True
	
	def on_resume(self):
		pass

	def build_config(self, config):
		config.setdefaults('duel', {
			'torpedo_count': 3})



if __name__ == "__main__":
	app = DuelApp()
	app.run()
