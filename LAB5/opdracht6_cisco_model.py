from getpass import getpass
import xml.dom.minidom

from ncclient import manager


HOST = "172.16.16.2"
USER = "student"
TABLE_NUMBER = 16
PASSWORD = getpass("Wachtwoord: ")


def connect():
    return manager.connect(
        host=HOST,
        port=830,
        username=USER,
        password=PASSWORD,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        device_params={"name": "iosxe"},
        timeout=30,
    )


def pretty(reply):
    print(xml.dom.minidom.parseString(reply.xml).toprettyxml(indent="  "))


HOSTNAME = f"""
<config>
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname>LAB-SR{TABLE_NUMBER}-R01-NC{TABLE_NUMBER}</hostname>
  </native>
</config>
"""


with connect() as m:
    pretty(m.edit_config(target="running", config=HOSTNAME))
