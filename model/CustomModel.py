import os

import toml
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import CPULimitedHost

from monitoring.Monitor import Monitor
from topology.CustomTopology import CustomTopology

from net_stats_plotter.NetStatsPlotter import NetStatsPlotter


class CustomModel:

    def __init__(self):
        self.__topology_config = {}
        self.__devices_startup_configs = {}
        self.__links_config = []
        self.__monitoring_config = None

    def configure_model(self, config_file):
        try:
            file = toml.load(config_file)
            self.__monitoring_config = file["monitoring"]
            self.__topology_config = {"devices": file["devices"],
                                    "switches": file["switches"],
                                    "links": file["links"]}

            for i in file["devices"]:
                self.__devices_startup_configs[i] = file["devices"][i]["cmd"]

            self.__links_config = file["links"]["cmd"]

        except FileNotFoundError:
            print("Введите корректное имя файла")

    def simulation(self):
        topology = CustomTopology(self.__topology_config)
        net = Mininet(topo=topology, host=CPULimitedHost, link=TCLink)
        net.start()
        print("Сеть запущена")
        try:
            self.__configure_links()
            self.__configure_devices(net.hosts)

            h1, h2 = net.get(
                self.__monitoring_config["host_client"],
                self.__monitoring_config["host_server"]
            )
            monitor = Monitor(h1, h2, self.__monitoring_config["interface"],
                              self.__monitoring_config["plots_dir"])
            qlen_mon_time = self.__monitoring_config["monitoring_time"]
            iperf_file = self.__monitoring_config["iperf_file_name"]
            iperf_commands = self.__monitoring_config["iperf_flags"] + " -t %d" % \
                             qlen_mon_time
            qlen_file = self.__monitoring_config["queue_data_file_name"]
            qlen_mon_interval = self.__monitoring_config["monitoring_interval"]
            monitor.net_monitoring(iperf_file, iperf_commands, qlen_file, qlen_mon_time, qlen_mon_interval)
        finally:
            net.stop()
            print("Сеть прекратила работу.")
            print("Строим графики.")

            plotter = NetStatsPlotter(self.__monitoring_config["plots_dir"], self.__monitoring_config["plots_format"])
            plotter.plot_net_stats(os.path.join(self.__monitoring_config["plots_dir"],
                                                self.__monitoring_config["iperf_file_name"]))
            plotter.plot_queue_len(os.path.join(self.__monitoring_config["plots_dir"],
                                                self.__monitoring_config["queue_data_file_name"]))
            print("Графики построены и находятся в директории {}.".format(self.__monitoring_config["plots_dir"]))

    def __configure_links(self):
        for i in self.__links_config:
            os.system(i)

    def __configure_devices(self, devices):
        for i in devices:
            command = self.__devices_startup_configs["{}".format(i)]
            i.cmd(command)
