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
import sqlite3
from pox.core import core
from pox.lib.util import dpidToStr

# main functiont to launch the module
from pox.lib.recoco import Timer

import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

# include as part of the betta branch
from pox.openflow.of_json import *
import os

log = core.getLogger()

#list to maintain the srcip and packet-count record

srcip_count={}
srcip_record={}
tmp_src_ip=None
srcip_blocked={}
rate_limit=50
# handler for timer function that sends the requests to all the
# switches connected to the controller.


def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))

def _timer_display():
  global tmp_src_ip
  if tmp_src_ip :
    srcip_count[tmp_src_ip]="Blocked"
    print srcip_count[tmp_src_ip]
    tmp_src_ip=None
    
  if srcip_count:
    os.system("clear")
    print "List of Blocked IPs"
    print "Blocked IP: %s" %(srcip_blocked)
    print "\n"
    print "List of active IPs and their packet counts"
    for i in srcip_count:
      print "%s:--> %s"%(i,srcip_count[i])
    srcip_count.clear()
    
# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)

# Get number of bytes/packets in flows for web traffic only
  web_packet = {}
  last_Packet_count=0
  for f in event.stats:
    if f.match.tp_dst==80:
      if web_packet.has_key(str(f.match.nw_src)):
        last_Packet_count= web_packet[str(f.match.nw_src)]
      web_packet[str(f.match.nw_src)] = last_Packet_count + f.packet_count
      last_Packet_count=0
      send_packet(event,str(f.match.nw_src),web_packet)
      
      
def send_packet(event,src_ip,web_packet):
  global srcip_count
  global srcip_blocked
  global rate_limit
  skip_loop=0
  if srcip_blocked:
    for i in srcip_blocked:
      if i==src_ip:
        skip_loop=1
  if skip_loop==0:
    srcip_count[src_ip]=web_packet[src_ip]
    global tmp_src_ip
    tmp_src_ip=None
    srcip_count1=srcip_count

# If an user exceeds the threshold
    for i in srcip_count:
      if srcip_count[i]>rate_limit:
        tmp_src_ip=i
        log.debug("packet-rate exceeded for %s. redirect the packets.",i)

# Add a flow to block the user
        for connection in core.openflow._connections.values():
          connection.send( of.ofp_flow_mod(match=of.ofp_match(
            nw_proto=6,dl_type=0x800,nw_src=i,nw_dst="10.10.1.0/24",tp_dst=80 )))
        log.debug("Host %s blocked and removed from the list",i)
    if tmp_src_ip :
      srcip_blocked[tmp_src_ip]="Blocked"
      print "Host %s blocked and removed from the list"%(tmp_src_ip)
      srcip_count[tmp_src_ip]="Blocked"
      tmp_src_ip=None      
 
# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
    

core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 

Timer(.01, _timer_func, recurring=True)
Timer(.5, _timer_display, recurring=True)
