from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    # pylint: disable=arguments-differ
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    # pylint: disable=arguments-differ
    def build( self, **_opts ):

        #Add routers
        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP )
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip='172.16.0.1/12')
        r3 = self.addNode( 'r3', cls=LinuxRouter, ip='10.0.0.1/8')

        #Add switches
        s1, s2, s3 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3' ) ]

        #Add links between the routers and switches
        self.addLink( s1, r1, intfName2='r1-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, r2, intfName2='r2-eth1',
                      params2={ 'ip' : '172.16.0.1/12' } )
        self.addLink( s3, r3, intfName2='r3-eth1',
                      params2={ 'ip' : '10.0.0.1/8' } )

        #Add links between the routers
        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2', params1={'ip': '192.168.4.1/30'}, params2={'ip': '192.168.4.2/30'})
        self.addLink(r2, r3, intfName1='r2-eth3', intfName2='r3-eth2', params1={'ip': '192.168.5.1/30'}, params2={'ip': '192.168.5.2/30'})
        self.addLink(r3, r1, intfName1='r3-eth3', intfName2='r1-eth3', params1={'ip': '192.168.6.1/30'}, params2={'ip': '192.168.6.2/30'})

        #create hosts
        h1 = self.addHost('h1', ip = '192.168.1.100/24', defaultRoute = 'via 192.168.1.1')
        h2 = self.addHost('h2', ip = '192.168.1.101/24', defaultRoute = 'via 192.168.1.1')
        h3 = self.addHost('h3', ip = '172.16.0.100/12', defaultRoute = 'via 172.16.0.1')
        h4 = self.addHost('h4', ip = '172.16.0.101/12', defaultRoute = 'via 172.16.0.1')
        h5 = self.addHost('h5', ip = '10.0.0.100/8', defaultRoute = 'via 10.0.0.1')
        h6 = self.addHost('h6', ip = '10.0.0.101/8', defaultRoute = 'via 10.0.0.1')

        #connect host to switches
        for h, s in [ (h1, s1), (h2, s1), (h3, s2), (h4, s2), (h5, s3), (h6, s3) ]:
            self.addLink( h, s )
        


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()

    # Enable packet capture on r1 for interfaces connected to other routers
    r1 = net.getNodeByName('r1')
    r1.cmd('tcpdump -n -i r1-eth2 -w /tmp/r1-eth2.pcap &')
    r1.cmd('tcpdump -n -i r1-eth3 -w /tmp/r1-eth3.pcap &')

    # Assigning static routes for the routers
    net['r1'].cmd('ip route add 172.16.0.0/12 via 192.168.4.2')
    net['r1'].cmd('ip route add 10.0.0.0/8 via 192.168.6.1')
    net['r2'].cmd('ip route add 192.168.1.0/24 via 192.168.4.1')
    net['r2'].cmd('ip route add 10.0.0.0/8 via 192.168.5.2')
    net['r3'].cmd('ip route add 192.168.1.0/24 via 192.168.6.2')
    net['r3'].cmd('ip route add 172.16.0.0/12 via 192.168.5.1')

    #info('*** Debug Information:\n')
    #info(net['h1'].cmd('ifconfig'))
    #info(net['h2'].cmd('ifconfig'))
    #info(net['r1'].cmd('ifconfig'))
    #info(net['r2'].cmd('ifconfig'))
    #info(net['r3'].cmd('ifconfig'))

    info('* Routing Table for Router r1:\n')
    info(net['r1'].cmd('route'))
    info('* Routing Table for Router r2:\n')
    info(net['r2'].cmd('route'))
    info('* Routing Table for Router r3:\n')
    info(net['r3'].cmd('route'))

    # Vary the default route for h1 to h6 traffic via different routers
    net['r1'].cmd('ip route del 10.0.0.0/8 via 192.168.6.1')
    net['r1'].cmd('ip route add 10.0.0.0/8 via 192.168.4.2')
    net['r3'].cmd('ip route del 192.168.1.0/24 via 192.168.6.2')
    net['r3'].cmd('ip route add 192.168.1.0/24 via 192.168.5.1')

    # Display updated routing tables
    info('* Updated Routing Table for Router r1:\n')
    info(net['r1'].cmd('route'))
    info('* Updated Routing Table for Router r2:\n')
    info(net['r2'].cmd('route'))
    info('* Updated Routing Table for Router r3:\n')
    info(net['r3'].cmd('route'))

    CLI(net)

    # Stop packet capture before exiting
    r1.cmd('kill %tcpdump')

    net.stop()
    
if __name__ == '__main__':
    setLogLevel( 'info' )
    run()