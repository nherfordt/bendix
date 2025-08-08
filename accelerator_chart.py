import matplotlib.pyplot as plt
import numpy as np
from get_data import conv_bin_dec

def make_accelerator_graph(vin,accelerators,event):
    time_values = []
    accelerator_values = accelerators

    for x in range(40):
        time_values.append(x * .5)

    for i in range(len(accelerator_values)):
        accelerator_values[i] = round(conv_bin_dec(accelerator_values[i]) * 3.2,2)

    xpoints = np.array(time_values)
    ypoints = np.array(accelerator_values)

    plt.figure().clear()
    plt.axis([0, 19.5, 0, 100])
    plt.rcParams["font.family"] = "Verdana"
    plt.title("Event " + str(event) + "  | Accelerator Pedal Position (%)")
    plt.ylabel("Accelerator Pedal Position (%)")
    plt.xlabel("Time")
    plt.xticks(np.arange(min(xpoints), max(xpoints)+1, 1.0))
    plt.yticks(np.arange(0, 100, 5.0))
    plt.grid()
    plt.plot(xpoints,ypoints, color='g')
    plt.savefig("reports/"+vin+"/charts/"+vin+"-accelerator_"+str(event)+".png", bbox_inches="tight")
