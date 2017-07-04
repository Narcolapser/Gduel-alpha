from kivy.uix.widget import Widget
from kivy.graphics import Ellipse
from kivy.graphics import Color
from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty
import math

class Pad(Widget):
	diameter = NumericProperty(50)
	pad_color = ListProperty([1,1,1,1])
	pad_width = NumericProperty(0)

class JoyStick (Widget):
	background_color = ListProperty([0.75,0.75,0.75,0.75])
	perimeter_color = ListProperty([0,0,0,0.75])
	perimeter_width = NumericProperty(6)
	pad_color = ListProperty([1,1,1,1])

	pad_x = NumericProperty(0.0)
	pad_y = NumericProperty(0.0)
	magnitude = NumericProperty(0.0)
	radians = NumericProperty(0.0)
	angle = NumericProperty(0.0)

	pad_callback = ListProperty([])
	pad_width = NumericProperty(50)
	_reach = NumericProperty(0)
	_perimeter_diameter = NumericProperty(0)
	
	def init(self,**kwargs):
		super(Joystick,self).__init__()

	def do_layout(self):
		if len(self.ids) > 0:
			self.ids.pad.center = self.center
			self.ids.pad.pad_color = self.pad_color
			self.ids.pad.pad_width = self.pad_width
		
		self._reach = self.width/2 if self.width < self.height else self.height/2
		self._perimeter_diameter = self.width/2 if self.width < self.height else self.height/2
		self._perimeter_diameter -= self.perimeter_width / 2
	
	def on_size(self, *args):
		self.do_layout()
		
	
	def on_pos(self, *args):
		self.do_layout()
	
	def add_widget(self, widget):
		super(JoyStick, self).add_widget(widget)
		self.do_layout()
	
	def remove_widget(self, widget):
		super(JoyStick, self).remove_widget(widget)
		self.do_layout()
	
	def move_pad(self,x,y):
		distance = ((self.center_x - x)**2 + (self.center_y - y) ** 2)**(0.5)
		if distance > self._reach - self.ids.pad.diameter/2:
			self.magnitude = 1.0
			new_distance = (self._reach - self.ids.pad.diameter/2) * 1.0 / distance
			new_x = -(self.center_x - x) * new_distance
			new_x = int(self.center_x + new_x)
			new_y = -(self.center_y - y) * new_distance
			new_y = int(self.center_y + new_y)
			self.ids.pad.center_x = new_x
			self.ids.pad.center_y = new_y
			#Output values
			self.pad_x = (x - self.center_x)*new_distance/(1.0*self._reach-self.pad_width/2.0)
			self.pad_y = (y - self.center_y)*new_distance/(1.0*self._reach-self.pad_width/2.0)
			
		else:
			self.magnitude = distance / self._reach
			self.ids.pad.center = (x,y)
			#Output values
			self.pad_x = (x - self.center_x)/(1.0*self._reach-self.pad_width/2.0)
			self.pad_y = (y - self.center_y)/(1.0*self._reach-self.pad_width/2.0)

		if self.pad_x == 0 and self.pad_y == 0:
			pass
		elif self.pad_x == 0:
			pass
		elif self.pad_y == 0:
			pass
		else:
			if self.pad_x > 0 and self.pad_y > 0:
				self.radians = math.atan(1.0*self.pad_y/self.pad_x)
			elif self.pad_x < 0 and self.pad_y > 0:
				self.radians = math.pi + math.atan(1.0*self.pad_y/self.pad_x)
			elif self.pad_x < 0 and self.pad_y < 0:
				self.radians = math.pi + math.atan(1.0*self.pad_y/self.pad_x)
			else:
				self.radians = math.pi*2 + math.atan(1.0*self.pad_y/self.pad_x)
			

		
		self.angle = math.degrees(self.radians)
		#print(self.angle,self.radians,self.magnitude)

		for callback in self.pad_callback:
			callback()

	def on_touch_down(self, touch):
		if self.collide_point(touch.x,touch.y):
			self.move_pad(touch.x,touch.y)
			touch.ud['pad'] = self
			return True
		return super(JoyStick, self).on_touch_down(touch)
	
	def on_touch_move(self,touch):
		if 'pad' in touch.ud:
			if touch.ud['pad'] == self:
				self.move_pad(touch.x,touch.y)
	
	def on_touch_up(self,touch):
		if 'pad' in touch.ud:
			if touch.ud['pad'] == self:
				self.move_pad(self.center_x,self.center_y)


Builder.load_string("""
<JoyStick>:
	canvas:
		Color:
			rgba: root.background_color
		Rectangle:
			pos: self.pos
			size: self.size
		Color:
			rgba: root.perimeter_color
		Line:
			circle: self.center_x, self.center_y, root._perimeter_diameter
			width: root.perimeter_width
	Pad:
		id: pad

<Pad>:
	canvas:
		Color:
			rgba: root.pad_color
		Ellipse:
			pos: self.center_x - root.pad_width/2, self.center_y - root.pad_width/2
			size: root.pad_width,root.pad_width
			id: pad
""")

