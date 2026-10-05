# Handleiding: Cisco Router Direct Configureren & Automatiseren met Netmiko

Deze handleiding beschrijft hoe je via een rechtstreekse Ethernet-kabel (zonder tussenkomst van een switch) verbinding maakt met een Cisco-router (interface `GigabitEthernet0/0/0`), SSH configureert, een statisch IP op je laptop instelt en vervolgens via Python (Netmiko) netwerkcommando's automatiseert.

---

## 1. Cisco Router Basisconfiguratie (via Console)

Sluit eerst de consolekabel aan op de router om de initiële management- en SSH-configuratie door te voeren.

### Interface configureren en inschakelen
Voor **Tafel 16** valt het management-subnet binnen `172.16.16.0/26` (subnetmasker `255.255.255.192`). We kennen het tweede host-adres toe aan de router:

```cisco
enable
configure terminal
interface GigabitEthernet0/0/0
 description Direct Link to Laptop Management
 ip address 172.16.16.2 255.255.255.192
 no shutdown
exit

hostname LAB-SR16-R01
ip domain-name data.labnet.local

crypto key generate rsa modulus 2048
ip ssh version 2

username admin privilege 15 secret cisco

line vty 0 4
 transport input ssh
 login local
 exit
```
## 2. Laptop Netwerkadapter Configureren (Windows)

Omdat de switch en DHCP-server zijn overgeslagen, moet de bekabelde netwerkadapter van je laptop statisch geconfigureerd worden in hetzelfde /26-subnet.

Sluit een standaard patchkabel rechtstreeks aan tussen de Ethernet-poort van je laptop en poort GigabitEthernet0/0/0 van de router.

Open PowerShell als Administrator (rechtermuisknop op PowerShell > Als administrator uitvoeren).

Stel het IP-adres en de gateway in:

```powershell
    New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 172.16.16.10 -PrefixLength 26 -DefaultGateway 172.16.16.2
```