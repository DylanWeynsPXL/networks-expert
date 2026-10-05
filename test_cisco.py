from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "172.16.16.2",
    "username": "admin",
    "password": "cisco",
}

connection = ConnectHandler(**device)
output = connection.send_command("show ip interface brief")
connection.disconnect()

admin_down_interfaces = []
down_interfaces = []
up_interfaces = []

for line in output.splitlines():
    line = line.strip()
    if not line or line.startswith("Interface"):
        continue

    parts = line.split()
    if not parts:
        continue

    interface_name = parts[0]
    if "administratively down" in line.lower():
        admin_down_interfaces.append(interface_name)
    elif "down" in line.lower():
        down_interfaces.append(interface_name)
    elif "up" in line.lower():
        up_interfaces.append(interface_name)
        
print("=== Interface Status Overzicht ===\n")

print(f"Interfaces Up ({len(up_interfaces)}):")
for iface in up_interfaces:
    print(f"  - {iface}")

print(f"\nInterfaces Administratively Down ({len(admin_down_interfaces)}):")
for iface in admin_down_interfaces:
    print(f"  - {iface}")

print(f"\nInterfaces Down ({len(down_interfaces)}):")
for iface in down_interfaces:
    print(f"  - {iface}")