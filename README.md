                                                                                 **------ STEPS TO LAUNCH THE PROJECT ------**

STEP 1 : Upload the **docker-compose.yml** file in your local machine and launch it by the command : **docker-compose up -d**

You can see all the services listed with : **docker ps** but for now we gonna focus on a Grafana and Zabbix services :

STEP 2 : Go to **http://localhost:3000** to access grafana interface 

STEP 3 : Go to the plugin section and type **Zabbix** and then click install >> enable.

STEP 4 : Go the data sources section and add zabbix data source then enter: **http://zabbix-web:8080/api_jsonrpc.php**.

STEP 5 : In Zabbix Connection section type **User and password** in the Auth type field and the credentiels by default Username : Admin / Password : zabbix.

STEP 6 : Then click the Save & test button.

Once the connection Grafana-Zabbix is established, we can create dashboards related to zabbix:

STEP 7 : Define all the clients hosts in the **inventory.yaml**.

STEP 8 : Create a vault file where we gonna store all SSH credentiels and passwords with : **ansible-vault create vault.yaml**.

STEP 10 : Initial the one-time connection SSH key-based between the orchetrator and the clients by copy the public key generated in STEP 1 and paste it in the authorized_keys file in the clients hosts. 

STEP 9 : Generate the SSH key in the orchetrator by using the command :   **"ssh-keygen -t rsa -b 4096 -f id_rsa"**.

STEP 11 : Once the public key is present in the **authorized_keys** file located at the machine clients you can run the playbook.




