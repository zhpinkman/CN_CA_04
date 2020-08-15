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


class CN_final(Topo):
    def __init__(self):
        Topo.__init__(self)
        
        # hosts
        h1 = self.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        h2 = self.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
        h3 = self.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
        h4 = self.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
        h5 = self.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
        h6 = self.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
        h7 = self.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)

        

        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')


        # links
        self.addLink(h1, s1, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(s2, s1, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(h2, s2, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        # self.addLink(s2, s3)
        self.addLink(s1, s3, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        # self.addLink(s2, s4)
        self.addLink(h3, s3, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(h4, s3, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(s3, s4, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(h5, s4, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(h6, s4, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)
        self.addLink(h7, s4, cls=TCLink, bw=random.randint(0, 10), delay='1ms',loss=0)


# def printit():
#   threading.Timer(5.0, printit).start()
#   print "Hello, World!"

# printit()

#  intf = h2.intf()
#     info( "Setting BW Limit for Interface " + str(intf) + " to " + str(target_bw) + "\n" )
#     intf.config(bw = target_bw, smooth_change = smooth_change)

topos = {'CN_final': (lambda : CN_final())}


