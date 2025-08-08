# speed_chart.py
import os
import matplotlib
matplotlib.use("Agg")  # headless backend for servers
import matplotlib.pyplot as plt
import numpy as np
from get_data import conv_bin_dec


def make_speed_graph(vin, speeds, event):
    # Ensure output dir exists
    charts_dir = os.path.join("reports", vin, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # Build time axis (0..19.5 in 0.5 steps, 40 points)
    time_values = [x * 0.5 for x in range(40)]

    # Convert binary strings -> mph
    speed_values = [round(conv_bin_dec(v) * 2.23714, 2) for v in speeds]

    xpoints = np.array(time_values[:len(speed_values)])
    ypoints = np.array(speed_values[:len(time_values)])

    # Plot
    fig = plt.figure()
    try:
        plt.rcParams["font.family"] = "Verdana"
        plt.axis([0, 19.5, 0, 100])
        plt.title(f"Event {event}  | Vehicle Speed")
        plt.ylabel("Vehicle Speed (mph)")
        plt.xlabel("Time")
        plt.xticks(np.arange(0, 20, 1.0))
        plt.yticks(np.arange(0, 100, 5.0))
        plt.grid()
        plt.plot(xpoints, ypoints, color="r")

        out_path = os.path.join(charts_dir, f"{vin}-speed_{event}.png")
        plt.savefig(out_path, bbox_inches="tight")
        return out_path
    finally:
        plt.close(fig)
