import json
from getpass import getpass
from urllib.parse import quote
import requests

# Waarschuwingen voor self-signed SSL-certificaten uitschakelen (enkel voor labo-omgeving)
requests.packages.urllib3.disable_warnings()

# ==========================================
# Instellingen Tafel 16
# ==========================================
x = 16
HOST = "172.16.16.2"
USER = "student"
PASSWORD = getpass("Wachtwoord (pxl): ") or "pxl"

BASE = f"https://{HOST}/restconf/data"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def call(method, path, body=None):
    """Generieke RESTCONF helper functie."""
    url = f"{BASE}/{path}"
    data = json.dumps(body) if body else None
    r = requests.request(
        method=method,
        url=url,
        auth=(USER, PASSWORD),
        headers=HEADERS,
        data=data,
        verify=False,
        timeout=30,
    )
    print(f"\n[{method}] {path} -> Status: {r.status_code}")
    return r


# ==========================================
# Opdracht 3: Alle interfaces opvragen
# ==========================================
print("\n" + "=" * 50)
print("OPDRACHT 3: Alle interfaces opvragen")
print("=" * 50)

r = call("GET", "ietf-interfaces:interfaces")
if 200 <= r.status_code <= 299:
    print("STATUS OK")
    print(f"{'Interface':<28} {'Enabled':<8} {'IP-Adres'}")
    print("-" * 50)
    for itf in r.json().get("ietf-interfaces:interfaces", {}).get("interface", []):
        ipv4 = itf.get("ietf-ip:ipv4", {}).get("address", [])
        ip = ipv4[0]["ip"] if ipv4 else "-"
        print(f"{itf['name']:<28} {str(itf.get('enabled', False)):<8} {ip}")


# ==========================================
# Opdracht 4: Gerichte opvraag (G0/0/0)
# ==========================================
print("\n" + "=" * 50)
print("OPDRACHT 4: GigabitEthernet0/0/0 inspecteren")
print("=" * 50)

naam = quote("GigabitEthernet0/0/0", safe="")
r = call("GET", f"ietf-interfaces:interfaces/interface={naam}")
if r.status_code == 200:
    print("Configuratie:")
    print(json.dumps(r.json(), indent=2))

r_state = call("GET", f"ietf-interfaces:interfaces-state/interface={naam}")
if r_state.status_code == 200:
    print("Operationele status:")
    print(json.dumps(r_state.json(), indent=2))


# ==========================================
# Opdracht 5: Loopback interface beheren
# ==========================================
print("\n" + "=" * 50)
print("OPDRACHT 5: Loopback interface (PUT, PATCH, DELETE)")
print("=" * 50)

NAME = f"Loopback{100 + x}"
PAD = f"ietf-interfaces:interfaces/interface={quote(NAME, safe='')}"

# 5a. Aanmaken met PUT
BODY = {
    "ietf-interfaces:interface": {
        "name": NAME,
        "description": f"Aangemaakt via RESTCONF door tafel {x}",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [{"ip": f"10.50.{x}.1", "netmask": "255.255.255.0"}]
        },
    }
}
r = call("PUT", PAD, BODY)
print("PUT resultaat:", r.status_code)

# 5b. Wijzigen met PATCH
PATCH_BODY = {
    "ietf-interfaces:interface": {
        "name": NAME,
        "description": "Gewijzigd via PATCH door tafel 16",
    }
}
r = call("PATCH", PAD, PATCH_BODY)
print("PATCH resultaat:", r.status_code)

# 5c. Verwijderen met DELETE
r = call("DELETE", PAD)
print("DELETE resultaat:", r.status_code)


# ==========================================
# Opdracht 6: OSPF beheren
# ==========================================
print("\n" + "=" * 50)
print("OPDRACHT 6: OSPF inspecteren en aanpassen")
print("=" * 50)

# 6b. OSPF lezen
r = call("GET", "Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf")
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))

# 6c. Network-statement toevoegen
OSPF_ID = 10
OSPF_PAD = f"Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf={OSPF_ID}"
OSPF_BODY = {
    "Cisco-IOS-XE-ospf:ospf": [{
        "id": OSPF_ID,
        "network": [{"ip": f"10.50.{x}.0", "wildcard": "0.0.0.255", "area": 0}],
    }]
}
r = call("PATCH", OSPF_PAD, OSPF_BODY)
print("OSPF PATCH resultaat:", r.status_code)

# Network-statement weer opruimen met DELETE
DELETE_NET_PAD = f"{OSPF_PAD}/network={quote(f'10.50.{x}.0,0.0.0.255,0', safe='')}"
r = call("DELETE", DELETE_NET_PAD)
print("OSPF DELETE resultaat:", r.status_code)

print("\nAlle opdrachten doorlopen!")
