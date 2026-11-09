from netmiko import ConnectHandler

# Verbindingsgegevens voor R1 (Tafel 16)
device = {
    "device_type": "cisco_ios",
    "host": "172.16.16.2",
    "username": "student",
    "password": "pxl",
}

# Configuratie-commando's voor R1 (Tafel 16 - LAB 6)
config_commands = [
    # 1. Hostname
    "hostname LAB-SR16-R01",

    # 2. Hoofdinterface G0/0/0 klaarmaken voor sub-interfaces (trunk naar switch)
    "interface GigabitEthernet0/0/0",
    "description Trunk naar SW1",
    "no ip address",
    "no shutdown",
    "exit",

    # Sub-interface G0/0/0.116 (Management VLAN 116)
    "interface GigabitEthernet0/0/0.116",
    "description Management VLAN 116",
    "encapsulation dot1Q 116",
    "ip address 172.16.16.2 255.255.255.192",
    "no shutdown",
    "exit",

    # Sub-interface G0/0/0.216 (VM-Hosts VLAN 216)
    "interface GigabitEthernet0/0/0.216",
    "description VM-Hosts VLAN 216",
    "encapsulation dot1Q 216",
    "ip address 172.16.16.66 255.255.255.192",
    "no shutdown",
    "exit",

    # Sub-interface G0/0/0.316 (Appliance-Servers VLAN 316)
    "interface GigabitEthernet0/0/0.316",
    "description Appliance-Servers VLAN 316",
    "encapsulation dot1Q 316",
    "ip address 172.16.16.130 255.255.255.192",
    "no shutdown",
    "exit",

    # Sub-interface G0/0/0.416 (Data-Users VLAN 416)
    "interface GigabitEthernet0/0/0.416",
    "description Data-Users VLAN 416",
    "encapsulation dot1Q 416",
    "ip address 172.16.16.194 255.255.255.192",
    "no shutdown",
    "exit",

    # 3. Externe uplink G0/0/1 naar switch LAB-SR2-SW10
    "interface GigabitEthernet0/0/1",
    "description Uplink naar externe switch LAB-SR2-SW10",
    "ip address 10.199.66.216 255.255.255.224",
    "no shutdown",
    "exit",

    # 4. Default route via Core Router LAB-CR1-R04 (10.199.66.200)
    "ip route 0.0.0.0 0.0.0.0 10.199.66.200",

    # 5. OSPF Process 10
    "router ospf 10",
    "default-information originate",
    "network 172.16.16.192 0.0.0.63 area 0",
    "exit",

    # 6. RESTCONF en HTTPS server activeren
    "ip http server",
    "ip http secure-server",
    "ip http authentication local",
    "restconf",
]

print("Verbinden met LAB-SR16-R01...")
try:
    connection = ConnectHandler(**device)
    print("Configuratie doorvoeren via Netmiko...")
    output = connection.send_config_set(config_commands)
    print(output)

    # Opslaan in startup-config
    print("\nConfiguratie opslaan...")
    connection.save_config()

    # Verificatie commando's
    print("\n=== INTERFACE OVERZICHT ===")
    print(connection.send_command("show ip interface brief"))

    print("\n=== ROUTING TABEL ===")
    print(connection.send_command("show ip route"))

    print("\n=== RESTCONF / HTTP STATUS ===")
    print(connection.send_command("show running-config | include restconf|http"))

    connection.disconnect()
    print("\nKlaar! De router is geconfigureerd en klaar voor LAB 6.")
except Exception as e:
    print(f"Fout tijdens verbinding: {e}")
