# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import mac
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event, switches
from collections import defaultdict

# switches
switches = []
# mymac[srcmac]->(switch, port)
mymac = {}
# adjacency map [sw1][sw2]->port from sw1 to sw2
adjacency = defaultdict(lambda: defaultdict(lambda: None))

# BANDWIDTH
def reverse_bw(b):
	return 1/b
# DEFAULT BW = 1
bw = defaultdict(lambda: defaultdict(lambda: 1))
# Chicago
bw[1][3] = reverse_bw(50)
bw[3][1] = reverse_bw(50)
bw[2][4] = reverse_bw(50)
bw[4][2] = reverse_bw(50)
bw[1][4] = reverse_bw(100)
bw[4][1] = reverse_bw(100)
bw[2][3] = reverse_bw(100)
bw[2][2] = reverse_bw(100)
# NewYork
bw[5][7] = reverse_bw(50)
bw[7][5] = reverse_bw(50)
bw[6][8] = reverse_bw(50)
bw[8][6] = reverse_bw(50)
bw[6][7] = reverse_bw(100)
bw[7][6] = reverse_bw(100)
bw[5][8] = reverse_bw(100)
bw[8][5] = reverse_bw(100)
# Seattle
bw[9][11] = reverse_bw(50)
bw[11][9] = reverse_bw(50)
bw[10][12] = reverse_bw(50)
bw[12][10] = reverse_bw(50)
bw[10][11] = reverse_bw(100)
bw[11][10] = reverse_bw(100)
bw[9][12] = reverse_bw(100)
bw[12][9] = reverse_bw(100)

bw[3][13] = reverse_bw(15)
bw[13][3] = reverse_bw(15)

bw[3][14] = reverse_bw(10)
bw[14][3] = reverse_bw(10)

bw[4][14] = reverse_bw(5)
bw[14][4] = reverse_bw(5)

bw[7][13] = reverse_bw(15)
bw[13][7] = reverse_bw(15)

bw[7][14] = reverse_bw(20)
bw[14][7] = reverse_bw(20)

bw[7][15] = reverse_bw(5)
bw[15][7] = reverse_bw(5)

bw[8][15] = reverse_bw(10)
bw[15][8] = reverse_bw(10)

bw[8][16] = reverse_bw(15)
bw[16][8] = reverse_bw(15)

bw[11][14] = reverse_bw(10)
bw[14][11] = reverse_bw(10)

bw[12][15] = reverse_bw(15)
bw[15][12] = reverse_bw(15)

bw[12][16] = reverse_bw(10)
bw[16][12] = reverse_bw(10)

# FIND THE NODE WITH MIN DIST IN Q
def minimum_distance(distance, Q):
	min_dist = float('Inf')
	node = 0
	for v in Q:
		if distance[v] < min_dist:
			min_dist = distance[v]
			node = v
	return node

# GET THE PATH FROM SOURCE TO DESTINATION REGARDING FIRST AND FINAL PORT
def get_path(src, dst, first_port, final_port):
	# Dijkstra's algorithm
	print("get_path is called, src=", src, " dst=", dst,
		  " first_port=", first_port, " final_port=", final_port)
	# INIT DIST AND PREV
	distance = {}
	previous = {}
	for switch_id in switches:
		distance[switch_id] = float('Inf')
		previous[switch_id] = None
	# SRC DIST IS 0 TO IT'S SELF
	distance[src] = 0
	Q = set(switches)
	print("Q=", Q)
	while len(Q) > 0:
		# CHOOSE THE NODE WITH LEAST DIST
		u = minimum_distance(distance, Q)
		Q.remove(u)
		# UPDATE COSTS OF ADJACENT NODES TO NODE u
		# FOR EVERY OTHER NODE
		# CALCULATE NEW DIST AND SET IF LESS THAN BEFORE
		for p in switches:
			if adjacency[u][p] is not None:
				w = bw[u][p]
				if distance[u] + w < distance[p]:
					# KEEP UPDATING DISTANCE VECTOR ACCORDING TO UPDATED NODES
					distance[p] = distance[u] + w
					# KEEP UPDATING PREVIOUS VECTOR ACCORDING TO UPDATED NODES
					previous[p] = u
	# GENERATING THE VECTOR CONTAINING PATH FROM THE SOURCE TO DESTINATION RECURSIVELY
	r = []
	p = dst
	r.append(p)
	q = previous[p]
	# UP UNTIL REACHING THE SOURCE NODE
	while q is not None:
		if q == src:
			r.append(q)
			break
		p = q
		r.append(p)
		# GETTING THE NODE BEFORE NODE p
		q = previous[p]
	# REVERSE THE PATH TO BE FROM SRC TO DST
	r.reverse()
	# IF THE PATH WAS A LOOP IGNORE PATH
	if src == dst:
		path = [src]
	else:
		path = r
	# Now add the ports
	r = []
	in_port = first_port
	# SET IN AND OUT PORTS OF SWITCHES BASED ON ADJACENCY LIST OF PORTS
	for s1, s2 in zip(path[:-1], path[1:]):
		out_port = adjacency[s1][s2]
		r.append((s1, in_port, out_port))
		in_port = adjacency[s2][s1]
	# APPENDS THE DESTINATION SWITCH WITH ITS INPUT AND OUTPUT PORT 
	r.append((dst, in_port, final_port))
	return r


class ProjectController(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(ProjectController, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self.topology_api_app = self
		self.datapath_list = []
	# Handy function that lists all attributes in the given object

	def ls(self, obj):
		print("\n".join([x for x in dir(obj) if x[0] != "_"]))

	def add_flow(self, datapath, in_port, dst, actions):
		ofproto = datapath.ofproto
		# 		Features request message

		# The controller sends a feature request to the switch upon session establishment.

		# This message is handled by the Ryu framework, so the Ryu application do not need to process this typically.
		parser = datapath.ofproto_parser
		match = datapath.ofproto_parser.OFPMatch(in_port=in_port, eth_dst=dst)
		inst = [parser.OFPInstructionActions(
			ofproto.OFPIT_APPLY_ACTIONS, actions)]
		# Modify Flow entry message
		# The controller sends this message to modify the flow table.
		mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, match=match, cookie=0,
			command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=ofproto.OFP_DEFAULT_PRIORITY, instructions=inst)
		datapath.send_msg(mod)

	# CALLED UPON PATH IS DETERMINED AND WE WANT IT TO BE INSTALLED IN SWITCHES' FLOW TABLES
	def install_path(self, p, ev, src_mac, dst_mac):
		print("install_path is called")
		# print "p=", p, " src_mac=", src_mac, " dst_mac=", dst_mac
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		# 		Features request message

		# The controller sends a feature request to the switch upon session establishment.

		# This message is handled by the Ryu framework, so the Ryu application do not need to process this typically.
		parser = datapath.ofproto_parser
		# SWITCH IN_PORT OUT_PORT FROM DIJKSTRA
		for sw, in_port, out_port in p:
			print(src_mac,"->", dst_mac, "via ", sw, " in_port=", in_port, " out_port=", out_port)
			# FIND THE SWITCH MATCHING OUR SETTING FOR SWITCH ID AND MAC ADDRESSES
			match = parser.OFPMatch(
				in_port=in_port, eth_src=src_mac, eth_dst=dst_mac)
			# GENERATE THE ACTION TO BE DONE IN FOREMENTIONED CIRCUMSTANCES WHICH IS ADDING THE OUT PUT PORT
			actions = [parser.OFPActionOutput(out_port)]
			# FIND THE ACCORDING SWITCH 
			datapath = self.datapath_list[int(sw) - 1]
			# APPLY THE GENERATED ACTION
			inst = [parser.OFPInstructionActions(
				ofproto.OFPIT_APPLY_ACTIONS, actions)]
			# Modify Flow entry message
			# The controller sends this message to modify the flow table.
			mod = datapath.ofproto_parser.OFPFlowMod(
				datapath=datapath, match=match, idle_timeout=0, hard_timeout=0, priority=1, instructions=inst)
			# SEND THE OPENFLOW ITEM (BROADCASTING)
			datapath.send_msg(mod)

	# CALLED UPON SWITCH CONFIGURATION IN THE NETWORK
	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		print("switch_features_handler is called")
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		# 		Features request message

		# The controller sends a feature request to the switch upon session establishment.

		# This message is handled by the Ryu framework, so the Ryu application do not need to process this typically.
		parser = datapath.ofproto_parser

		# MATCH CERTAIN SETTINGS FOR THE SWITCH FLOW TABLE TO BE MODIFIED
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(
			ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
		# Modify Flow entry message
		# The controller sends this message to modify the flow table.
		mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, match=match, cookie=0,
			command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=0, instructions=inst)
		datapath.send_msg(mod)


	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		# print("------------packet_in event:", ev.msg.datapath.id, " in_port:", ev.msg.match['in_port'])
		# msg: An object which describes the corresponding OpenFlow message.
		msg = ev.msg
		# msg.datapath: A ryu.controller.controller.Datapath instance which describes an OpenFlow switch from which we received this OpenFlow message.
		datapath = msg.datapath
		# ofproto: A module which exports OpenFlow definitions, mainly constants appeared in the specification, for the negotiated OpenFlow version. For example, ryu.ofproto.ofproto_v1_0 for OpenFlow 1.0.
		ofproto = datapath.ofproto
		# ofproto_parser: A module which exports OpenFlow wire message encoder and decoder for the negotiated OpenFlow version. For example, ryu.ofproto.ofproto_v1_0_parser for OpenFlow 1.0.
		# 		Features request message

		# The controller sends a feature request to the switch upon session establishment.

		# This message is handled by the Ryu framework, so the Ryu application do not need to process this typically.
		parser = datapath.ofproto_parser
		# INPUT PORT WHICH THIS PACKET CAME FROM
		in_port = msg.match['in_port']
		# CREATE PACKET FROM MSG.DATA TO ACCESS ETH TYPE
		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)
		# print "eth.ethertype=", eth.ethertype
		# avoid broadcast from LLDP Link Layer Discovery Protocol 
		if eth.ethertype == 35020:
			return
		# PACKET SRC AND DST SWITCH MAC
		dst = eth.dst
		src = eth.src
		# print("src=", src, " dst=", dst, " type=", hex(eth.ethertype))
		# print("adjacency=", adjacency)

		# ID OF THIS SWITCH IN DATAPATH
		dpid = datapath.id
		self.mac_to_port.setdefault(dpid, {})
		if src not in mymac.keys():
			# IF WE DON'T KNOW SRC YET ADD IT
			# ADD MAC ADDRESS OF EACH PORT OF SWITCHES EIGHTER FOR HOSTS OR COMMUNICATION BETWEEN SWITCHES
			mymac[src] = (dpid, in_port)
			print("NEW MAC: (DATAPATH_ID, ONE OF THIS SWITCH PORTS ID) =" , src, mymac[src])
		# print("\n\nmymac=", mymac)
		if dst in mymac.keys():
			# IF WE KNOW IN WHICH SWITCH AND PORT DST IS LOCATED
			# ex. src = 5a:b2:d0:4f:af:45
			p = get_path(mymac[src][0], mymac[dst][0], mymac[src][1], mymac[dst][1])
			print("***Path:", mymac[src][0], ":", mymac[src][1], "To", mymac[dst][0], ":",  mymac[dst][1], "is ", end=" ")
			print(p)
			self.install_path(p, ev, src, dst)
			out_port = p[0][2]
		else:
			# IF WE DON'T KNOW WHERE DST IS THEN FLOOD
			# FLOODING
			out_port = ofproto.OFPP_FLOOD
		# ofproto_parser.OFPxxxx(datapath,...): A callable to prepare an OpenFlow message for the given switch. It can be sent with Datapath.send_msg later. xxxx is a name of the message. For example OFPFlowMod for flow-mod message. Arguemnts depend on the message.
		actions = [parser.OFPActionOutput(out_port)]
		# install a flow to avoid packet_in next time
		if out_port != ofproto.OFPP_FLOOD:
			# ofproto_parser.OFPxxxx(datapath,...): A callable to prepare an OpenFlow message for the given switch. It can be sent with Datapath.send_msg later. xxxx is a name of the message. For example OFPFlowMod for flow-mod message. Arguemnts depend on the message.
			match = parser.OFPMatch(in_port=in_port, eth_src=src, eth_dst=dst)
		data = None
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data
		# ofproto_parser.OFPxxxx(datapath,...): A callable to prepare an OpenFlow message for the given switch. It can be sent with Datapath.send_msg later. xxxx is a name of the message. For example OFPFlowMod for flow-mod message. Arguemnts depend on the message.
		out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
		# send_msg(self, msg): Queue an OpenFlow message to send to the corresponding switch. If msg.xid is None, set_xid is automatically called on the message before queueing.
		datapath.send_msg(out)

	events = [event.EventSwitchEnter,
				event.EventSwitchLeave, event.EventPortAdd,
				event.EventPortDelete, event.EventPortModify,
				event.EventLinkAdd, event.EventLinkDelete]

	@set_ev_cls(events)
	def get_topology_data(self, ev):
		global switches
		# GET SWITCHES IDS FROM TOPOLOGY
		switch_list = get_switch(self.topology_api_app, None)
		switches = [switch.dp.id for switch in switch_list]
		print("raw switches data: ", switches)
		self.datapath_list = [switch.dp for switch in switch_list]
		# print "self.datapath_list=", self.datapath_list
		print("switches=", switches)
		# GET LINKS FROM TOPOLOGY
		links_list = get_link(self.topology_api_app, None)
		mylinks = [(link.src.dpid, link.dst.dpid, link.src.port_no, link.dst.port_no) for link in links_list]
		# CREATE adjacency map [sw1][sw2]->port from sw1 to sw2
		# PORTS ARE THE OUTPUT PORTS FOR THE SWITCHES
		for s1, s2, port1, port2 in mylinks:
			adjacency[s1][s2] = port1
			adjacency[s2][s1] = port2
			print (s1,s2,port1,port2)
