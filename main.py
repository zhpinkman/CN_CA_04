from mininet.topo import Topo
import random
import threading
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

def main():
    print("HELLO")
    topo = Topology()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print ("*** Running CLI")
    CLI(net)  # Bring up the mininet CLI
    print ("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()