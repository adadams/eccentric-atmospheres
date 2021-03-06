import numpy as N
import astropy.units as U

import datetime

import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.animation as anim
from mpl_toolkits.basemap import Basemap
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
plt.rcParams['animation.ffmpeg_path'] = '/usr/local/bin/ffmpeg'

###########################################################
# Produces an orbital top-down view and a projection of surface temperatures, animated.
# The planet parameters MUST be set or determined beforehand.
########################################################### 
def draw(planet, plot_objects, num_orbits):
    
    #The class that gets used in the animation routine to update the visualized data for each time step.
    #The orbit points, star position, globe projection outline and temperature bounds are static.
    #Only the projected temperature arrays and line connecting the star and the planet at its position need to be updated in time.
    class UpdateFrames(object):
        
        #Initializes the temperature map and line from the star to the initial planet position.
        def __init__(self):
            self.plot_objects = plot_objects
            
        #Replaces the temperature map object and star-planet line with the appropriate ones for the desired time step (indexed by i).
        def __call__(self, i):
            for obj in self.plot_objects:
                obj.update(i)
    
    fig, axarr = plt.subplots(1, len(plot_objects))

    for i, obj in enumerate(plot_objects):
        time_resolution = obj.time_resolution
        if len(plot_objects)>1: obj.draw_animate(axarr[i])
        else: obj.draw(axarr)
    
    #Makes everything fit on the plot.
    fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    #The object that tells the animation routine to update.
    update_frames = UpdateFrames()

    #The actual animation routine.
    animation = anim.FuncAnimation(fig, update_frames,
                                   frames=time_resolution*num_orbits, blit=False)

    #Codec to write the animation to file.
    FFwriter = anim.FFMpegWriter()

    #Save the animation.
    animation.save('{0}_{1}_animation.mp4'.format(datetime.date.today(), planet.name), writer=FFwriter)
