print "start"
import matplotlib.pyplot as plt
import numpy as np

print "modules loaded"

class View:
    
    def __init__(self):

        self.x = np.arange(10, 310, 10)
        self.y = np.sin(self.x)+1.5
        
        self.fig = plt.figure()
        self.ax  = self.fig.add_subplot(111)

        self.ax.plot(self.x, self.y)
        self.connect()

        self.started = None
        self.ended   = None
        self.pressed = False
        self.lastp   = None
              

    def connect(self):
        self.cidmotion = self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.cidpress = self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect("button_release_event", self.on_release)
        self.cididle = self.fig.canvas.mpl_connect("idle_event", self.on_idle)
        #self.kidpress = self.fig.canvas.mpl_connect("key_press_event", self.xx)

    def next_to(self, x):
        imin = np.argmin(np.abs(x-self.x))
        return self.x[imin], self.y[imin]

    def on_idle(self, evt):
        print "idle"

    def on_press(self, evt):
        self.pressed = True
        self.started = evt.xdata, evt.ydata
        #x, y = self.next_to(evt.xdata)
        #self.ax.plot(x, y, "ro")
        #self.fig.canvas.draw()
        
    def on_motion(self, evt):
        if not self.pressed: return
        #x, y = self.next_to(evt.xdata)
        #if (x,y) != self.lastp:
            #print "on_motion"
            #self.ax.plot(x,y, "bo")
        x, y = evt.xdata, evt.ydata
        self.ax.
        self.fig.canvas.draw()
        self.lastp = x,y

    def on_release(self, evt):
        self.pressed = False
        
        


mv=View()
plt.show()

            
        



