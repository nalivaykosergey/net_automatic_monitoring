from time import sleep
from subprocess import *
from threading import Thread
import re
import os

from plotting.NetStatsPlotter import NetStatsPlotter

class Monitor:

    def __init__(self, host, server, iface, save_dir="monitoring_plots"):

        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            os.system("chmod 777 {}".format(save_dir))
        self.host = host
        self.server = server
        self.iface = iface

    def net_monitoring(self, iperf_file, iperf_commands,
                       qlen_file, qlen_mon_time, qlen_mon_interval):
        th1 = Thread(target=self.__iperf_monitoring,
                     args=(iperf_file, iperf_commands,))
        th2 = Thread(target=self.__queue_len_monitoring,
                     args=(qlen_mon_time, qlen_mon_interval, qlen_file))
        th1.start()
        th2.start()
        th1.join()
        th2.join()
        print("Мониторинг окончен. Строим графики.")
        plotter = NetStatsPlotter(self.save_dir, "png")
        plotter.plot_net_stats(os.path.join(self.save_dir, iperf_file))
        plotter.plot_queue_len(os.path.join(self.save_dir, qlen_file))
        print("Графики построены и находятся в директории {}.".format(self.save_dir))

    def __queue_len_monitoring(self, time=1, interval_sec_=0.1, fname="qlen.dat"):
        print("Начало мониторинга сети на интерфейсе {}. Продолжительность мониторинга: "
              "{} сек. с интервалом {}".format(self.iface, time, interval_sec_))
        current_time = 0
        # Регуляроное выражение для поиска данных с tc
        pat_queued = re.compile(r'backlog\s[^\s]+\s([\d]+)p')
        cmd = "tc -s qdisc show dev {}".format(self.iface)
        # Открытие файла мониторинга на запись
        file = open("{}/{}".format(self.save_dir, fname), 'w')
        # Цикл, в котором происходит мониторинг до прерывания
        while current_time < time:
            # Вызов команды в tc в терминале и поиск значения длины очереди, количества отброшенных пакетов
            p = Popen(cmd, shell=True, stdout=PIPE)
            output = p.stdout.read().decode('utf-8')
            matches_queue = pat_queued.findall(output)
            if matches_queue:
                t = "%f" % current_time
                current_time += interval_sec_
                file.write(t + ' ' + matches_queue[-1] + " " + '\n')
            sleep(interval_sec_)
            current_time += interval_sec_
        os.system("chmod 777 {}/{}".format(self.save_dir, fname))
        file.close()

    def __iperf_monitoring(self, file_name, params):
        print("Начало работы iperf. Хост: {}, сервер: {}. "
              "Файл с данными: {}/{}"
              .format(self.host.name, self.server.name, self.save_dir, file_name))

        self.server.popen("iperf3 -s -p 7777 -1")
        self.host.cmd("iperf3 -c {} -p 7777 {} -J > {}/{}"
                      .format(self.server.IP(), params, self.save_dir, file_name))
        os.system("chmod 777 {}/{}".format(self.save_dir, file_name))
