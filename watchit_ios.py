'''
A simple analog clock made of ShapeNodes.
Includes slider UI to adjust the minutes, seconds and tenths of seconds.

To use internet clock time install stuff, see:
https://github.com/ywangd/stash
"import requests as r; exec(r.get('https://bit.ly/get-stash').content)"
Then
% launch_stash.py
> pip install ntplib
'''

from scene import *
import ui
from math import pi, sin, cos
from datetime import datetime,timedelta
import ntplib

class Clock (Scene):
	def setup(self):
		print('-----------', datetime.now())
		self.offset, sync_flag = self.get_offset()
		self.button_state = 0 # [0,1,2] for different slider range
		self.button_label = ["mins", "secs", "0.1s"]
		self.slider_loc=[0,0,0]
		#print("one")
		"""
		The lag is stored in a 3 address list: mins, seconds and 1/10 seconds. All with units [s]
		The corresponding slider positions [0,1] are stored in similar lists: slider_loc[:]
		The button_state is an integer to control which of the 3 addresses is being viewed.
		"""
		try:
			self.lag = Logging().load('log.txt')
			print("loaded log.txt, lag (s)=", self.lag_tot())
			self.slider_convert(self.lag, self.button_state, "seconds_to_slider")
			#print(self.slider_loc)
		except:
			print('log file not loaded')
			self.lag = [timedelta(seconds=0), timedelta(seconds=0), timedelta(seconds=0)] # Store the lag [mins,sec,sec/10]
			self.slider_loc = [0.5, 0.5, 0.5] # Store the slider location

		# Draw the clock
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
		#label = LabelNode("offset:"+str(self.offset.microseconds)+u"\u03bcs", font=('HelveticaNeue-UltraLight', 0.1*r))
		label = LabelNode("offset:"+str(self.offset.total_seconds())+"s", font=('HelveticaNeue-UltraLight', 0.1*r))
		if sync_flag == True:
			label.color = 'green'
		else:
			label.color = 'red'
		label.position = (0, 0.3*r)
		self.face.add_child(label)

		self.slider = self.view.superview.subviews[1]
		self.slider.continuous = True
		self.label1 = self.view.superview.subviews[2]
		self.button = self.view.superview.subviews[3]
		self.label2 = self.view.superview.subviews[4]
		self.button_save = self.view.superview.subviews[5]

		self.slider.action = self.slider_changed
		self.button.action = self.button_changed
		self.button_save.action = self.button_save_changed
		
		# Set initial Lag label value
		self.label2.text = str(self.lag_tot())+"s"
		# Set initial slider position (mins)
		self.slider.value = self.slider_loc[0]

	def lag_tot(self):
		"""
		sum datetime objects in self.lag and return as seconds
		"""
		return (self.lag[0]+self.lag[1]+self.lag[2]).total_seconds()

	def did_change_size(self):
		self.face.position = self.size/2

	def update(self):
		t = datetime.now() - self.offset + self.lag[0] + self.lag[1] + self.lag[2]
		tick = -2 * pi / 60.0
		seconds = t.second + t.microsecond/1000000.0
		minutes = t.minute + seconds/60.0
		hours = (t.hour % 12) + minutes/60.0
		self.hands[0].rotation = 5 * tick * hours
		self.hands[1].rotation = tick * minutes
		self.hands[2].rotation = tick * seconds
		#self.label2.text = self.picker.date.strftime('%H:%M:%S')

	def get_offset(self):
			'''
			Calculate the clock offset from true time
			+ : local clock is ahead
			- : local clock is behind
			'''
			try:
				x = ntplib.NTPClient()
				try:
					return datetime.now() - datetime.utcfromtimestamp(x.request('europe.pool.ntp.org').tx_time), True
				except:
					return timedelta(seconds=0), False
			except:
				return timedelta(seconds=0), False


	def slider_changed(self, sender):
		value = sender.superview['slider1'].value
		self.slider_convert(value, self.button_state, 'slider_to_seconds')
		#if self.button_state == 0:
		#	#value = int(sender.superview['slider1'].value*10-5)
		#	self.lag[0] = timedelta(seconds=int(value*10-5)*60)
		#elif self.button_state == 1:
		#	#value = int(sender.superview['slider1'].value*60-30)
		#	self.lag[1] = timedelta(seconds=int(value*60-30))
		#else:
		#	#value = round(sender.superview['slider1'].value*2-1,1)
		#	self.lag[2] = timedelta(seconds=round(value*2-1,1))

		self.slider_loc[self.button_state] = value
		#sender.superview['label2'].text = str((self.lag[0]+self.lag[1]+self.lag[2]).total_seconds())+"s"
		sender.superview['label2'].text = str(self.lag_tot())+"s"
		self.update()

	def slider_convert(self, value, button_state, direction):
		"""
		convert between slider values and seconds
		direction = [ 'slider_to_seconds', 'seconds_to_slider']
		populates either self.lag or self.slider_loc respectively
		"""
		#print (direction)
		if direction == "slider_to_seconds":
			if button_state == 0:
				self.lag[0] = timedelta(seconds=int(value*10-5)*60)
			elif button_state == 1:
				self.lag[1] = timedelta(seconds=int(value*60-30))
			elif button_state == 2:
				self.lag[2] = timedelta(seconds=round(value*2-1,1))
			else:
				print('not expecting that button_state')
		elif direction == "seconds_to_slider":
			#print('value=',value)
			#print((int(value[0].total_seconds()/60)+5)/10.)
			#if button_state == 0:
			self.slider_loc[0] = (int(value[0].total_seconds()/60)+5)/10.
			#elif button_state == 1:
			self.slider_loc[1] = (value[1].total_seconds() + 30)/60.
			#elif button_state == 2:
			self.slider_loc[2] = (value[2].total_seconds() + 1)/2.
			#print('self.slider_loc:',self.slider_loc)
			#timedelta(seconds=round(value*2-1,1))
			#else:
			#print('not expecting that button_state')
		pass


	def button_changed(self, sender):
		self.button_state = (self.button_state + 1) % 3
		sender.superview['label1'].text = str(self.button_label[self.button_state]) #str(self.button_state)
		sender.superview['slider1'].value = self.slider_loc[self.button_state]
		#sender.superview['button1'].title = str(self.button_label[self.button_state])
		self.update()

	def button_save_changed(self, sender):
		#Logging().save( str((self.lag[0]+self.lag[1]+self.lag[2]).total_seconds()) )
		Logging().save( str((self.lag_tot())), '{:.3f}'.format(self.offset.total_seconds()) )
		self.update()


class Logging (Clock):
	def setup(self, label):
		check_logfile('log.txt')
		pass

	def check_logfile(self, fname):
		#data = pd.read_csv(fname, header = None)
		#print(data)
		pass

	def load(self, fname):
		"""
		Load log file and return list of last slider values
		self.lag = Logging().load('log.txt')
		"""
		with open(fname, "r") as file:
			first_line = file.readline()
			for last_line in file:
				pass
		#print('last_line:',last_line)
		last_line = last_line.split(',')
		#for i in [0, 1, 2]:
		#	print('last_line[',str(i),']',last_line[i])
		
		timestamp = last_line[0]
		lag = float(last_line[1])
		offset = last_line[2]
		lag_mins = int(lag/60)
		lag_secs = int(lag-lag_mins*60)
		lag_dsec = lag - lag_mins*60 - lag_secs
		#print("loaded lag:", str(lag_mins), str(lag_secs), str(lag_dsec))
		return [timedelta(seconds=lag_mins*60), timedelta(seconds=lag_secs), timedelta(seconds=lag_dsec)]

	def save(self, label, offset):
		x = open('log.txt', 'a+')
		timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
		x.write(timestamp+","+label+","+offset+"\n")
		#x.write( label )
		x.close()


#run(Clock())
v = ui.load_view('watchit_ios.pyui')
v['sceneview'].scene = Clock()
#v['pickerview'].scene = Picker()
v.present('fullscreen')
