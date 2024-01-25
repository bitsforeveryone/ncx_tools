import redis
import ipaddress

def ip_range_parser(ip_range_string):
    #supported formats:
    #192.168.*.3
    #192.168.1.*
    #192.168.1-225.*
    octets = ip_range_string.split(".")
    if len(octets) != 4:
        return None
    if octets[0] == "*":
        octets[0] = "0-255"
    if octets[1] == "*":
        octets[1] = "0-255"
    if octets[2] == "*":
        octets[2] = "0-255"
    if octets[3] == "*":
        octets[3] = "0-255"
    octets_possible = []
    for octet in octets:
        if "-" in octet:
            octet_range = octet.split("-")
            if len(octet_range) != 2:
                return None
            octets_possible.append(list(range(int(octet_range[0]), int(octet_range[1]) + 1)))
        else:
            octets_possible.append([int(octet)])
    ips = []
    if len(octets_possible[0]) * len(octets_possible[1]) * len(octets_possible[2]) * len(octets_possible[3]) > 10000:
        print("Too many IPs to scan, please narrow your range")
        return None
    for octet0 in octets_possible[0]:
        for octet1 in octets_possible[1]:
            for octet2 in octets_possible[2]:
                for octet3 in octets_possible[3]:
                    ips.append(ipaddress.ip_address(str(octet0) + "." + str(octet1) + "." + str(octet2) + "." + str(octet3)))
    return ips

def get_connection():
    #read the redis password from ../redis_password.txt
    with open(".redis_env", "r") as f:
        redis_password = f.readline().split("REDISCLI_AUTH=")[1].strip()
        redis_host = f.readline().split("HOST_IP=")[1].strip()
        redis_port = f.readline().split("REDIS_PORT=")[1].strip()
        return redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
    return None

def get_hosts():
    r = get_connection()
    if r:
        return r.smembers("hosts")
    return None


def get_hosts_ip_only():
    r = get_connection()
    if r:
        hosts = r.smembers("hosts")
        hosts_dups =  [host.decode("utf-8").split("@")[1] for host in hosts]
        #remove duplicates
        hosts = list(dict.fromkeys(hosts_dups))
        return hosts
    return None

def remove_host(host):
    r = get_connection()
    if r:
        return r.srem("hosts", host)
    return None

def add_target(target : str):
    #make sure the target is a valid IP address and is in the scope
    if ip_range_parser(target):
        r = get_connection()
        if r:
            return r.sadd("targets", target)
    return None
        
def remove_target(target : str):
    r = get_connection()
    if r:
        return r.srem("targets", target)
    return None

def get_targets():
    r = get_connection()
    if r:
        return r.smembers("targets")
    return None

def is_blacklisted(ip : ipaddress.IPv4Address):
    r = get_connection()
    if r:
        if r.sismember("blacklisted_ips", str(ip)):
            return True
    return False

def is_in_scope(ip : ipaddress.IPv4Address):
    r = get_connection()
    if r:
        targets = r.smembers("targets")
        for target in targets:
            if ip in ip_range_parser(target.decode("utf-8")) and not is_blacklisted(ip):
                return True
    return False

def get_blacklisted():
    r = get_connection()
    if r:
        return r.smembers("blacklisted_ips")
    return None

def add_blacklisted_ip(ip : ipaddress.IPv4Address):
    r = get_connection()
    if r:
        return r.sadd("blacklisted_ips", str(ip))
    return None

def remove_blacklisted_ip(ip : ipaddress.IPv4Address):
    r = get_connection()
    if r:
        return r.srem("blacklisted_ips", str(ip))
    return None

    
    

def add_host(host_ssh_string):
    r = get_connection()
    if r:
        return r.sadd("hosts", host_ssh_string)
    return None

