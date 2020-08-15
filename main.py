from mininet.topo import Topo
import random
import threading
import time
import os
from mininet.link import TCLink, Intf
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from subprocess import call

from mininet_script import Topology

MIN_BW = 1
MAX_BW = 5

running = True


def main():
    global running
    print("-------------------------HELLO-----------------------")
    topo = Topology()
    net = Mininet(topo=topo, link=TCLink)

    net.start()
    threading.Thread(target=change_bw_timer_task,
                     name='TIMER_TASK1', args=(net,)).start()
    
    print ("*** Running CLI")
    CLI(net)  # Bring up the mininet CLI
    

    print("*** Stopping network")
    running = False
    net.stop()


def change_bw_timer_task(net):  # runs every second
    global running
    while running:
        for link in net.links:
            bw = random.randint(MIN_BW, MAX_BW)
            link.intf1.params["bw"] = bw
        print("net.links[0].intf1: ", net.links[0].intf1.params["bw"])
        time.sleep(1)


if __name__ == '__main__':
    os.system("sudo mn -c")
    setLogLevel('info')
    main()
