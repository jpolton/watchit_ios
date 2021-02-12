'''
A simple analog clock made of ShapeNodes.
'''

from scene import *
import ui
from math import pi, sin, cos
from datetime import datetime,timedelta
import ntplib

class Clock (Scene):
	def setup(self):
		self.offset, sync_flag = self.get_offset()
		r = min(self.size)/2 * 0.9
		circle = ui.Path.oval(0, 0, r*2, r*2)
		circle.line_width = 6
		shadow = ('black', 0, 0, 15)
		self.face = ShapeNode(circle, 'white', 'silver', shadow=shadow)
		self.add_child(self.face)
		for i in range(12):
			# add numbers
			label = LabelNode(str(i+1), font=('HelveticaNeue-UltraLight', 0.2*r))
			label.color = 'black'
			a = 2 * pi * (i+1)/12.0
			label.position = sin(a)*(r*0.8), cos(a)*(r*0.8)
			self.face.add_child(label)
			# add tick marks
			shape = ShapeNode(ui.Path.rounded_rect(0, 0, 4, r*0.1, 2), 'black')
			shape.position = sin(a)*(r*0.95), cos(a)*(r*0.95)
			shape.rotation = -a
			self.face.add_child(shape)
			for j in range(5):
				aa = a + 2 * pi * (j+1)/60.0
				shape = ShapeNode(ui.Path.rounded_rect(0, 0, 2, r*0.05, 2), 'black')
				shape.position = sin(aa)*(r*0.95), cos(aa)*(r*0.95)
				shape.rotation = -aa
				self.face.add_child(shape)
		self.hands = []
		hand_attrs = [(r*0.6, 8, 'black'), (r*0.9, 8, 'black'), (r*0.9, 4, 'red')]
		for l, w, color in hand_attrs:
			shape = ShapeNode(ui.Path.rounded_rect(0, 0, w, l, w/2), color)
			shape.anchor_point = (0.5, 0)
			self.hands.append(shape)
			self.face.add_child(shape)
		self.face.add_child(ShapeNode(ui.Path.oval(0, 0, 15, 15), 'black'))
		self.did_change_size()
		#self.offset = self.get_offset()
		# add offset as label
		label = LabelNode("offset:"+str(self.offset.microseconds)+u"\u03bcs", font=('HelveticaNeue-UltraLight', 0.1*r))
		if sync_flag == True:
			label.color = 'green'
		else:
			label.color = 'red'
		label.position = (0, 0.3*r)
		self.face.add_child(label)
		
		self.picker = self.view.superview.subviews[1]
		self.picker.mode = ui.DATE_PICKER_MODE_COUNTDOWN
		self.picker.objc_instance.secondInterval=5
		
		
		self.slider = self.view.superview.subviews[2]
		self.label1 = self.view.superview.subviews[3]
		self.button = self.view.superview.subviews[4]
		self.label2 = self.view.superview.subviews[5]
		
		self.picker.x = 0.9*r
			
		self.picker.action = self.picker_changed
		
	def did_change_size(self):
		self.face.position = self.size/2
		
	def update(self):
		t = datetime.now() - self.offset
		tick = -2 * pi / 60.0
		seconds = t.second + t.microsecond/1000000.0
		minutes = t.minute + seconds/60.0
		hours = (t.hour % 12) + minutes/60.0
		self.hands[0].rotation = 5 * tick * hours
		self.hands[1].rotation = tick * minutes
		self.hands[2].rotation = tick * seconds
		self.label2.text = self.picker.date.strftime('%H:%M:%S')
		
	def get_offset(self):
			'''
			Calculate the clock offset from true time
			+ : local clock is ahead
			- : local clock is behind
			'''
			x = ntplib.NTPClient()
			try:
				return datetime.now() - datetime.utcfromtimestamp(x.request('europe.pool.ntp.org').tx_time), True	
			except:
				return timedelta(seconds=0), False	
				
	def picker_changed(self, sender):
			self.update() 
				
					
#run(Clock())
v = ui.load_view('watchit_ios.pyui')
v['sceneview'].scene = Clock()
#v['pickerview'].scene = Picker()
v.present('fullscreen')
