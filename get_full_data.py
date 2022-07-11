from cgi import test
import requests
import time
import sys
import os
import getopt
import datetime
import json # only used in raw data

# GLOBALS
FUSO_BRASIL = 10800 # precisa tirar a diferenca do gmtime
SITE = "http://monipe-central.rnp.br"
BASE = SITE+"/esmond/perfsonar/archive"
SEP = ";"
#pops_id = {}
services = {}
dns_servers = {}

# Load services and dns_servers from file
def load_dict(_dict, filename):
    with open(filename, "r") as f:
        for line in f:
            items = line.strip().split(";")
            
            if len(items) < 2:
                print("Error loading file " + filename)
                sys.exit(1)
            
            val = items[-1]
            for key in items[:-1]:
                _dict[key] = val

def create_folders(path):
    full_path = ""
    for folder in path.split("/"):
        full_path += folder + "/"
        create_folder(full_path)

def create_folder(folder):
    try:
        os.mkdir(folder)
    except OSError: pass

def load_pops(filename="pop_lat_lon.txt"):
    pops = {}
    with open(filename) as f:
        for line in f:
            name, lat, lon, cod = line.strip().split(";")

            pops[name] = (lat, lon, cod)

    return pops


def div_mil(val):
    return int(val / 1000 + 0.5)

def mult_mil(val):
    return int(val * 1000 + 0.5)

def pts2mls(time):
    time = time[2:-1] # remove "PT" and "S"
    sec = float(time)

    mls = sec * 1000
    return mls
 


# eventos multivalorados: o campo val eh uma lista ou um objeto
def failures_data(item):
    return [2]


def process_dns(item):
    mls = pts2mls(item["val"]["time"])
    # Do something with item["val"]["record"]
    return [mls]

def dns_pscheduler_data(item):
    return process_dns(item)


def process_http(item):
    mls = pts2mls(item["val"]["time"])
    return [mls]

def http_pscheduler_data(item):
    return process_http(item)


def process_subinterval(subinterval):
    v_min = 100000000
    v_max = 0
    acc, n = 0, 0
    #print(hist)
    for item in subinterval["val"]:
        #val = int(item["val"] / 1000 + 0.5)
        val = item["val"]
        acc = acc + val
        n = n + 1
        if val < v_min: v_min = val
        if val > v_max: v_max = val
    
    if n == 0: return [0, 0, 0]
    #avg = int((acc/n)+0.5)
    avg = acc/n

    return [avg, v_min, v_max]

def packet_retransmits_subintervals_data(item):
    return process_subinterval(item)

def throughput_subintervals_data(item):
    return process_subinterval(item)


def process_histogram(hist):
    v_min = 100000000
    v_max = 0
    acc, n = 0, 0
    #print(hist)
    for k,v in hist["val"].items():
        #val = int(float(k) * 1000 + 0.5)
        val = float(k)
        acc = acc + val * v
        n = n + v
        if val < v_min: v_min = val
        if val > v_max: v_max = val
    
    if n == 0: return [0, 0, 0]
    #avg = int((acc/n)+0.5)
    avg = acc/n

    return [avg, v_min, v_max]

def histogram_rtt_data(item):
    return process_histogram(item)


def histogram_rtt_reverse_data(item):
    return process_histogram(item)


def histogram_owdelay_data(item):
    return process_histogram(item)


def histogram_ttl_data(item):
    return process_histogram(item)


def histogram_ttl_reverse_data(item):
    return process_histogram(item)


def process_traceroute(vet):
    v_min = 100000000
    v_max = 0
    acc, n = 0, 0
    #print(hist)
    for item in vet["val"]:
        #val = int(item["val"] / 1000 + 0.5)
        val = item.get("rtt", 0.0)
        acc = acc + val
        n = n + 1
        if val < v_min: v_min = val
        if val > v_max: v_max = val
    
    if n == 0: return [0, 0, 0, 0, 0]
    #avg = int((acc/n)+0.5)
    avg = acc/n

    return [avg, v_min, v_max, n/1000, acc] # media rtt, min_rtt, max_rtt, max_ttl, acc_rtt

def packet_trace_data(item):
    return process_traceroute(item)


def pscheduler_run_href_data(item):
    return "2"


# eventos nao multivalorados
def packet_retransmits_data(item):
    return [item["val"]]


def packet_count_lost_bidir_data(item):
    return [item["val"]]


def packet_count_sent_data(item):
    return [item["val"]]


def packet_duplicates_bidir_data(item):
    return [item["val"]]


def packet_loss_rate_bidir_data(item):
    return [item["val"]]


def packet_reorders_bidir_data(item):
    return [item["val"]]

def packet_count_lost_data(item):
    return [item["val"]]


def packet_duplicates_data(item):
    return [item["val"]]


def packet_loss_rate_data(item):
    return [item["val"]]


def packet_reorders_data(item):
    return [item["val"]]


def time_error_estimates_data(item):
    return [item["val"]]


def path_mtu_data(item):
    return [item["val"]]


def throughput_data(item):
    #val = str(item["val"]) # bit/s
    #val2 = str(int(item["val"]/1000))

    #return val + SEP + val2
    return [item["val"]/1000]


def get_raw_data(path, lat, lon, src_cod, dst_cod, data, data_function_codes):
    f = None
    filename = None
    #buffer = "" # data of the same day
    buffer = [] # data of the same day
    # data_function = data_function_codes[0]
    # codes = data_function_codes[1]
    # convert_function = data_function_codes[2]
    for item in data:
        date = str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(item["ts"] - FUSO_BRASIL)))
        item["ts"] = date # formated date


        new_filename = date.split(" ")[0].replace("-", "")

        if new_filename != filename:
            if f is not None:
                #print(buffer[:-2], file=f) # print buffer without the last ","
                #print("]", file=f)
                json.dump(buffer, f, indent=2)
                f.close()
                #buffer = ""
                buffer = []

            filename = new_filename
            f = open(path + "/" + filename + "_00_00.csv", "w")
            #print("[", file=f)
            # print("Gerando: " + path + "/" + filename + "_00_00.csv")
        
        #buffer += "\t" + str(item).replace("'", "\"") + ",\n"
        buffer.append(item)

    
    if not f.closed:
        # print(buffer[:-2], file=f) # print buffer without the last ","
        # print("]", file=f)
        json.dump(buffer, f, indent=2)
        f.close()


def get_data(path, lat, lon, src_cod, dst_cod, data, data_function_codes):
    f = None
    filename = None
    data_function = data_function_codes[0]
    codes = data_function_codes[1]
    convert_function = data_function_codes[2]
    for item in data:
        date = str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(item["ts"] - FUSO_BRASIL)))

        new_filename = date.split(" ")[0].replace("-", "")

        if new_filename != filename:
            if f is not None: f.close()
            filename = new_filename
            f = open(path + "/" + filename + "_00_00.csv", "w")
            # print("Gerando: " + path + "/" + filename + "_00_00.csv")

        line_prefix = date + SEP + lat + SEP + lon + SEP
        line_sufix = SEP + src_cod + SEP + dst_cod
        results = data_function(item)

        if codes is not None:
            if len(codes) != len(results):
                print("Fatal Erro 249")
                return

            for i in range(len(codes)):
                v = convert_function(results[i])
                code = codes[i]
                line = line_prefix + str(v) + line_sufix + SEP + str(code)

                print(line, file=f)
        else:
            if len(results) != 1:
                print("Fatal Erro 250")
                return
            
            v = convert_function(results[0])
            line = line_prefix + str(v) + line_sufix
            print(line, file=f)


    if not f.closed:
        f.close()

def build_url(src, dst, interface, test_id, time_start):
    source = "monipe-"+src+"-"+interface+".rnp.br"
    str_time_start = "time-start="+str(time_start)

    if test_id == "pscheduler-test-type=dns" or test_id == "pscheduler-test-type=http":
        url = BASE + "/" + "?measurement-agent="+source+"&"+test_id+"&"+str_time_start
    else:
        destination = "monipe-"+dst+"-"+interface+".rnp.br"

        url = BASE + "/" + "?source="+source+"&destination="+destination+"&"+test_id+"&"+str_time_start

    return url


def get_metadata_keys_info(data, metadata_keys:dict):
    for obj in data:
        metadata_keys[obj["metadata-key"]] = {}
        metadata_keys[obj["metadata-key"]]["last_update"] = None
        metadata_keys[obj["metadata-key"]]["events_base_uri"] = []
        metadata_keys[obj["metadata-key"]]["events_summaries_uri"] = []
        
        if "pscheduler-http-url" in obj: # http
            metadata_keys[obj["metadata-key"]]["http_dst"] = obj["pscheduler-http-url"]
        
        elif ("pscheduler-dns-query" in obj) and ("pscheduler-dns-nameserver" in obj): # dns
            metadata_keys[obj["metadata-key"]]["dns_query"] = obj["pscheduler-dns-query"]
            metadata_keys[obj["metadata-key"]]["dns_dst"] = obj["pscheduler-dns-nameserver"]

        for event in obj["event-types"]:
            if metadata_keys[obj["metadata-key"]]["last_update"] is None:
                metadata_keys[obj["metadata-key"]]["last_update"] = event["time-updated"]
            elif event["time-updated"] is not None and event["time-updated"] > metadata_keys[obj["metadata-key"]]["last_update"]:
                metadata_keys[obj["metadata-key"]]["last_update"] = event["time-updated"]

            metadata_keys[obj["metadata-key"]]["events_base_uri"].append(event["base-uri"])

            n = len(event["summaries"])
            if n > 0:
                for i in range(n):
                    metadata_keys[obj["metadata-key"]]["events_summaries_uri"].append(event["summaries"][i]["uri"])


def response_check(url, response_code):
    if response_code != 200:
        print("### Response Error ###")
        print("URL:", url)
        print("Status Code:", response_code)
        print("######################")
        return True

    return False


def get_events_data(metadata_keys, lat, lon, src, dst, src_cod, dst_cod, path, event_type, test_type, time_start, time_end, data_file_func=get_data):
    # events = {"event_name": (data_function, codes list, aux_function)}
    events = {
    "banda_bbr.failures": (failures_data, [70], int),
    "banda_bbr.packet-retransmits": (packet_retransmits_data, [71], int),
    "banda_bbr.packet-retransmits-subintervals": (packet_retransmits_subintervals_data, [72, 73, 74], int),
    "banda_bbr.throughput": (throughput_data, [77], int),
    "banda_bbr.throughput-subintervals": (throughput_subintervals_data, [78, 79, 80], div_mil),

    "banda_cubic.failures": (failures_data, [100], int),
    "banda_cubic.packet-retransmits": (packet_retransmits_data, [101], int),
    "banda_cubic.packet-retransmits-subintervals": (packet_retransmits_subintervals_data, [102, 103, 104], int),
    "banda_cubic.throughput": (throughput_data, [107], int),
    "banda_cubic.throughput-subintervals": (throughput_subintervals_data, [108, 109, 110], div_mil),

    "atraso_bidir.failures": (failures_data, [10], int),
    "atraso_bidir.histogram-rtt": (histogram_rtt_data, [11, 12, 13], mult_mil),
    "atraso_bidir.histogram-ttl-reverse": (histogram_rtt_reverse_data, [16, 17, 18], int),
    "atraso_bidir.packet-count-lost-bidir": (packet_count_lost_bidir_data, [21], int),
    "atraso_bidir.packet-count-sent": (packet_count_sent_data, [22], int),
    "atraso_bidir.packet-duplicates-bidir": (packet_duplicates_bidir_data, [23], int),
    "atraso_bidir.packet-loss-rate-bidir": (packet_loss_rate_bidir_data, [24], int),
    "atraso_bidir.packet-reorders-bidir": (packet_reorders_bidir_data, [25], int),

    "atraso_unidir.failures": (failures_data, [40], int),
    "atraso_unidir.histogram-owdelay": (histogram_owdelay_data, [41, 42, 43], mult_mil),
    "atraso_unidir.histogram-ttl": (histogram_ttl_data, [46, 47, 48], int),
    "atraso_unidir.packet-count-lost": (packet_count_lost_data, [51], int),
    "atraso_unidir.packet-count-sent": (packet_count_sent_data, [52], int),
    "atraso_unidir.packet-duplicates": (packet_duplicates_data, [53], int),
    "atraso_unidir.packet-loss-rate": (packet_loss_rate_data, [54], mult_mil), # perdidos/enviados
    "atraso_unidir.packet-reorders": (packet_reorders_data, [55], int),

    "traceroute.failures": (failures_data, [130], int),
    "traceroute.packet-trace": (packet_trace_data, [131, 132, 133, 134, 135], mult_mil),
    "dns.pscheduler-raw": (dns_pscheduler_data, None, int),
    #"dns.pscheduler-run-href": (, [151], None),
    "http.pscheduler-raw": (http_pscheduler_data, None, int),
    #"http.pscheduler-run-href": (, [151], None),
    # "traceroute.time-error-estimates": (time_error_estimates_data, [], func),
    # "traceroute.path-mtu": (path_mtu_data, [], func),
    
    # "pscheduler-run-href": pscheduler_run_href_data
    }

    str_time_start = "?time-start=" + str(time_start)
    str_time_end = ""
    if time_end is not None: str_time_end = "&time-end=" + str(time_end)
    str_limit = "&limit=" + str(1000000000)

    for metadata_key in metadata_keys:       
        dns_query = None
        # site accessed in http and resolved by dns
        if "http_dst" in metadata_keys[metadata_key]:
            dst = metadata_keys[metadata_key]["http_dst"]
            
            pos = dst.find(":")
            if pos != -1: dst = dst[pos+3:]
            if dst[-1] == "/": dst = dst[:-1]
            
            dst = dst.replace("/", "_") # must replace "/" to be able to create folder

            if dst in services:
                dst_cod = services[dst]
            else:
                print("Unknow service: {}".format(dst))
                continue
        elif "dns_dst" in metadata_keys[metadata_key] and "dns_query" in metadata_keys[metadata_key]:
            # DNS DST (DNS Server)
            dst = metadata_keys[metadata_key]["dns_dst"]
            if dst in dns_servers:
                dst_cod = dns_servers[dst]
            else:
                print("Unkown DNS Server: {}".format(dst))
                continue
            
            
            
            # DNS Query (Service)
            dns_query = metadata_keys[metadata_key]["dns_query"]

            pos = dns_query.find(":")
            if pos != -1: dns_query = dns_query[pos+3:]
            if dns_query[-1] == "/": dns_query = dns_query[:-1]
            
            dns_query = dns_query.replace("/", "_") # must replace "/" to be able to create folder

            

            if dns_query in services:
                dst_cod = "{};{}".format(dst_cod, services[dns_query])
            else:
                print("Unknow service: {}".format(dns_query))
                continue

        #print("DNS Query: {}, DST: {}, DST CODE: {}".format(dns_query, dst, dst_cod))
        
        for event in metadata_keys[metadata_key]["events_base_uri"]:
            if event_type is not None and event_type+"/" not in event: continue

            url = SITE+event+str_time_start+str_time_end+str_limit
            response = requests.get(url) # pega todos os dados daquele evento
            if response_check(url, response.status_code): continue
            
            result2 = response.json()
            if len(result2) == 0: continue # o evento nao possui dados para aquele periodo


            domain = test_type
            event_name = event.split("/")[-2]
            if dns_query is None:
                file_path = path + "/" + event_name.replace("-", "_") + "/" + src + "/" + dst
            else:
                file_path = path + "/" + event_name.replace("-", "_") + "/" + src + "/" + dst + "/" + dns_query


            key = domain + "." + event_name
            if key not in events:
                print("\""+key+"\"")
                continue

            create_folders(file_path)
            data_file_func(file_path, lat, lon, src_cod, dst_cod, result2, events[key])




def main(interface, test_id, path, event_type, test_type, time_start, time_end, raw_data):

    hash_mk = {}
    pops0 = ["rj", "sp"] # test
    pops = ["ac","al","am","ap","ba","ce","df","es","go","ma","mg","ms","mt","pa","pb","pe","pi","pr","rj","rn","ro","rr","rs","sc","se","sp","to"]
    #pops = pops0
    
    if test_id != "pscheduler-test-type=dns" and test_id != "pscheduler-test-type=http":
        for src in pops:
            for dst in pops:
                if src == dst: continue
                
                key = src + dst
                url = build_url(src, dst, interface, test_id, time_start)
                #print("URL:", url, "\n")
                response = requests.get(url)
                if response_check(url, response.status_code): return
                result1 = response.json()

                metadata_keys = {}

                get_metadata_keys_info(result1, metadata_keys)
                hash_mk[key] = metadata_keys
            
        if len(metadata_keys) == 0: return

        pops_id = load_pops()
        for src in pops:
            for dst in pops:
                if src == dst: continue
                #print(">>>>>>>>>>", src, "->", dst, "("+test_type+")")
            
                lat, lon, src_cod = pops_id[src]
                dst_cod = pops_id[dst][2]

                if not raw_data:
                    get_events_data(hash_mk[src+dst], lat, lon, src, dst, src_cod, dst_cod, path, event_type, test_type, time_start, time_end)
                else:
                    get_events_data(hash_mk[src+dst], lat, lon, src, dst, src_cod, dst_cod, path, event_type, test_type, time_start, time_end, data_file_func=get_raw_data)

                print("<<<<<<<<<<", src, "->", dst, "("+test_type+")")
    
    else:
        dst = None # must get dst from object returned in step 1 of query
        for src in pops:
            key = src
            url = build_url(src, None, interface, test_id, time_start)
            response = requests.get(url)
            if response_check(url, response.status_code): return
            result = response.json()
            
            metadata_keys = {}

            get_metadata_keys_info(result, metadata_keys)
            hash_mk[key] = metadata_keys
            
        pops_id = load_pops()
        for src in pops:
            lat, lon, src_cod = pops_id[src]
            dst_cod = None

            if not raw_data:
                get_events_data(hash_mk[src], lat, lon, src, dst, src_cod, dst_cod, path, event_type, test_type, time_start, time_end)
            else:
                get_events_data(hash_mk[src], lat, lon, src, dst, src_cod, dst_cod, path, event_type, test_type, time_start, time_end, data_file_func=get_raw_data)

            print("<<<<<<<<<<", src, "->", dst, "("+test_type+")")


# YYYYMMDD to epoch
# end=True vai ate o final daquela data
def date_to_epoch(date, end=False):
    if date is None: return

    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:])

    if not end: return int(datetime.datetime(year, month, day, 0, 0, 0).timestamp())

    #return int(datetime.datetime(year, month, day+1, 0, 0, 0).timestamp()) -1
    return int(datetime.datetime(year, month, day, hour=23, minute=59, second=59).timestamp())

if __name__ == "__main__":
    def help():
        print("###### TIP ######")
        print("Forneca os parametros: source, destination, test-type, event-type(opcional), time-end(opcional), raw-data(opcional).")
        print("\ttime-start: Data a partir da qual os dados serao pegos, deve estar no formato YYYYMMDD")
        print("\ttest-type: deve ser uma das seguintes opcoes-> atraso_bidir, atraso_unidir, traceroute, banda_bbr, banda_cubic.")
        print("\tevent-type: deve ser um evento que aquele teste possui.")
        print("\ttime-end: date ate a qual os dados serao pegos(inclusivo). 20210626 pegara dados ate 26/06/2021 23:59:59")
        print("------------------------------------------------------------------------------------------------------------------------")
        print("Ex1: python3 get_full_data.py --time-start 20210601 --test-type atraso_bidir")
        print("Ex2: python3 get_full_data.py --time-start 20210601 --test-type atraso_bidir --event-type histogram-rtt")
        print("Ex3: python3 get_full_data.py --time-start 20210601 --time-end 20210905 --test-type atraso_bidir")
        print("Ex4: python3 get_full_data.py --time-start 20210601 --time-end 20210905 --test-type atraso_bidir --event-type histogram-rtt")
        print("###### END ######")
        sys.exit(1)

    date_start = None
    test_type = None
    event_type = None
    date_end = None
    raw_data = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],None,["time-start=","time-end=","test-type=","event-type=","raw-data"])
    except getopt.GetoptError as err:
        print(err)
        help()
        
    for opt, arg in opts:
        if opt in ("--time-start"):
            date_start = arg
        elif opt in ("--time-end"):
            date_end = arg
        elif opt in ("--test-type"):
            test_type = arg
        elif opt in ("--event-type"):
            event_type = arg
        elif opt in ("--raw-data"):
            raw_data = True


    if not (date_start and test_type):
        print("not date_start and test_type")
        help()

    time_start = date_to_epoch(date_start)
    time_end = date_to_epoch(date_end, end=True) # pega epoch ate date_end 23:59:59

    # print("time-start:", time_start)
    # print("time-end:", time_end)
    # print("test-type:", test_type)
    # print("event-type:", event_type)


    test_types = {
        "atraso_bidir": ("atraso_bidir", "event-type=histogram-rtt"), # test name, test id(parametro que identifica o teste)
        "atraso_unidir": ("atraso_unidir", "event-type=histogram-owdelay"),
        "traceroute":("traceroute", "event-type=packet-trace"),
        "banda_bbr": ("banda_bbr", "bw-target-bandwidth=10000000000"),
        "banda_cubic": ("banda_cubic", "bw-target-bandwidth=9999999999"),
        "dns": ("dns", "pscheduler-test-type=dns"),
        "http": ("http", "pscheduler-test-type=http")
        }

    if test_type not in test_types:
        print("ERRO: " + test_type + " não eh um teste valido!")
        help()

    interfaces = {
        "atraso_bidir": "atraso",
        "atraso_unidir": "atraso",
        "traceroute":"atraso",
        "banda_bbr": "banda",
        "banda_cubic": "banda",
        "dns": "atraso",
        "http": "atraso"
        }

    path, test_id = test_types[test_type]
    interface = interfaces[test_type]

    load_dict(services, "services.txt")
    load_dict(dns_servers, "dns_servers.txt")

    main(interface, test_id, path, event_type, test_type, time_start, time_end, raw_data)
