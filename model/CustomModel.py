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
        self.topology_config = {}
        self.devices_startup_configs = {}
        self.links_config = []
        self.monitoring_config = None

    def configure_model(self, config_file):
        try:
            file = toml.load(config_file)
            self.monitoring_config = file["monitoring"]
            self.topology_config = {"devices": file["devices"],
                                    "switches": file["switches"],
                                    "links": file["links"]}

            for i in file["devices"]:
                self.devices_startup_configs[i] = file["devices"][i]["cmd"]

            self.links_config = file["links"]["cmd"]

        except FileNotFoundError:
            print("Введите корректное имя файла")

    def simulation(self):
        topology = CustomTopology(self.topology_config)
        net = Mininet(topo=topology, host=CPULimitedHost, link=TCLink)
        net.start()
        print("Сеть запущена")
        try:
            self.__configure_links()
            self.__configure_devices(net.hosts)

            h1, h2 = net.get(
                self.monitoring_config["host_client"],
                self.monitoring_config["host_server"]
            )
            monitor = Monitor(h1, h2, self.monitoring_config["interface"],
                              self.monitoring_config["plots_dir"])
            qlen_mon_time = self.monitoring_config["monitoring_time"]
            iperf_file = self.monitoring_config["iperf_file_name"]
            iperf_commands = self.monitoring_config["iperf_flags"] + " -t %d" % \
                             qlen_mon_time
            qlen_file = self.monitoring_config["queue_data_file_name"]
            qlen_mon_interval = self.monitoring_config["monitoring_interval"]
            monitor.net_monitoring(iperf_file, iperf_commands, qlen_file, qlen_mon_time, qlen_mon_interval)
        finally:
            net.stop()
            print("Сеть прекратила работу.")
            print("Строим графики.")

            plotter = NetStatsPlotter(self.monitoring_config["plots_dir"], self.monitoring_config["plots_format"])
            plotter.plot_net_stats(os.path.join(self.monitoring_config["plots_dir"],
                                                self.monitoring_config["iperf_file_name"]))
            plotter.plot_queue_len(os.path.join(self.monitoring_config["plots_dir"],
                                                self.monitoring_config["queue_data_file_name"]))
            print("Графики построены и находятся в директории {}.".format(self.monitoring_config["plots_dir"]))

    def __configure_links(self):
        for i in self.links_config:
            os.system(i)

    def __configure_devices(self, devices):
        for i in devices:
            command = self.devices_startup_configs["{}".format(i)]
            i.cmd(command)
