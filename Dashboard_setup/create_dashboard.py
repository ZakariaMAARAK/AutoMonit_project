import json
import requests

ZABBIX_API_URL = "http://localhost:8080/api_jsonrpc.php"
ZABBIX_USERNAME = "Admin"
ZABBIX_PASSWORD = "zabbix"

GRAFANA_URL = "http://localhost:3000"
GRAFANA_API_TOKEN = "glsa_WheqMkk7BZni0yi7SOih1GLrp3lTzHEy_38813b3d" # NB : This Grafana API token session you can create your own (STEP 7/8)
TEMPLATE_FILE = "dashboard_template.json" # NB : This is the imported json template you can create your own and import it as well (STEP 9)


ZABBIX_DATASOURCE_UID = "aes45x3zoq874a"
PROMETHEUS_DATASOURCE_UID = "des469lkyb1tsb"  

HEADERS_GRAFANA = {
    "Authorization": f"Bearer {GRAFANA_API_TOKEN}",
    "Content-Type": "application/json"
}


def get_zabbix_api_token():
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": ZABBIX_USERNAME,
            "password": ZABBIX_PASSWORD
        },
        "id": 1
    }

    res = requests.post(ZABBIX_API_URL, headers={"Content-Type": "application/json"}, json=auth_payload)
    auth_response = res.json()

    if "result" in auth_response:
        token = auth_response["result"]
        print(f"[DEBUG] Zabbix Auth token: {token}")
        return token
    else:
        print(f"Authentication failed: {auth_response}")
        return None


def get_zabbix_hosts(api_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name"],
            "filter": {
                "status": "0"
            },
            "selectInterfaces": ["ip", "port", "available"]
        },
        "id": 1
    }

    res = requests.post(ZABBIX_API_URL, headers=headers, json=payload)
    response_json = res.json()

    if "result" in response_json:
        return response_json["result"]
    else:
        print("Failed to get hosts.")
        return []


def availability_to_text(value):
    if value == "1":
        return "available"
    elif value == "2":
        return "unavailable"
    return "unknown"


def get_or_create_folder_id(folder_name):
    res = requests.get(f"{GRAFANA_URL}/api/folders", headers=HEADERS_GRAFANA)
    if res.status_code == 200:
        folders = res.json()
        for folder in folders:
            if folder["title"].lower() == folder_name.lower():
                return folder["id"]

    payload = {"title": folder_name}
    res = requests.post(f"{GRAFANA_URL}/api/folders", headers=HEADERS_GRAFANA, json=payload)
    if res.status_code == 200:
        return res.json()["id"]
    else:
        print(f"[✘] Failed to create/get folder '{folder_name}': {res.status_code} - {res.text}")
        return 0


def ensure_prometheus_datasource():
    response = requests.get(f"{GRAFANA_URL}/api/datasources/uid/{PROMETHEUS_DATASOURCE_UID}", headers=HEADERS_GRAFANA)
    if response.status_code == 200:
        print("[✔] Prometheus datasource already exists.")
        return

    print("[➕] Creating Prometheus datasource...")

    payload = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://localhost:9090",
        "access": "proxy",
        "basicAuth": False,
        "uid": PROMETHEUS_DATASOURCE_UID,
        "isDefault": False
    }

    response = requests.post(f"{GRAFANA_URL}/api/datasources", headers=HEADERS_GRAFANA, json=payload)
    if response.status_code == 200:
        print("[✔] Prometheus datasource created.")
    else:
        print(f"[✘] Failed to create Prometheus datasource: {response.status_code} - {response.text}")


def create_dashboard_for_vm(host, interface_ip, port, availability_status):
    with open(TEMPLATE_FILE, "r") as f:
        template_json = json.load(f)

    vm_name = host["name"]
    host_name = host["host"]

    if "zabbix" in host_name.lower():
        zabbix_group = "Zabbix servers"
    else:
        zabbix_group = "Linux servers"

    folder_id = get_or_create_folder_id(zabbix_group)

    tags = [
        "Zabbix",
        f"IP:{interface_ip}",
        f"Port:{port}"
    ]

    template_json["title"] = f"Dashboard - {vm_name}"
    template_json["uid"] = f"dash-{host_name.lower()}"
    template_json["tags"] = tags

    # Replace placeholders
    for panel in template_json.get("panels", []):
        datasource = panel.get("datasource", {})
        if isinstance(datasource, dict):
            if datasource.get("type") == "prometheus":
                panel["datasource"]["uid"] = PROMETHEUS_DATASOURCE_UID
            elif datasource.get("type") == "alexanderzobnin-zabbix-datasource":
                panel["datasource"]["uid"] = ZABBIX_DATASOURCE_UID

        for target in panel.get("targets", []):
            if "host" in target and "filter" in target["host"]:
                target["host"]["filter"] = host_name
            if "group" in target and "filter" in target["group"]:
                target["group"]["filter"] = zabbix_group
            if "expr" in target:
                target["expr"] = target["expr"].replace("_VM_NAME_", host_name)

        if "title" in panel:
            panel["title"] = panel["title"].replace("_VM_NAME_", vm_name)

        if "alert" in panel and "name" in panel["alert"]:
            panel["alert"]["name"] = panel["alert"]["name"].replace("_VM_NAME_", vm_name)

    payload = {
        "dashboard": template_json,
        "overwrite": True,
        "folderId": folder_id
    }

    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        headers=HEADERS_GRAFANA,
        json=payload
    )

    if response.status_code == 200:
        print(f"[✔] Dashboard created for {vm_name} ({interface_ip}:{port}) - Status: {availability_status} in folder '{zabbix_group}'")
    else:
        print(f"[✘] Failed to create dashboard for {vm_name}: {response.status_code} - {response.text}")


if __name__ == "__main__":
    ensure_prometheus_datasource()

    api_token = get_zabbix_api_token()
    if not api_token:
        print("Authentication failed. Exiting.")
        exit(1)

    hosts = get_zabbix_hosts(api_token)

    for host in hosts:
        if host.get("interfaces"):
            interface = host["interfaces"][0]
            ip = interface.get("ip", "N/A")
            port = interface.get("port", "10050")
            availability = availability_to_text(interface.get("available", "0"))
            create_dashboard_for_vm(host, ip, port, availability)
