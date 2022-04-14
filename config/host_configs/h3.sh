#!/bin/bash
sysctl -w net.ipv4.tcp_congestion_control=reno
sleep 20
iperf3 -c 10.0.0.4 -p 7779 -t 20

