from time import sleep
from subprocess import *
from threading import Thread
import re
import os


class Monitor:

    def __init__(self, host, server, iface, save_dir="monitoring_plots"):

        self.__save_dir = save_dir
        if not os.path.exists(self.__save_dir):
            os.makedirs(self.__save_dir)
            os.system("chmod 777 {}".format(save_dir))
        self.__host = host
        self.__server = server
        self.__iface = iface

    def set_host(self, host):
        self.__host = host

    def set_server(self, server):
        self.__server = server

    def set_iface(self, iface):
        self.__iface = iface

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
        print("Мониторинг окончен.")


    def __queue_len_monitoring(self, time=1.0, interval_sec_=0.1, fname="qlen.dat"):
        print("Начало мониторинга сети на интерфейсе {}. Продолжительность мониторинга: "
              "{} сек. с интервалом {}".format(self.__iface, time, interval_sec_))
        current_time = 0
        # Регуляроное выражение для поиска данных с tc
        pat_queued = re.compile(r'backlog\s[^\s]+\s([\d]+)p')
        cmd = "tc -s qdisc show dev {}".format(self.__iface)
        # Открытие файла мониторинга на запись
        file = open("{}/{}".format(self.__save_dir, fname), 'w')
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
        os.system("chmod 777 {}/{}".format(self.__save_dir, fname))
        file.close()

    def __iperf_monitoring(self, file_name, params):
        print("Начало работы iperf. Хост: {}, сервер: {}. "
              "Файл с данными: {}/{}"
              .format(self.__host.name, self.__server.name, self.__save_dir, file_name))

        self.__server.cmd("iperf3 -s -D")
        self.__host.cmd("iperf3 -c {} {} -J > {}/{}"
                        .format(self.__server.IP(), params, self.__save_dir, file_name))
        os.system("chmod 777 {}/{}".format(self.__save_dir, file_name))
