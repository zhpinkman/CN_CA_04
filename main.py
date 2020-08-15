from mininet.topo import Topo
import random
import threading
import time
import os
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch, OVSSwitch
from mininet.node import IVSSwitch
from mininet.link import TCLink, Intf
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from subprocess import call

from mininet_script import Topology

MIN_BW = 1
MAX_BW = 5
BW_INTERVAL = 10
SEND_TCP_INTERVAL = 0.1

running = True


def main():
    global running
    print("-------------------------HELLO-----------------------")
    topo = Topology()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink, switch=OVSSwitch)

    # controller
    c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633 )

    net.start()
    threading.Thread(target=change_bw_timer_task, args=(net,)).start()
    # threading.Thread(target=send_data_timer_task, args=(net,)).start()

    print ("*** Running CLI")
    CLI(net)  # Bring up the mininet CLI
    

    print("*** Stopping network")
    running = False
    net.stop()


def send_data_timer_task(net):  # runs every second
    global running
    while running:
        # for host in net.hosts:
            #target_host = random
            # net.iperf( self, hosts=[host, ], l4Type='TCP', udpBw='100K', fmt=None,seconds=5, port=5001)
        print("sent TCP messages: ")
        time.sleep(SEND_TCP_INTERVAL)


def change_bw_timer_task(net):  # runs every second
    global running
    while running:
        for link in net.links:
            bw = random.randint(MIN_BW, MAX_BW)
            link.intf1.params["bw"] = bw
        print("net.links[0].intf1: ", net.links[0].intf1.params["bw"])
        time.sleep(BW_INTERVAL)


if __name__ == '__main__':
    os.system("sudo mn -c")
    setLogLevel('info')
    main()
