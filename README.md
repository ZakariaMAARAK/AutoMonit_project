# 🖥️ Advanced Cloud Infrastructure Monitoring & Observability Platform

[![Prometheus](https://img.shields.io/badge/PROMETHEUS-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/GRAFANA-F46800?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/DOCKER-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Loki](https://img.shields.io/badge/LOKI-F4A261?style=for-the-badge&logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nginx](https://img.shields.io/badge/NGINX-009639?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org/)
[![MySQL](https://img.shields.io/badge/MYSQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/REDIS-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)

---

## Overview :

This project aims to deploy an optimal and automated supervision solution to remote endpoints via a secured tunnel IPsec.

![High Quality Diagram](https://github.com/ZakariaMAARAK/project_PFE/blob/main/Global_Conception.png)

## Technologies and frameworks :
---

- Docker & Docker compose
- Ansible  
- Zabbix 
- APIs  
- Prometheus  
- Grafana  
- SSH
- Alertmanager
- Wazuh (SIEM)
- AWX
- IPsec

## Getting started :
---

- Setup a virtualized environnement : Install VMware Workstatioin Pro where we gonna put the server (Orchestrator) and the  VMs clients (Debian + CentOS)

- You can refer to the Steps listed in the next section :

## Steps to launch the playbook :
---

- STEP 1 : Upload the **docker-compose.yml** file in your local machine and launch it by using the command : **docker-compose up -d**

You can see all the services listed with : **docker ps** but for now we gonna focus on a Grafana and Zabbix services :

- STEP 2 : Go to **http://localhost:3000** to access grafana interface 

- STEP 3 : Go to the plugin section and type **Zabbix** and then click install >> enable.

- STEP 4 : Go the data sources section and add zabbix data source then enter: **http://zabbix-web:8080/api_jsonrpc.php**.

- STEP 5 : In Zabbix Connection section type **User and password** in the Auth type field and the credentiels by default Username : Admin / Password : zabbix.

- STEP 6 : Then click the Save & test button.

Once the connection Grafana-Zabbix is established, we can create dashboards related to zabbix:

- STEP 7 : In Grafana UI, go to Administration >> Users and access >> Service accounts section then click Add service account give it an name and Role Admin and click create and +Add service account token button to generate an api token.

- STEP 8 : Copy then paste the API token to the script **create_dashboard.py**.

- STEP 9 : Create the dashboard json template **dashboard_template.json** one-time and then import it and insert it in the script **create_dashboard.py**.

- STEP 10 : Define all the clients hosts in the **inventory.yaml**.

- STEP 11 : Generate the SSH key in the orchetrator by using the command : **ssh-keygen -t rsa -b 4096 -f id_rsa**.

- STEP 12 : Create a vault file where we gonna store all SSH credentiels and passwords with : **ansible-vault create vault.yaml**.

- STEP 13 :

   Option 1 : Run the **playbook2.yaml** to automatically transfer the SSH public key to clients : **ansible-playbook -i inventory.yaml playbook2.yaml --ask-vault-pass**

   Option 2 : Initial the one-time connection SSH key-based between the orchetrator and the clients by copying the public key generated in STEP 1 and paste it manually in the **authorized_keys** file in the clients hosts or via the command : **ssh-copy-id client2@192.168.220.139**. (NB: **client2** and **192.168.220.139** are examples you can replace them with your clients).
  

- STEP 14 : Once the public key is present in the **authorized_keys** file located at the machine's clients you can run the playbook : **ansible-playbook -i inventory.yaml playbook.yaml --ask-vault-pass**
