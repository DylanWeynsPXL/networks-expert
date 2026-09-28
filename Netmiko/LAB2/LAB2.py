from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host:": "172.168.16.2",
    "username": "student",
    "password": "cisco"
}

connection = ConnectHandler(**device)

output = connection.send_command("show ip interface brief")

print(output)

connection.disconnect()