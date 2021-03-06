# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/python

import sys
import os
import binascii
_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_THIS_DIR, "tests", "pd_thrift"))

sys.path.append(os.path.join(_THIS_DIR, "..", "..", "testutils"))

from utils import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TMultiplexedProtocol

from p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *

import p4_pd_rpc.hello_switch as p4_module
import mc_pd_rpc.mc as mc_module
import conn_mgr_pd_rpc.conn_mgr as conn_mgr_module

transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)
bprotocol = TBinaryProtocol.TBinaryProtocol(transport)

mc_protocol = TMultiplexedProtocol.TMultiplexedProtocol(bprotocol, "mc")
conn_mgr_protocol = TMultiplexedProtocol.TMultiplexedProtocol(bprotocol, "conn_mgr")
p4_protocol = TMultiplexedProtocol.TMultiplexedProtocol(bprotocol, "hello_switch")

client = p4_module.Client(p4_protocol)
mc = mc_module.Client(mc_protocol)
conn_mgr = conn_mgr_module.Client(conn_mgr_protocol)
transport.open()

sess_hdl = conn_mgr.client_init(16)
dev_tgt = DevTarget_t(0, hex_to_i16(0xFFFF))

match_spec =  hello_switch_dmac_match_spec_t(
    ethernet_dstAddr = binascii.unhexlify("aabbccddeeff")
)

action_spec =  hello_switch_forward_action_spec_t(
    action_port = 3
)

# Set drop as the default action (when there is a table miss)
client.dmac_set_default_action__drop(sess_hdl,dev_tgt);

# Add one entry to the table
client.dmac_table_add_with_forward(sess_hdl,dev_tgt,match_spec,action_spec);
