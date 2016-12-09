#!/usr/bin/python
# Copyright 2012 William Yu
# wyu@ateneo.edu
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX. If not, see <http://www.gnu.org/licenses/>.
#

"""
This is a demonstration file created to show how to obtain flow 
and port statistics from OpenFlow 1.0-enabled switches. The flow
statistics handler contains a summary of web-only traffic.
"""

# standard includes
from pox.core import core
from pox.lib.util import dpidToStr

# main functiont to launch the module
from pox.lib.recoco import Timer

import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()

#list to maintain the srcip and packet-count record
srcip_count={}

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
#  log.debug("FlowStatsReceived from %s: %s", 
 #   dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
  web_packet = 0
  for f in event.stats:

    if f.match.tp_dst==80:
      log.debug("srcip=%s",f.match.nw_src)

      web_packet += f.packet_count
      send_packet(event,f.match.nw_src,web_packet)
#      srcip_count[f.match.nw_src]=web_packet
      
#  log.debug("list_of_ip_counts=%s",srcip_count)
#  for i in srcip_count:
#    if srcip_count[i]>15:
#      log.debug("packet-rate exceeded for %s. redirect the packets.",i)
#      connection.send( of.ofp_flow_mod(                        
#                                       match=of.ofp_match(dl_type=0x800,nw_dst="10.10.1.3/24",tp_dst=80 )))
#      del srcip_count[i]
#      log.debug("Host %s blocked and removed from the list",i)


#    log.debug("packet_count in the list:%s",i)

#  log.info("Web traffic from %s:(%s packets) ", 
#    dpidToStr(event.connection.dpid), web_packet)
#  dpid = event.connection.dpid

def send_packet(event,packet_count,web_packet):
  srcip_count[packet_count]=web_packet
      
  log.debug("list_of_ip_counts=%s",srcip_count)
  for i in srcip_count:
    if srcip_count[i]>15:
      log.debug("packet-rate exceeded for %s. redirect the packets.",i)
#*******      
      for connection in core.openflow._connections.values():
#        connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

        connection.send( of.ofp_flow_mod(                        
                                       match=of.ofp_match(dl_type=0x800,nw_src=i,nw_dst="10.10.1.0/24",tp_dst=80 )))
#*******
      del srcip_count[i]
      log.debug("Host %s blocked and removed from the list",i)

  

# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
#  log.debug("PortStatsReceived from %s: %s", 
#    dpidToStr(event.connection.dpid), stats)
    
def handle_packetIn (self,event):
  inport = event.port
  packet = event.parsed
  log.debug("source_ip=%s" %
                  (packet.next.srcip))

  if packet.type==ethernet.IP_TYPE:
    ipv4_packet=event.parsed.find("ipv4")
    src_ip=ipv4_packet.srcip
  if not packet.parsed:
    log.warning("%i ignoring unparsed packet", dpid)
    return

 # if isinstance(packet.next, ipv4):
#  log.info("%i IP %s => %s", dpid,
#                packet.next.srcip,packet.next.dstip)
#  log.info("installing flow for %s.%i -> %s.%i" %
#                  (packet.src, event.port, packet.dst, port))
#  log.debug("installing flow for %s.%i -> %s.%i" %
#                  (packet.next.srcip, event.port, packet.dst, port))
  




  # attach handsers to listners
#core.openflow.addListenerByName("Packet_in received", 
#    handle_packetIn) 

core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
core.openflow.addListenerByName("PortStatsReceived", 
    _handle_portstats_received) 

  # timer set to execute every five seconds
Timer(10, _timer_func, recurring=True)