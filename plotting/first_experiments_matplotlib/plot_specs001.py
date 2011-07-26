print "start"
import matplotlib.pyplot as plt
import numpy as np

print "modules loaded"

class SimpleMZView:
    
    def __init__(self):

        x = np.arange(10, 310, 10)
        y = np.sin(x)+1.5
        
        self.spec= np.array((x,y), np.float32).T
        self.fig = plt.figure()
        self.ax  = self.fig.add_subplot(111)
        for mz, I in self.spec:
            self.ax.plot([mz,mz],[0, I], 'r') 
            self.ax.plot(mz, I, "w.")


        self.ax.axis([0, 350, 0, 4])

        self.connect()
        self.last = None
              

    def connect(self):
        self.cidmotion = self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        #self.cidpress = self.fig.canvas.mpl_connect("button_press_event", self.xx)
        #self.kidpress = self.fig.canvas.mpl_connect("key_press_event", self.xx)

    def xx(self, evt):
        pass
        
    def on_motion(self, evt):
        print "on_motion event"
        xr, yr = evt.xdata, evt.ydata
        if xr is None: 
            return
        p = np.array((xr,yr))
       
        diff = (self.spec-p)
        dist = diff[:,0]**2 + diff[:,1]**2
        m, I = self.spec[np.argmin(dist)]
        if self.last:
            m0, I0 = self.last
            if (m0, I0) !=  (m, I):
                self.ax.plot(m0, I0, "w.")
                self.ax.plot(m,I, "b.")
                self.fig.canvas.draw()
                print "draw called"
        self.last = m,I


mv=SimpleMZView()
plt.show()

            
        



