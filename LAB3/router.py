from netmiko import ConnectHandler

# Verbindingsgegevens voor R1
device = {
    "device_type": "cisco_ios",
    "host": "172.16.16.2",
    "username": "student",
    "password": "pxl",
}

# Configuratie-commando's voor R1 (Tafel 16)
config_commands = [
    # 1. Hostname
    "hostname R1",

    # 2. Hoofdinterface G0/0/0 klaarmaken voor sub-interfaces
    "interface GigabitEthernet0/0/0",
    "no ip address",
    "no shutdown",
    "exit",

    # Sub-interface G0/0/0.116 (Management)
    "interface GigabitEthernet0/0/0.116",
    "encapsulation dot1Q 116",
    "ip address 172.16.16.2 255.255.255.192",
    "exit",

    # Sub-interface G0/0/0.216 (VM-Hosts)
    "interface GigabitEthernet0/0/0.216",
    "encapsulation dot1Q 216",
    "ip address 172.16.16.66 255.255.255.192",
    "exit",

    # Sub-interface G0/0/0.316 (Appliance-Servers)
    "interface GigabitEthernet0/0/0.316",
    "encapsulation dot1Q 316",
    "ip address 172.16.16.130 255.255.255.192",
    "exit",

    # Sub-interface G0/0/0.416 (Data-Users)
    "interface GigabitEthernet0/0/0.416",
    "encapsulation dot1Q 416",
    "ip address 172.16.16.194 255.255.255.192",
    "exit",

    # 3. Uplink G0/0/1 configureren
    "interface GigabitEthernet0/0/1",
    "ip address 10.199.66.216 255.255.255.224",
    "no shutdown",
    "exit",

    # 4. Default route via G0/0/1
    "ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/1",

    # 5. OSPF Process 10
    "router ospf 10",
    "default-information originate",
    "network 172.16.16.192 0.0.0.63 area 0",
    "exit",

    # 6. ACL's configureren (Verkeer naar/van buiten via G0/0/1)
    # Binnenkomend verkeer op G0/0/1: niet naar VLAN 116, wel naar 216, 316, 416
    "ip access-list extended OUTSIDE_TO_INSIDE",
    "deny ip any 172.16.16.0 0.0.0.63",
    "permit ip any 172.16.16.64 0.0.0.63",
    "permit ip any 172.16.16.128 0.0.0.63",
    "permit ip any 172.16.16.192 0.0.0.63",
    "deny ip any any",
    "exit",

    # Uitgaand verkeer op G0/0/1: niet van VLAN 116, wel van 216, 316, 416
    "ip access-list extended INSIDE_TO_OUTSIDE",
    "deny ip 172.16.16.0 0.0.0.63 any",
    "permit ip 172.16.16.64 0.0.0.63 any",
    "permit ip 172.16.16.128 0.0.0.63 any",
    "permit ip 172.16.16.192 0.0.0.63 any",
    "deny ip any any",
    "exit",

    # ACL's toepassen op buiteninterface G0/0/1
    "interface GigabitEthernet0/0/1",
    "ip access-group OUTSIDE_TO_INSIDE in",
    "ip access-group INSIDE_TO_OUTSIDE out",
    "exit",
]

print("Verbinden met R1...")
connection = ConnectHandler(**device)

print("Configuratie doorvoeren via Netmiko...")
output = connection.send_config_set(config_commands)
print(output)

# Opslaan in startup-config
print("Configuratie opslaan...")
connection.save_config()

# Verificatie
check_ip = connection.send_command("show ip interface brief")
check_routes = connection.send_command("show ip route")
check_ospf = connection.send_command("show ip ospf interface brief")

print("\n=== INTERFACE OVERZICHT ===")
print(check_ip)

print("\n=== ROUTING TABEL ===")
print(check_routes)

connection.disconnect()
print("\nKlaar!")