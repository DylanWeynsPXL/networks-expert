# LAB 6 - Netwerkinfrastructuur en RESTCONF Voorbereiding

Deze handleiding beschrijft de volledige configuratie van de router en switch voor **LAB 6 (RESTCONF in de praktijk)**, gebaseerd op het netwerkschema van **LAB 1 - Basic LAN Network Infrastructure** en de richtlijnen uit `LAB_6_-_RESTCONF_in_de_praktijk.docx`.

Voor **Tafel 16** (tafelnummer $x = 16$) gelden de volgende VLAN's en subnets:

| VLAN | Naam | Subnet | Netmask | Eerste bruikbare IP (Gateway) | Router IP (2e client) | Switch IP (4e client) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VLAN 99** | Native-Vlan | - | - | - | - | - |
| **VLAN 116** | Management | `172.16.16.0/26` | `255.255.255.192` | `172.16.16.1` | `172.16.16.2` | `172.16.16.4` |
| **VLAN 216** | VM-Hosts | `172.16.16.64/26` | `255.255.255.192` | `172.16.16.65` | `172.16.16.66` | - |
| **VLAN 316** | Appliance-Servers | `172.16.16.128/26` | `255.255.255.192` | `172.16.16.129` | `172.16.16.130` | - |
| **VLAN 416** | Data-Users | `172.16.16.192/26` | `255.255.255.192` | `172.16.16.193` | `172.16.16.194` | - |

Daarnaast is er een **externe uplink** vanaf de router naar de centrale externe switch:
- **Externe switch:** `LAB-SR2-SW10` ("Any port can be used")
- **Subnet:** `10.199.66.192/27` (netmask `255.255.255.224`)
- **Router uplink (G0/0/1):** `10.199.66.216/27` (`10.199.66.20x` met $x=16$)
- **Core Router / Datacenter Gateway (LAB-CR1-R04):** `10.199.66.200`
- **Datacenter Services:** DNS/DHCP (`10.199.64.66`), TFTP (`10.199.64.134`), Domein `data.labnet.local`

> [!NOTE]
> Gebruik je een ander tafelnummer, vervang dan overal `16` door je eigen tafelnummer $x$.

---

## Deel 1 - Router Configuratie (LAB-SR16-R01)

Sluit aan op de consolepoort van router `LAB-SR16-R01`. Op de router configureren we:
1. De interne trunk-koppeling naar de switch (`GigabitEthernet0/0/0`) met sub-interfaces voor alle VLAN's.
2. De externe uplink naar `LAB-SR2-SW10` (`GigabitEthernet0/0/1`).
3. Routing (default route en OSPF-proces 10).
4. SSH-toegang voor beheer.
5. **RESTCONF en HTTPS** (poort 443) zodat RESTCONF API-calls ontvangen kunnen worden.

```cisco
enable
configure terminal
hostname LAB-SR16-R01

! ==========================================
! 1. Interne interface naar lokale switch
! ==========================================
interface GigabitEthernet0/0/0
 description Trunk naar SW1 (Gi1/0/24)
 no ip address
 no shutdown
exit

! Sub-interface VLAN 116 (Management)
interface GigabitEthernet0/0/0.116
 description Management VLAN 116
 encapsulation dot1Q 116
 ip address 172.16.16.2 255.255.255.192
 no shutdown
exit

! Sub-interface VLAN 216 (VM-Hosts)
interface GigabitEthernet0/0/0.216
 description VM-Hosts VLAN 216
 encapsulation dot1Q 216
 ip address 172.16.16.66 255.255.255.192
 no shutdown
exit

! Sub-interface VLAN 316 (Appliance-Servers)
interface GigabitEthernet0/0/0.316
 description Appliance-Servers VLAN 316
 encapsulation dot1Q 316
 ip address 172.16.16.130 255.255.255.192
 no shutdown
exit

! Sub-interface VLAN 416 (Data-Users)
interface GigabitEthernet0/0/0.416
 description Data-Users VLAN 416
 encapsulation dot1Q 416
 ip address 172.16.16.194 255.255.255.192
 no shutdown
exit

! ==========================================
! 2. Externe link naar switch LAB-SR2-SW10
! ==========================================
interface GigabitEthernet0/0/1
 description Uplink naar externe switch LAB-SR2-SW10
 ip address 10.199.66.216 255.255.255.224
 no shutdown
exit

! ==========================================
! 3. Routing (Default route & OSPF)
! ==========================================
! Default route via Core Router LAB-CR1-R04 (.200)
ip route 0.0.0.0 0.0.0.0 10.199.66.200

! OSPF proces 10 (zoals gebruikt in LAB 3 en LAB 6)
router ospf 10
 default-information originate
 network 172.16.16.192 0.0.0.63 area 0
exit

! ==========================================
! 4. SSH Beheertoegang
! ==========================================
ip domain name student.local
username student privilege 15 secret pxl
crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 4
 login local
 transport input ssh
exit

! ==========================================
! 5. RESTCONF & HTTPS Server Inschakelen (LAB 6)
! ==========================================
ip http server
ip http secure-server
ip http authentication local
restconf
exit
```

### Verificatie Router
Controleer of alle interfaces en sub-interfaces `up/up` zijn en of RESTCONF/HTTP draait:

```cisco
show ip interface brief
show ip route
show running-config | include restconf|http
```

---

## Deel 2 - Switch Configuratie (LAB-SR16-SW01)

Op de switch `LAB-SR16-SW01` maken we alle vereiste VLAN's aan, stellen we de management-SVI in op `172.16.16.4`, en richten we de poorten in:
- **Poort 21 en 22 (Gi1/0/21, Gi1/0/22):** Access in Management VLAN 116 voor de laptop / DEVASC VM (zoals gespecificeerd in `LAB_6_-_RESTCONF_in_de_praktijk.docx`).
- **Poort 24 (of Gi1/0/2):** Trunk naar routerpoort `GigabitEthernet0/0/0`.

```cisco
enable
configure terminal
hostname LAB-SR16-SW01

! ==========================================
! 1. VLANs aanmaken
! ==========================================
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

! ==========================================
! 2. Management SVI & Default Gateway
! ==========================================
interface Vlan116
 description Management SVI
 ip address 172.16.16.4 255.255.255.192
 no shutdown
exit

ip default-gateway 172.16.16.2

! ==========================================
! 3. SSH Beheertoegang
! ==========================================
ip domain name student.local
username student privilege 15 secret pxl
crypto key generate rsa modulus 2048
ip ssh version 2

line vty 0 4
 login local
 transport input ssh
exit

! ==========================================
! 4. Poorten 21 en 22 naar PC / DEVASC VM (VLAN 116)
! ==========================================
interface range GigabitEthernet1/0/21 - 22
 description Management-aansluiting PC / DEVASC VM
 switchport mode access
 switchport access vlan 116
 spanning-tree portfast
 no shutdown
exit

! ==========================================
! 5. Poort 24 (of Gi1/0/2) naar Router G0/0/0 (Trunk)
! ==========================================
interface GigabitEthernet1/0/24
 description Trunk uplink naar router G0/0/0
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 99,116,216,316,416
 no shutdown
exit
```

### Verificatie Switch
Controleer de statussen van de poorten en VLAN's:

```cisco
show ip interface brief
show vlan brief
show interfaces status
```

---

## Deel 3 - Laptop / DEVASC VM Netwerkadapter Configureren

Sluit je laptop of netwerkkabel aan op **poort 21 of poort 22** van de switch (in VLAN 116).

Geef de netwerkadapter van je laptop of VM een statisch IP-adres binnen het `/26` managementsubnet:
- **IP-adres:** `172.16.16.10` (of een ander vrij adres zoals `172.16.16.50`)
- **Subnetmasker:** `255.255.255.192` (`/26`)
- **Standaardgateway:** `172.16.16.2` (de router)

### Instellen via Windows PowerShell (als Administrator)
```powershell
New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 172.16.16.10 -PrefixLength 26 -DefaultGateway 172.16.16.2
```

### Instellen via Linux (DEVASC VM)
```bash
sudo ip addr add 172.16.16.10/26 dev eth0
sudo ip route add default via 172.16.16.2
```

---

## Deel 4 - Verificatie & RESTCONF Testen

### 1. Connectiviteit testen
Test vanaf je laptop of VM de verbinding naar de router, de switch en het datacenter:

```bash
# Ping naar de router sub-interface
ping -c 3 172.16.16.2

# Ping naar de switch SVI
ping -c 3 172.16.16.4

# Ping naar de router externe uplink
ping -c 3 10.199.66.216

# Ping naar de Core Router / Datacenter gateway
ping -c 3 10.199.66.200
```

### 2. SSH-toegang verifiëren
```bash
ssh student@172.16.16.2
ssh student@172.16.16.4
```

### 3. RESTCONF controleren (Opdracht 2 uit LAB 6)
Controleer via `curl` of RESTCONF data teruggeeft via HTTPS (poort 443):

```bash
# Hostname opvragen als JSON
curl -k -i -u student:pxl \
  -H "Accept: application/yang-data+json" \
  https://172.16.16.2/restconf/data/Cisco-IOS-XE-native:native/hostname

# Alle interfaces opvragen
curl -k -u student:pxl \
  -H "Accept: application/yang-data+json" \
  https://172.16.16.2/restconf/data/ietf-interfaces:interfaces
```
