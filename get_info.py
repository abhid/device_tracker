from netmiko import ConnectHandler
import redis
import getpass
import json
import schedule
import time

def get_info(user, pwd):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    sw_list = ["10.120.254.2", "10.100.254.2", "10.100.254.3"]
    redis_db = redis.Redis(host="localhost")

    for sw in sw_list:
        cisco_3850 = {
            'device_type': 'cisco_ios',
            'ip':   sw,
            'username': user,
            'password': pwd
        }

        net_connect = ConnectHandler(**cisco_3850)
        hostname = net_connect.find_prompt()[:-1]
        serial = net_connect.send_command("show ver | in System Serial").split(" ")[-1]
        arp_table = net_connect.send_command("show ip arp", use_textfsm=True)
        fdb = net_connect.send_command("show mac address-table", use_textfsm=True)
        for entry in arp_table:
            entry["switch"] = hostname
            entry["switch_ip"] = sw
            entry["switch_serial"] = serial
            redis_db.rpush("arp_table_new", json.dumps(entry))
        for entry in fdb:
            entry["switch"] = hostname
            entry["switch_ip"] = sw
            entry["switch_serial"] = serial
            redis_db.rpush("fdb_new", json.dumps(entry))
    redis_db.delete("arp_table")
    redis_db.rename("arp_table_new", "arp_table")
    redis_db.delete("fdb")
    redis_db.rename("fdb_new", "fdb")


user = input("Username:")
pwd = getpass.getpass("Password:")

# Run get_info every 5 minutes to download the latest info from the switches
schedule.every(5).minutes.do(get_info, user, pwd)

get_info(user, pwd)
while True:
    schedule.run_pending()
    time.sleep(1)