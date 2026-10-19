# LAB 3 - Router- en switchmanagement met SSH

Deze handleiding gebruikt de adressering uit het meegeleverde netwerkschema. Voor
tafel 16 is het managementsubnet `172.16.16.0/26` met subnetmasker
`255.255.255.192`.

> Gebruik je een andere tafel, vervang dan overal `16` door je tafelnummer.

## Deel 1 - Voorbereiding


De router krijgt het tweede hostadres van het subnet: `172.16.16.2`.

```cisco
enable
configure terminal
hostname LAB-SR16-R01

! 1. Hoofdinterface aanzetten zonder IP
interface GigabitEthernet0/0/0
 description Uplink naar SW1 poort Gi1/0/2
 no ip address
 no shutdown
exit

! 2. Management sub-interface voor VLAN 116
interface GigabitEthernet0/0/0.116
 description Management VLAN 116
 encapsulation dot1Q 116
 ip address 172.16.16.2 255.255.255.192
 no shutdown
exit

! 3. SSH Toegang op de router
ip domain name student.local
username student privilege 15 secret pxl
crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 4
 login local
 transport input ssh
exit
end
```

Controleer daarna of de interface actief is:

```cisco
show ip interface brief
```

Test de SSH-configuratie vanaf een pc in hetzelfde subnet:

```powershell
ssh student@172.16.16.2
```

### 3. SW1 voorbereiden voor SSH en management

SW1 gebruikt het derde hostadres (`172.16.16.4`) op de management-SVI van
VLAN 116. Poort 1 is de managementpoort voor een eindapparaat en poort 2 is
de uplink naar de router.

```cisco
enable
configure terminal
hostname LAB-SR16-SW01

! 1. VLANs aanmaken
vlan 99
 name Native-Vlan
vlan 116
 name Management
vlan 216
 name VM-Hosts
vlan 316
 name Appliance-Servers
vlan 416
 name Data-Users
exit

! 2. Switch SVI en gateway instellen
interface Vlan116
 description Management VLAN
 ip address 172.16.16.4 255.255.255.192
 no shutdown
exit

ip default-gateway 172.16.16.2

! 3. SSH Toegang op de switch
ip domain name student.local
username student privilege 15 secret pxl
crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 4
 login local
 transport input ssh
exit

! 4. Poort Gi1/0/1 naar beheer-PC (Access in VLAN 116)
interface GigabitEthernet1/0/1
 description Management-aansluiting PC
 switchport mode access
 switchport access vlan 116
 spanning-tree portfast
 no shutdown
exit

! 5. Poort Gi1/0/2 naar router G0/0/0 (Trunk)
interface GigabitEthernet1/0/2
 description Uplink naar router G0/0/0
 switchport trunk encapsulation dot1q    ! Sla over als de switch dit commando niet herkent
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 99,116,216,316,416
 no shutdown
exit
end
```


Controleer de configuratie:

```cisco
show ip interface brief
show vlan brief
show interfaces status
```

Poort 22 moet in VLAN 116 staan en poort 24 moet verbonden zijn met
`GigabitEthernet0/0/0` van de router. Test ten slotte vanaf een pc:

```powershell
ssh student@172.16.16.4
```