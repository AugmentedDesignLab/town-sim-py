import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os

from landscape import Landscape

def generateRoadAngleGraph(folderpath):
    for _, _, filenames in os.walk(folderpath):
        filenames = [f for f in filenames if f.endswith(".p")]

        list_of_degrees = []
        
        for f in filenames:
            f = f[:f.index(".p")]
            print ("Filename = {}.".format(f))

            filename_state = "{}/{}.p".format(folderpath, f)
            filename_roads = "{}/{}.output.txt".format(folderpath, f)
            filename_stats = "{}/stats_{}.output.txt".format(folderpath, f)

            landscape = Landscape(100, 100, None, 0, 0, 0, 0, load_filename=filename_state) #hard-code size=100
            for rs in landscape.roadsegments:
                (x, y) = (rs.rnode1.x - rs.rnode2.x, rs.rnode1.y - rs.rnode2.y)
                r = math.hypot(x, y)
                theta = np.arctan2(y, x)
                theta = math.radians(math.degrees(theta) % 360)
                list_of_degrees.append((r, theta))

        list_of_degrees = sorted(list_of_degrees, key=lambda x: x[1])
        directions = set([theta for (r, theta) in list_of_degrees])
        summed_list_of_degrees = []
        for direction in directions:
            magnitude = math.log(sum([r for (r, theta) in list_of_degrees if theta == direction]))
            summed_list_of_degrees.append((magnitude, direction))
        
        width, height = matplotlib.rcParams['figure.figsize']
        size = min(width, height)
        # make a square figure
        fig = plt.figure(figsize=(size, size))
        ax = fig.add_axes([0, 0, 1, 1], polar=True)
        
        for r, theta in summed_list_of_degrees:
            ax.plot([theta, theta], [0, r], color='#000000')
        ax.grid(False)
        plt.title("Sum of {} towns in log scale.".format(len(filenames)))
        plt.show()

def generateConnectivityGraph(folderpath):
    for _, _, filenames in os.walk(folderpath):
        filenames = [f for f in filenames if f.endswith(".p")]
        
        connectivity = []
        local_depth = []
        global_depth = []

        for f in filenames:
            f = f[:f.index(".p")]
#             print ("Filename = {}.".format(f))

            filename_state = "{}/{}.p".format(folderpath, f)
            filename_roads = "{}/{}.output.txt".format(folderpath, f)
            filename_stats = "{}/stats_{}.output.txt".format(folderpath, f)
            
            # skip first two numbers x and y, match next 3 numbers
            p = re.compile("\D+\d+\D+\d+\D+(\d+)\D+(\d+)\D+(\d+)\D+") 
            
            with open(filename_stats, "rb") as file:
                line = file.readline()
                c = []
                l = []
                g = []
                while line:
                    m = p.match(str(line))
                    c.append(float(m.groups()[0]))
                    l.append(float(m.groups()[1]))
                    g.append(float(m.groups()[2]))
#                     connectivity.append(float(m.groups()[0]))
#                     local_depth.append(float(m.groups()[1]))
#                     global_depth.append(float(m.groups()[2]))
                    line = file.readline()
                connectivity.append(sum(c)/len(c))
                local_depth.append(sum(l)/len(l))
                global_depth.append(sum(g)/len(g))

        fig1, ax1 = plt.subplots()
        ax1.set_title("Connectedness of {} towns.".format(len(filenames)))
        ax1.boxplot([connectivity])
        ax2 = ax1.twinx()
        ax2.boxplot([[], local_depth, global_depth])
        plt.xlim(0.5, 3.5)
        plt.axvspan(0.5, 1.5, facecolor='b', alpha=0.1)
        plt.axvspan(1.5, 3.5, facecolor='g', alpha=0.1)
        ax1.tick_params(axis='y', colors='blue')
        ax2.tick_params(axis='y', colors='green')
        plt.xticks([1, 2, 3], ['connectivity', 'local depth', 'global depth'])

        plt.show()

def generateCurvatureGraph(folderpath):
	pass

generateRoadAngleGraph("../statsoutputs")
generateConnectivityGraph("../statsoutputs")
generateCurvatureGraph("../statsoutputs")

# need to generate screenshots for a fourth analysis

# parameter variation screenshots

# 8-10 image sequence showing growth 
# river crossing
# radial bypass screenshots sequence ... point to it 
# garden conversion (even though it doesn't do anything)