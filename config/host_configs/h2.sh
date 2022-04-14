#!/bin/bash
sysctl -w net.ipv4.tcp_congestion_control=reno
sleep 10
iperf3 -c 10.0.0.4 -p 7778 -t 20

