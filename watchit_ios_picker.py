'''
WORK IN PROGRESS

A simple analog clock made of ShapeNodes.
Includes custom picker UI to adjust the lag with true time.

To use internet clock time install stuff, see:
https://github.com/ywangd/stash
'''

from scene import *
import ui
from math import pi, sin, cos
from datetime import datetime,timedelta
import ntplib
from objc_util import ObjCInstance, c, ObjCClass, ns, create_objc_class, NSObject
from ctypes import c_void_p
import arrow



# Data for four pickers
_data = [
    #[str(x) for x in range(0,10)],
    #[str(x) for x in range(0, 24)],
    [str(x) for x in range(0,60)],
    [str(x) for x in range(0,60)],
]

# ObjC classes
UIColor = ObjCClass('UIColor')
UIPickerView = ObjCClass('UIPickerView')
UIFont = ObjCClass('UIFont')
NSAttributedString = ObjCClass('NSAttributedString')


# Default attributes, no need to recreate them again and again
def _str_symbol(name):
    return ObjCInstance(c_void_p.in_dll(c, name))


_default_attributes = {
    _str_symbol('NSFontAttributeName'): UIFont.fontWithName_size_(ns('Courier'), 16),
    _str_symbol('NSForegroundColorAttributeName'): UIColor.blackColor(),
    _str_symbol('NSBackgroundColorAttributeName'): UIColor.whiteColor()
}


# Data source & delegate methods
def pickerView_attributedTitleForRow_forComponent_(self, cmd, picker_view, row, component):
    tag = ObjCInstance(picker_view).tag()
    return NSAttributedString.alloc().initWithString_attributes_(ns(_data[tag - 1][row]), ns(_default_attributes)).ptr


def pickerView_titleForRow_forComponent_(self, cmd, picker_view, row, component):
    tag = ObjCInstance(picker_view).tag()
    return ns(_data[tag - 1][row]).ptr


def pickerView_numberOfRowsInComponent_(self, cmd, picker_view, component):
    tag = ObjCInstance(picker_view).tag()
    return len(_data[tag - 1])


def numberOfComponentsInPickerView_(self, cmd, picker_view):
    return 1


def rowSize_forComponent_(self, cmd, picker_view, component):
    return 100


def pickerView_rowHeightForComponent_(self, cmd, picker_view, component):
    return 30


def pickerView_didSelectRow_inComponent_(self, cmd, picker_view, row, component):
    tag = ObjCInstance(picker_view).tag()
    print(f'Did select {_data[tag - 1][row]}')


methods = [
    numberOfComponentsInPickerView_, pickerView_numberOfRowsInComponent_,
    rowSize_forComponent_, pickerView_rowHeightForComponent_, pickerView_attributedTitleForRow_forComponent_,
    pickerView_didSelectRow_inComponent_
]

protocols = ['UIPickerViewDataSource', 'UIPickerViewDelegate']


UIPickerViewDataSourceAndDelegate = create_objc_class(
    'UIPickerViewDataSourceAndDelegate', NSObject, methods=methods, protocols=protocols
)


# UIPickerView wrapper which behaves like ui.View (in terms of init, layout, ...)
class UIPickerViewWrapper(ui.View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._picker_view = UIPickerView.alloc().initWithFrame_(ObjCInstance(self).bounds()).autorelease()
        ObjCInstance(self).addSubview_(self._picker_view)

    def layout(self):
        self._picker_view.frame = ObjCInstance(self).bounds()

    @property
    def tag(self):
        return self._picker_view.tag()

    @tag.setter
    def tag(self, x):
        self._picker_view.setTag_(x)

    @property
    def delegate(self):
        return self._picker_view.delegate()

    @delegate.setter
    def delegate(self, x):
        self._picker_view.setDelegate_(x)

    @property
    def data_source(self):
        return self._picker_view.dataSource()

    @data_source.setter
    def data_source(self, x):
        self._picker_view.setDataSource_(x)

class Picker(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_color = 'white'
        #self.countdown_time = arrow.now().shift(days=+3, hours=+1, minutes=+3)
        self.countdown_time = arrow.now().shift(minutes=+3, seconds=+10)
        self.make_view()
        self.update_interval = 1

    def make_view(self):
        
        self.delegate_and_datasource = UIPickerViewDataSourceAndDelegate.alloc().init().autorelease()
        
        x = 50
        dx = 100
        dy = 100
        for i in range(0,2): #4
          l = ui.Label(frame=(x,50,dx,dy))
          #l.text = ['day','hour','min','sec'][i]
          l.text = ['min','sec'][i]
          l.alignment = ui.ALIGN_CENTER
          self.add_subview(l)
          pv = UIPickerViewWrapper(frame=[x, 100, dx, dy])
          pv.name = l.text
          pv.delegate = self.delegate_and_datasource
          pv.data_source = self.delegate_and_datasource
          pv._picker_view.userInteractionEnabled = False
          
          pv.tag = i + 1
          self.add_subview(pv)
          x = x + dx

    def update(self):
        #self.update_interval = 30 if self.update_interval == 1 else 1
        td = self.countdown_time - arrow.now()
        self.name = str(td)
        self.disp_counters(td)
        
    def disp_counters(self,td):
        #days  = td.days
        secs  = td.seconds
        hours = int(secs/3600)
        secs  = secs - hours*3600
        mins  = int(secs/60)
        secs  = secs - mins*60
        #self['day']._picker_view.selectRow_inComponent_animated_(days, 0, True)
        #self['hour']._picker_view.selectRow_inComponent_animated_(hours, 0, True)
        self['min']._picker_view.selectRow_inComponent_animated_(mins, 0, True)
        self['sec']._picker_view.selectRow_inComponent_animated_(secs, 0, True)


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
f = (0, 0, 320, 480)
#v['pickerview'].scene = Picker(frame = f)
v.present('fullscreen')


#tt = MyTimerTest(frame=f)
#tt.present('sheet')
