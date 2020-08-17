from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():

    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/8', autoStaticArp=False)

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           port=6633)

    info('*** Add switches\n')
    sw1 = net.addSwitch('sw1', cls=OVSKernelSwitch)
    sw2 = net.addSwitch('sw2', cls=OVSKernelSwitch)
    sw3 = net.addSwitch('sw3', cls=OVSKernelSwitch)
    sw4 = net.addSwitch('sw4', cls=OVSKernelSwitch)
    sw5 = net.addSwitch('sw5', cls=OVSKernelSwitch)
    sw6 = net.addSwitch('sw6', cls=OVSKernelSwitch)
    sw7 = net.addSwitch('sw7', cls=OVSKernelSwitch)

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.1.0.1',
                     mac='00:00:00:00:00:01', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.1.0.2',
                     mac='00:00:00:00:00:02', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.1.0.3',
                     mac='00:00:00:00:00:03', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.1.0.4',
                     mac='00:00:00:00:00:04', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.1.0.5',
                     mac='00:00:00:00:00:05', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.1.0.6',
                     mac='00:00:00:00:00:06', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.1.0.7',
                     mac='00:00:00:00:00:07', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.1.0.8',
                     mac='00:00:00:00:00:08', defaultRoute=None)

    info('*** Add links\n')
    net.addLink(h1, sw3)
    net.addLink(h2, sw3)
    net.addLink(h3, sw4)
    net.addLink(h4, sw4)
    net.addLink(h5, sw6)
    net.addLink(h6, sw6)
    net.addLink(h7, sw7)
    net.addLink(h8, sw7)

    net.addLink(sw3, sw2)
    net.addLink(sw4, sw2)
    net.addLink(sw6, sw5)
    net.addLink(sw7, sw5)

    net.addLink(sw2, sw1)
    net.addLink(sw5, sw1)
    
    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('sw1').start([c0])
    net.get('sw2').start([c0])
    net.get('sw3').start([c0])
    net.get('sw4').start([c0])
    net.get('sw5').start([c0])
    net.get('sw6').start([c0])
    net.get('sw7').start([c0])

    info('*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
