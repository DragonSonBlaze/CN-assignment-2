from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import argparse
import subprocess
import time


class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    "A LinuxRouter connecting three IP subnets"

    def build(self, **_opts):
        # Add Switches
        s1, s2 = [self.addSwitch(s) for s in ('s1', 's2')]

        # Add Hosts
        h1 = self.addHost('h1', ip='192.168.1.100/24')
        h2 = self.addHost('h2', ip='192.168.1.101/24')
        h3 = self.addHost('h3', ip='192.168.1.102/24')
        h4 = self.addHost('h4', ip='192.168.1.103/24')

        # Add Links
        for h, s in [(h1, s1), (h2, s1), (h3, s2), (h4, s2)]:
            self.addLink(h, s)
        self.addLink(s1, s2)


def run_tcp_server(host, port):
    # Start iperf server on the specified host and port
    host.cmd(f'iperf -s -p {port} &')


def run_tcp_client(host, server_ip, port, duration=10, congestion_control='reno', link_loss=0):
    # Run iperf client on the specified host to connect to the server
    cmd = f'iperf -c {server_ip} -p {port} -t {duration} --congestion {congestion_control} --loss {link_loss} > /tmp/iperf_result.txt 2>&1'
    host.cmd(cmd)


def main():
    setLogLevel('info')

    parser = argparse.ArgumentParser(description="Mininet Topology and TCP client-server program")
    parser.add_argument('--config', choices=['b', 'c'], required=True, help='Configuration Type')
    parser.add_argument('--congestion', default='reno', help='Congestion Control Type')
    parser.add_argument('--loss', default=0, type=float, help='Link Loss')

    args = parser.parse_args()


    topo = NetworkTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    if args.config == 'b':
        # Run the iperf server on H4
        run_tcp_server(net.get('h4'), 5001)

        # Wait for a moment before starting the client
        time.sleep(2)

        # Run the iperf client on H1 with congestion control and link loss options
        run_tcp_client(net.get('h1'), '10.0.0.4', 5001, congestion_control=args.congestion, link_loss=args.loss)

    elif args.config == 'c':
        # Run the iperf server on H4
        run_tcp_server(net.get('h4'), 5001)

        # Wait for a moment before starting the clients on H1, H2, H3
        time.sleep(2)

        # Run the iperf clients on H1, H2, H3 with congestion control and link loss options
        for host in ['h1', 'h2', 'h3']:
            run_tcp_client(net.get(host), '10.0.0.4', 5001, congestion_control=args.congestion, link_loss=args.loss)


    CLI(net)
    net.stop()


if __name__ == '__main__':
    main()
