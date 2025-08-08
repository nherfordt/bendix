import matplotlib.pyplot as plt
import numpy as np

def make_combo_graph(vin,speeds,accelerators,event):
    time_values = []
    speed_values = speeds
    accelerator_values = accelerators

    for x in range(40):
        time_values.append(x * .5)

    xpoints = np.array(time_values)
    ypoints = np.array(speed_values)
    zpoints = np.array(accelerator_values)

    plt.figure().clear()
    plt.axis([0, 19.5, 0, 100])
    plt.rcParams["font.family"] = "Verdana"
    plt.title("Event " + str(event) + " | Speed and Accelerator Pedal Position")
    plt.xlabel("Angle")
    plt.xlabel("Time")
    plt.xticks(np.arange(min(xpoints), max(xpoints)+1, 1.0))
    plt.yticks(np.arange(0, 100, 5.0))
    plt.grid()
    plt.plot(xpoints, ypoints, color='r', label='Speed (mph)')
    plt.plot(xpoints, zpoints, color='g', label='Accelerator (%)')
    plt.legend()
    plt.savefig("reports/"+vin+"/charts/"+vin+"-combo_"+str(event)+".png", bbox_inches="tight")
