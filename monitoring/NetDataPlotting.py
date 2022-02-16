import matplotlib.pyplot as plt
import numpy as np


def plot_net_stats(stats, plot_format, folder):
    x_stats, y_stats = stats
    for i in y_stats:
        plt.plot(x_stats, y_stats[i][0], 'k', linewidth=1)
        plt.grid()
        plt.xlim(xmin=0, xmax=x_stats[-1])
        plt.xlabel(y_stats[i][1]["x"])
        plt.ylabel(y_stats[i][1]["y"])
        plt.title(y_stats[i][1]["title"])
        plt.savefig("{}/{}.{}".format(folder, i, plot_format))
        plt.clf()


def plot_queue_len(stats, plot_format, folder):
    x_stats, y_stats = stats
    plt.plot(x_stats, y_stats, 'k', linewidth=1)
    plt.grid()
    plt.xlim(xmin=0, xmax=x_stats[-1])
    plt.xlabel("Время (с)")
    plt.ylabel("Размер очереди (пакеты)")
    plt.title("Размер очереди в течении времени")
    plt.savefig("{}/queue_len.{}".format(folder, plot_format))