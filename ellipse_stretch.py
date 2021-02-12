from scene import *
import ui

class MyScene (Scene):

    width = 900
    height = 500
    activeNode = None
    handles = ()
    menu_collapse = True

    def setup(self):
        ground = Node(parent=self)
        ground.position = (self.size.w/2, self.size.h/2)

        self.ellipse = ShapeNode(ui.Path.oval(0,0, self.width, self.height), fill_color='clear', stroke_color='#b50000')
        self.handleWidth = ShapeNode(ui.Path.oval(0,0, 10, 10), fill_color='#b50000', stroke_color='clear')
        self.handleHeight = ShapeNode(ui.Path.oval(0,0, 10, 10), fill_color='#b50000', stroke_color='clear')

        menuShape = ui.Path.rect(0,0,32,2)
        menuShape.append_path(ui.Path.rect(0,-8,32,2))
        menuShape.append_path(ui.Path.rect(0,-16,32,2))
        self.menu = ShapeNode(menuShape, fill_color='white', stroke_color='clear')
        self.menu.position = (24,self.size.y-20)

        ground.add_child(self.ellipse)
        ground.add_child(self.handleWidth)
        ground.add_child(self.handleHeight)
        self.add_child(self.menu)
        self.add_child(ground)

        self.handles = (self.handleWidth, self.handleHeight, self.menu)

        self.ui01 = self.view.superview.subviews[1]
        self.ui01.x = -400

        self.sliderW = self.ui01['slider-01']
        self.sliderW.action = self.sliderW_changed
        self.sliderH = self.ui01['slider-02']
        self.sliderH.action = self.sliderH_changed

        self.updateStuff()


    def updateStuff(self):
        self.ellipse.path = ui.Path.oval(0,0, self.width, self.height)
        self.handleWidth.position = (self.width/2,0)
        self.handleHeight.position = (0, self.height/2)
        self.sliderW.value = round(self.width/1000,2)
        self.sliderH.value = round(self.height/1000,2)
        self.ui01['label-01'].text = str(self.width)
        self.ui01['label-02'].text = str(self.height)


    def checkTouchAndSetActiveHandle(self, touch):
        l = touch.location
        detectSize  = 20

        for node in self.handles:
            p = node.point_to_scene((0,0)) #.position
            if (p.x-detectSize < l.x < p.x+detectSize) and (p.y-detectSize < l.y < p.y+detectSize):
                self.activeNode = node


    def touch_began(self, touch):
        self.checkTouchAndSetActiveHandle(touch)
        if self.activeNode == self.menu:
            if self.menu_collapse == True:
                self.menu.position = (424, self.size.y-20)
                self.ui01.x = 0
                self.menu_collapse = False

            else:
                self.menu.position = (24, self.size.y-20)
                self.ui01.x = -400
                self.menu_collapse = True

        elif self.activeNode == self.handleWidth:
            self.handleWidth.path = ui.Path.oval(0,0, 50, 50)

        elif self.activeNode == self.handleHeight:
            self.handleHeight.path = ui.Path.oval(0,0, 50, 50)


    def touch_moved(self, touch):
        x = touch.location.x
        y = touch.location.y

        if self.activeNode == self.handleWidth:
            self.width = max(0,self.handleWidth.parent.point_from_scene((x,y)).x)*2
            self.updateStuff()

        elif self.activeNode == self.handleHeight:
            self.height = max(0,self.handleHeight.parent.point_from_scene((x,y)).y)*2
            self.updateStuff()


    def touch_ended(self, touch):
        self.activeNode = None
        self.handleWidth.path = ui.Path.oval(0,0, 10, 10)
        self.handleHeight.path = ui.Path.oval(0,0, 10, 10)


    def sliderW_changed(self, sender):
        value = round(sender.superview['slider-01'].value*1000,2)
        sender.superview['label-01'].text = str(value)
        self.width = value
        self.updateStuff()


    def sliderH_changed(self, sender):
        value = round(sender.superview['slider-02'].value*1000,2)
        sender.superview['label-02'].text = str(value)
        self.height = value
        self.updateStuff()


v = ui.load_view('ellipse_stretch.pyui')
v['sceneview'].scene = MyScene()
v.present('fullscreen')
