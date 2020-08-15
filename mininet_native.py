from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


def topology():
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSSwitch )


    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)


    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6653 ) # can be 6633

    # links
    net.addLink(h1, s1, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(s2, s1, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(h2, s2, cls=TCLink, bw=random.randint(0, 10))
    # net.addLink(s2, s3)
    net.addLink(s1, s3, cls=TCLink, bw=random.randint(0, 10))
    # net.addLink(s2, s4)
    net.addLink(h3, s3, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(h4, s3, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(s3, s4, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(h5, s4, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(h6, s4, cls=TCLink, bw=random.randint(0, 10))
    net.addLink(h7, s4, cls=TCLink, bw=random.randint(0, 10))

    net.build()

    c0.start()

    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])


    print ("*** Running CLI")
    CLI(net)

    print ("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()    