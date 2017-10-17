from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithSidebar
from kivy.app import App
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.clock import Clock
from kivy import utils
import math
import joystick
import json
from os.path import join
from vessel import *
from game import *
from android.runnable import run_on_ui_thread

import kivy
kivy.require('1.9.0')

from kivy.config import Config
Config.set('graphics', 'width', '768')
Config.set('graphics', 'height', '1024')

class GameScreen(Screen):
	def run(self):
		game = GameHost()
		self.game = game
		self.add_widget(self.game)
		app = App.get_running_app()
		print("Name: " + app.get_application_name() + " Icon: " + app.get_application_icon())
		self.game.set_torpedo_limit(app.config.getint('Duel','torpedo_count'))
		Clock.schedule_interval(game.update,1/60.0)
		if utils.platform == 'android':
			HideButtons()

@run_on_ui_thread
def HideButtons():
	from jnius import autoclass
	activity = autoclass('org.kivy.android.PythonActivity').mActivity
	View = autoclass('android.view.View')
	decorView = activity.getWindow().getDecorView()
	flags = View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY \
			| View.SYSTEM_UI_FLAG_FULLSCREEN \
			| View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN \
			| View.SYSTEM_UI_FLAG_LAYOUT_STABLE \
			| View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION \
			| View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
	decorView.setSystemUiVisibility(flags)

class VictoryScreen(Screen):
	def __init__(self,winner=None,**kwargs):
		self.winner = winner
		if winner.name == 'player 1':
			self.winner_color = "Red"
			app = App.get_running_app()
			score = int(app.red_score) +1
			app.red_score = str(score)
		elif winner.name == 'player 2':
			self.winner_color = "Blue"
			app = App.get_running_app()
			score = int(app.blue_score) +1
			app.blue_score = str(score)
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

settings_json = json.dumps([
	{'type':'numeric',
	'title':'Torpedo Limit',
	'section': 'Duel',
	'key':'torpedo_count'}
	])

class DuelApp (App):
	blue_score = StringProperty("0")
	red_score = StringProperty("0")
	
	def build(self):
		self.icon = 'assets/duel_512.png'
		data_dir = getattr(self, 'user_data_dir')
		self.data_dir = data_dir
		#self.build_config(self.config)
		print("torpedo count set",join(data_dir,"duel.ini"))
		self.settings_cls = SettingsWithSidebar
		try:
			val = self.config.getint('Duel','torpedo_count')
			print("Getting torpedo count: ",val)
		except:
			self.config.write()
			print("error Getting torpedo count: ")
		self.use_kivy_settings = False
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
		data_dir = getattr(self, 'user_data_dir')
		config.read(join(data_dir,"duel.ini"))
		config.setdefaults('Duel', {
			'torpedo_count': 3})
	
	def build_settings(self, settings):
		settings.add_json_panel('Space Duel Rules',
								self.config,
								data=settings_json)

if __name__ == "__main__":
	app = DuelApp()
	app.run()
