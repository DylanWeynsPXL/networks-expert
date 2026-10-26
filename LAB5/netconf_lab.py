from ncclient import manager
from getpass import getpass
import xml.dom.minidom
from urllib.parse import parse_qs, urlsplit
 
HOST = "172.16.16.2"
USER = "student"
PASSWORD = getpass("Wachtwoord: ")
 
 
def connect():
    return manager.connect(
        host=HOST, port=830, username=USER, password=PASSWORD,
        hostkey_verify=False, allow_agent=False, look_for_keys=False,
        device_params={"name": "iosxe"}, timeout=30,
    )
 
 
def pretty(reply):
    print(xml.dom.minidom.parseString(reply.xml).toprettyxml(indent="  "))
 
FILTER_IF = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name/>
    <description/>
    <enabled/>
  </interface>
</interfaces>
"""
FILTER_STATE = """
<interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name/>
    <oper-status/>
  </interface>
</interfaces-state>
"""

FILTER_NATIVE_HOSTNAME = """
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
  <hostname/>
</native>
"""

x = 16
 
LOOPBACK = f"""
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"
              xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
    <interface>
      <name>Loopback{100 + x}</name>
      <description>Aangemaakt via NETCONF door tafel {x}</description>
      <type>ianaift:softwareLoopback</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.50.{x}.1</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>
"""

DELETE_LOOP = f"""
<config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface nc:operation="remove">
      <name>Loopback{100 + x}</name>
    </interface>
  </interfaces>
</config>
"""


 
with connect() as m:

    print("LOOPBACK INTERFACE")
    print("==============================")
    reply = m.edit_config(target="running", config=LOOPBACK)
    print(reply)

    print("DELETE LOOPBACK INTERFACE")
    print("==============================")
    reply = m.edit_config(target="running", config=DELETE_LOOP)
    print(reply)

    print("CISCO NATIVE HOSTNAME")
    print("==============================")
    pretty(
        m.get_config(
            source="running",
            filter=("subtree", FILTER_NATIVE_HOSTNAME),
        )
    )


    print("FILTER IF")
    print("==============================")
    pretty(m.get_config(source="running", filter=("subtree", FILTER_IF)))


    print("FILTER STATE")
    print("==============================")
    pretty(m.get_config(source="running", filter=("subtree", FILTER_STATE)))


    print("FILTER STATE (get)")
    print("==============================")
    pretty(m.get(filter=("subtree", FILTER_STATE)))


    total_capabilities = 0
    requested_modules = {"ietf-interfaces", "Cisco-IOS-XE-native"}
    print("Session-id:", m.session_id)
    for cap in m.server_capabilities:
        total_capabilities += 1
        query = parse_qs(urlsplit(str(cap)).query)
        module = query.get("module", [None])[0]
        if module in requested_modules:
            revision = query.get("revision", ["niet vermeld"])[0]
            print(f"{module}: revision {revision}")
    print("Total capabilities:", total_capabilities)
