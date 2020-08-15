from mininet.topo import Topo


class CN_final(Topo):
    def __init__(self):
        Topo.__init__(self)
        
        # hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')


        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')


        # links
        self.addLink(h1, s1)
        self.addLink(s2, s1)
        self.addLink(h2, s2)
        self.addLink(s2, s3)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(h3, s3)
        self.addLink(h4, s3)
        self.addLink(s3, s4)
        self.addLink(h5, s4)
        self.addLink(h6, s4)
        self.addLink(h7, s4)


topos = {'CN_final': (lambda : CN_final())}


