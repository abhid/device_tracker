from netmiko import ConnectHandler
import redis
import getpass
import json
import schedule
import time
from multiprocessing.dummy import Pool as ThreadPool

redis_db = redis.Redis(host="localhost")
redis_db.flushdb()

user = input("Username:")
pwd = getpass.getpass("Password:")

def get_info(sw):
    cisco_3850 = {
        'device_type': 'cisco_ios',
        'ip':   sw,
        'username': user,
        'password': pwd
    }
    print("[" + time.strftime("%H:%M:%S", time.gmtime()) + "] Connecting to " + sw)
    net_connect = ConnectHandler(**cisco_3850)
    hostname = net_connect.find_prompt()[:-1]
    serial = net_connect.send_command("show ver | in ID").split(" ")[-1]
    arp_table = net_connect.send_command("show ip arp", use_textfsm=True)
    fdb = net_connect.send_command("show mac address-table", use_textfsm=True)
    for entry in arp_table:
        entry["switch"] = hostname
        entry["switch_ip"] = sw
        entry["switch_serial"] = serial
        redis_db.rpush("arp:" + entry["mac"] + ":" + entry["address"], json.dumps(entry))
    if (type(fdb) == type([])):
        for entry in fdb:
            entry["switch"] = hostname
            entry["switch_ip"] = sw
            entry["switch_serial"] = serial
            redis_db.rpush("fdb:" + entry["destination_address"], json.dumps(entry))


print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
pool = ThreadPool(20)

sw_list = []
with open("device_list.txt") as file:
    for sw in file:
        sw_list.append(sw.rstrip('\n'))
pool.map(get_info, sw_list)

redis_db.delete("arp_table")
redis_db.rename("arp_table_new", "arp_table")
redis_db.delete("fdb")
redis_db.rename("fdb_new", "fdb")

print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
