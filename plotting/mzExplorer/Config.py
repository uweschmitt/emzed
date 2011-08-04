from guiqwt.config import CONF

__author__ = 'Administrator'

def setupCommonStyle(line, marker):

   markerSymbol = "Ellipse" # in this case a circle, because we give only one size parameter.
   edgeColor = "#555555"
   faceColor = "#cc0000"
   alpha = 0.8
   size = 6
   params = {
       "marker/cross/symbol/marker": markerSymbol,
       "marker/cross/symbol/edgecolor": edgeColor,
       "marker/cross/symbol/facecolor": faceColor,
       "marker/cross/symbol/alpha": alpha,
       "marker/cross/symbol/size": size,
       "marker/cross/pen/width": 0,
       "marker/cross/linestyle": 0,
       }
   CONF.update_defaults(dict(plot=params))
   marker.markerparam.read_config(CONF, "plot", "marker/cross")
   marker.markerparam.update_marker(marker)
   params = {
       "shape/drag/symbol/marker": markerSymbol,
       "shape/drag/symbol/size": size,
       "shape/drag/symbol/edgecolor": edgeColor,
       "shape/drag/symbol/facecolor": faceColor,
       "shape/drag/symbol/alpha": alpha,

       }
   CONF.update_defaults(dict(plot=params))
   line.shapeparam.read_config(CONF, "plot", "shape/drag")
   line.shapeparam.update_shape(line)