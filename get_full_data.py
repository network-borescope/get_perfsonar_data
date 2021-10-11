import requests
import time
import sys
import os

# GLOBALS
FUSO_BRASIL = 10800 # precisa tirar a diferenca do gmtime
SITE = "http://monipe-central.rnp.br"
BASE = SITE+"/esmond/perfsonar/archive"
SEP = ";"

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
            name, lat, lon = line.strip().split(";")

            pops[name] = (lat, lon)

    return pops

# eventos multivalorados: o campo val eh uma lista ou um objeto
def failures_data(item):
    return "2"


def packet_retransmits_subintervals_data(item):
    return "2"


def throughput_subintervals_data(item):
    return "2"


def histogram_rtt_data(item):
    return "2"


def histogram_rtt_reverse_data(item):
    return "2"


def histogram_owdelay_data(item):
    return "2"


def histogram_ttl_data(item):
    return "2"


def histogram_ttl_reverse_data(item):
    return "2"


def packet_trace_data(item):
    return "2"


def pscheduler_run_href_data(item):
    return "2"


# eventos nao multivalorados
def packet_retransmits_data(item):
    return str(item["val"])


def packet_count_lost_bidir_data(item):
    return str(item["val"])


def packet_count_sent_data(item):
    return str(item["val"])


def packet_duplicates_bidir_data(item):
    return str(item["val"])


def packet_loss_rate_bidir_data(item):
    return str(item["val"])


def packet_reorders_bidir_data(item):
    return str(item["val"])

def packet_count_lost_data(item):
    return str(item["val"])


def packet_duplicates_data(item):
    return str(item["val"])


def packet_loss_rate_data(item):
    return str(item["val"])


def packet_reorders_data(item):
    return str(item["val"])


def time_error_estimates_data(item):
    return str(item["val"])


def path_mtu_data(item):
    return str(item["val"])


def throughput_data(item):
    val = str(item["val"])
    val2 = str(int(item["val"]/1000))

    return val + SEP + val2


def get_data(path, lat, lon, src, dst, data, data_function):
    f = None
    filename = None

    for item in data:
        data = str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(item["ts"] - FUSO_BRASIL)))

        new_filename = data.split(" ")[0].replace("-", "")

        if new_filename != filename:
            if f is not None: f.close()
            filename = new_filename
            f = open(path + "/" + filename + "_00_00.csv", "w")
            print("Gerando: " + path + "/" + filename + "_00_00.csv")

        line = data + SEP + lat + SEP + lon + SEP
        line += data_function(item) + SEP + src + SEP + dst

        print(line, file=f)

    if not f.closed:
        f.close()

def build_url(src, dst, interface, test_id):
    source = "monipe-"+src+"-"+interface+".rnp.br"
    destination = "monipe-"+dst+"-"+interface+".rnp.br"

    url = BASE+ "/" + "?source="+source+"&destination="+destination+"&"+test_id

    return url


def get_metadata_keys_info(data, metadata_keys:dict):
    for obj in data:
        metadata_keys[obj["metadata-key"]] = {}
        metadata_keys[obj["metadata-key"]]["events_base_uri"] = []
        metadata_keys[obj["metadata-key"]]["events_summaries_uri"] = []

        for event in obj["event-types"]:
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

def get_events_data(metadata_keys, lat, lon, path, event_type):
    # events = {"event_name": function}
    events = {
    "failures": failures_data, "packet-retransmits": packet_retransmits_data,
    "packet-retransmits-subintervals": packet_retransmits_subintervals_data,
    "throughput": throughput_data, "throughput-subintervals": throughput_subintervals_data,
    "histogram-rtt": histogram_rtt_data, "histogram-rtt-reverse": histogram_rtt_reverse_data,
    "packet-count-lost-bidir": packet_count_lost_bidir_data, "packet-count-sent": packet_count_sent_data,
    "packet-duplicates-bidir": packet_duplicates_bidir_data, "packet-loss-rate-bidir": packet_loss_rate_bidir_data,
    "packet-reorders-bidir": packet_reorders_bidir_data, "histogram-owdelay": histogram_owdelay_data,
    "histogram-ttl": histogram_ttl_data, "histogram-ttl-reverse": histogram_ttl_reverse_data,
    "packet-count-lost": packet_count_lost_data, "packet-count-sent": packet_count_sent_data, 
    "packet-duplicates": packet_duplicates_data, "packet-loss-rate": packet_loss_rate_data, 
    "packet-reorders": packet_reorders_data, "packet-trace": packet_trace_data,
    "time-error-estimates": time_error_estimates_data, "path-mtu": path_mtu_data, 
    "pscheduler-run-href": pscheduler_run_href_data
    }
    
    for metadata_key in metadata_keys:
        for event in metadata_keys[metadata_key]["events_base_uri"]:
            if event_type is not None and event_type+"/" not in event: continue

            response = requests.get(BASE+event) # pega todos os dados daquele evento
            if response_check(BASE+event, response.status_code): continue
            
            result2 = response.json()

            event_name = event.split("/")[-2]
            file_path = path + "/" + event_name + "/" + src + "/" + dst
            #create_folder(file_path)
            create_folders(file_path)


            if len(result2) == 0: continue # o evento nao possui dados para aquele periodo

            if event_name not in events:
                print(event_name)
                continue

            get_data(file_path, lat, lon, src, dst, result2, events[event_name])




def main(src, dst, interface, test_id, path, event_type):
    pops = load_pops()
    lat, lon = pops[src]

    url = build_url(src, dst, interface, test_id)
    print("URL:", url, "\n")
    response = requests.get(url)
    if response_check(url, response.status_code): return
    result1 = response.json()

    metadata_keys = {}

    get_metadata_keys_info(result1, metadata_keys)

    count = 0
    print("BEGIN METADATA KEYS")
    for metadata_key in metadata_keys:
        count += 1
        print(str(count) + ") " + metadata_key)
    print("END METADATA KEYS\n")

    get_events_data(metadata_keys, lat, lon, path, event_type)




if __name__ == "__main__":
    def help():
        print("###### TIP ######")
        print("Forneca os parametros: source, destination, test-type, event-type(opcional).")
        print("\tsource: sigla estado de origem.")
        print("\tdestination: sigla estado de destino.")
        print("\ttest-type: deve ser uma das seguintes opcoes-> atraso_bi, atraso_uni, traceroute, banda_bbr, banda_cubic.")
        print("\tevent-type: deve ser um evento que aquele teste possui.\n")
        print("Ex1: python3 get_full_data.py df sp banda_bbr")
        print("Ex2: python3 get_full_data.py df sp banda_bbr throughput")
        print("###### END ######")

    args = sys.argv[1:] # o primeiro arg eh o nome do programa
    event_type = None
    if len(args) < 3:
        help()
        sys.exit(1)
    elif len(args) == 3:
        src, dst, test_type = args
    elif len(args) == 4:
        src, dst, test_type, event_type = args

    if src == dst:
        print("Erro: A origem e o destino devem ser diferentes.")
        help()
        sys.exit(1)

    test_types = {
        "atraso_bi": ("Atraso e Perda de pacotes", "event-type=histogram-rtt"), # test name, test id(parametro que identifica o teste)
        "atraso_uni": ("Atraso unidirecional", "event-type=histogram-owdelay"),
        "traceroute":("Traceroute", "event-type=packet-trace"),
        "banda_bbr": ("Banda(BBR)", "bw-target-bandwidth=10000000000"),
        "banda_cubic": ("Banda(CUBIC)", "bw-target-bandwidth=9999999999")
        }

    if test_type not in test_types:
        print("ERRO: " + test_type + " não eh um teste valido!")
        help()
        sys.exit(1)

    interfaces = {
        "atraso_bi": "atraso",
        "atraso_uni": "atraso",
        "traceroute":"atraso",
        "banda_bbr": "banda",
        "banda_cubic": "banda"
        }

    path, test_id = test_types[test_type]
    #path += "/" + src + "/" + dst
    interface = interfaces[test_type]
    #create_folders(path)
    main(src, dst, interface, test_id, path, event_type)
