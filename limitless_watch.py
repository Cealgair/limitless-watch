#####################
#  LIMITLESS WATCH  #
# (c) 2026 cealgair #
#####################

# see README.md for instructions

import requests
import xml.etree.ElementTree as ET
import re
import json
from time import sleep, gmtime, strftime
import os
from copy import deepcopy

VERBOSITY = False

def print_log(text):
    log_string = f"{strftime("%Y-%m-%d %H:%M:%S", gmtime())} UTC - {text}"
    f = open("logs.txt", "a")
    f.write(log_string+"\n")
    f.close()
    if VERBOSITY:
        print(log_string)
    return

try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    if parser.parse_args().verbose:
        VERBOSITY = True
except:
    print_log("Error: argparse not available, verbosity might not work")

try:
    settings = json.load(open("config.json","r"))
    assert len(settings)>0
except:
    VERBOSITY = True
    print_log("Fatal: config.json is either missing or malformed. See README.md")
    assert False

sleep_hours = 24 # hours
if "sleep_hours" in settings[0]:
    sleep_hours=settings[0]["sleep_hours"]

def sanitize_xml(data):
    data = re.sub(r'>[ \n\t]*([^<>]+?)[ \n\t]*<',r'><text>\1</text><',data,flags=re.M)
    data = re.sub(r'<text>[ \n\t]?</text>','',data,flags=re.M)
    root = ET.fromstring(data)
    return root
    

def sanitize_table(data,css_class):
    table = '<table>'+data.split('<table class="'+css_class+'">')[1].split('</table>')[0]+'</table>'
    table = re.sub(r'colspan=([0-9]+)',r'colspan="\1"',table)
    table = re.sub(r'(<img .*?)>',r'\1/>',table)
    table = re.sub(r'(href="[^"]*?)\?.*?"',r'\1"',table)
    return sanitize_xml(table)

def parse_pokemon_set_line(line):
    aname = line[0][0]
    url = aname.attrib["href"]
    name = aname[-2].text # counting from the end because BS does not have image
    code = aname[-1][0].text
    adate = line[1][0]
    possibledate = [c for c in adate]
    if len(possibledate)==0:
        date=None
    else:
        date = possibledate[0].text
    cards = line[2][0][0].text
    return {
        "name": name,
        "code": code,
        "cards": int(cards),
        "date": date,
        "url": url
    }

def parse_onepiece_product_set_line(line):
    acode = line[0][0]
    url = acode.attrib["href"]
    name = line[1][0][0].text
    code = acode[0].text
    adate = line[2][0]
    possibledate = [c for c in adate]
    if len(possibledate)==0:
        date=None
    else:
        date = possibledate[0].text
    cards = line[3][0][0].text
    return {
        "name": name,
        "code": code,
        "cards": int(cards),
        "date": date,
        "url": url
    }

def parse_onepiece_promo_set_line(line):
    aname = line[0][0]
    url = aname.attrib["href"]
    name = aname[0].text
    adate = line[1][0]
    possibledate = [c for c in adate]
    if len(possibledate)==0:
        date=None
    else:
        date = possibledate[0].text
    cards = line[2][0][0].text
    return {
        "name": name,
        "code": None,
        "cards": int(cards),
        "date": date,
        "url": url
    }

def get_bandai_sets(which):
    ids = ["riftbound","lorcana","swu","bandai/dcg","bandai/fw","bandai/dbs","bandai/bss","bandai/gundam"]
    assert which in ids
    domain_name="https://limitlesstcg.com"
    url=f"{domain_name}/{which}"
    response = requests.get(url)
    data="<ul>"+response.text.split("<ul>")[1].split("</ul>")[0]+"</ul>"
    root = sanitize_xml(data)
    lines = [c for c in root if c.tag=='li']
    
    
    sets = []
    for line in lines:
        set = {}
        set["name"]=None
        set["series"]=None
        set["date"]=None
        set["code"]=line[0][0].text
        set["url"]=domain_name+line[0].attrib["href"]
        set["cards"]=int(line[0][1][0].text[1:].split(" ")[0])
        sets.append(set)
    return sets

def get_sets(which):
    urls = {
        "international": "https://limitlesstcg.com/cards",
        "japanese": "https://limitlesstcg.com/cards/jp",
        "pocket": "https://pocket.limitlesstcg.com/cards",
        "onepiece products": "https://onepiece.limitlesstcg.com/cards",
        "onepiece promos": "https://onepiece.limitlesstcg.com/cards/promos"
    }
    if which not in urls:
        return get_bandai_sets(which)
    url=urls[which]
    response = requests.get(url)
    root = sanitize_table(response.text,"data-table sets-table striped")
    lines = [[td for td in c if td.tag=="td" or td.tag=="th"] for c in root if c.tag=='tr']
    heading = lines[0]
    
    # to do: add checks on the heading, to ensure the format has not changed or anything
    
    domain_name = url.split('limitlesstcg.com')[0]+'limitlesstcg.com'
    
    sets = []
    current_subheading=None
    for line in lines[1:]:
        if len(line)==1:
            # assume it's a subheading
            current_subheading = line[0][0].text
        else:
            # assume it's a set
            if which in ["international","japanese","pocket"]:
                set = parse_pokemon_set_line(line)
            elif which == "onepiece products":
                set = parse_onepiece_product_set_line(line)
            elif which == "onepiece promos":
                set = parse_onepiece_promo_set_line(line)
            else:
                assert False
            set["series"]=current_subheading
            if set["url"][0]=='/':
                set["url"]=domain_name+set["url"]
            else:
                # to do
                assert False
            sets.append(set)
    return sets

def get_tournaments(which):
    urls = {
        "pokemon": "https://limitlesstcg.com/tournaments",
        "vgc": "https://limitlessvgc.com/tournaments",
        "onepiece": "https://onepiece.limitlesstcg.com/tournaments"
    }
    assert which in urls
    url=urls[which]
    response = requests.get(url)
    root = sanitize_table(response.text,"data-table striped completed-tournaments")
    lines = [c for c in root if c.tag=='tr']
    heading = lines[0]
    
    # to do: add sanity checks on the heading, to ensure the format has not changed or anything
    
    domain_name = url.split('.com/')[0]+'.com/'
    
    tournaments = []
    for line in lines[1:]:
        # assume it's a tournament
        tournament={
            "name": line.attrib["data-name"],
            "date": line.attrib["data-date"],
            "format": line.attrib["data-format"],
            "url": line[2][0].attrib["href"]
        }
        if tournament["url"][0]=='/':
            tournament["url"]=domain_name+tournament["url"][1:]
        else:
            # to do
            assert False
        
        tournaments.append(tournament)
    return tournaments

def get_ptcg_tournament_format(tournament):
    response = requests.get(tournament["url"])
    format = response.text.split('<a href="/decks/?time=all&format=')[1].split('"')[0]
    tournament["format"] += f" ({format})"
    return # we are modifying a dict, no need to return anything

def changelog_sets(old,new):
    changelog = {
        "new sets" : [],
        "enlarged sets": [],
        "changed codes": []
    }
    new_data = {s["code"]:s for s in new}
    
    def tuplify(s):
        return (s["date"],s["name"],s["code"],s["cards"])
    old_tuples = {tuplify(s) for s in old}
    new_tuples = {tuplify(s) for s in new}
    
    # remove everything that did not change at all
    inters = old_tuples.intersection(new_tuples)
    for t in inters:
        old_tuples.remove(t)
        new_tuples.remove(t)
        
    # look for changed set codes
    for key in [[0,1,3],[0,1],[0,3],[0]]:
        old_dict = {tuple([t[i] for i in key]) : t for t in old_tuples}
        new_dict = {tuple([t[i] for i in key]) : t for t in new_tuples}
        inters = {t for t in old_dict}.intersection({t for t in new_dict})
        for t in inters:
            if new_dict[t][2]==old_dict[t][2]:
                continue
            changelog["changed codes"].append({
                "data": new_data[new_dict[t][2]],
                "old": old_dict[t][2]
            })
            old_tuples.remove(old_dict[t])
            new_tuples.remove(new_dict[t])
    
    # from now on we assume that set codes identify sets
    old_dict = {t[2]:t for t in old_tuples}
    new_dict = {t[2]:t for t in new_tuples}
    for c in new_dict:
        if c in old_dict:
            if old_dict[c][3] < new_dict[c][3]:
                changelog["enlarged sets"].append({
                    "data": new_data[new_dict[c][2]],
                    "old": old_dict[c][3]
                })
        else:
            changelog["new sets"].append(new_data[new_dict[c][2]])
    
    return changelog

def changelog_tournaments(old,new):
    changelog = []
    new_data = {s["url"]:s for s in new}
    new_urls = {u for u in new_data}
    old_urls = {s["url"] for s in old}
    for u in new_urls:
        if u not in old_urls:
            changelog.append(new_data[u])
    return changelog

def send_message(webhook,title,url,dbname=None,description=None):
    # webhook is a dictionary, like an item of the config.json array
    embed = {"title":title,"url":url,"type":"rich","author":{"name":"Limitless"}}
    if dbname is not None:
        embed["footer"]={"text": dbname}
    if description is not None:
        embed["description"] = description
    message = {}
    if "webhook_parameters" in webhook:
        for x in ["username","avatar_url"]:
            if x in webhook["webhook_parameters"]:
                if webhook["webhook_parameters"][x] is not None:
                    message[x]=webhook["webhook_parameters"][x]
        if "color" in webhook["webhook_parameters"]:
            if webhook["webhook_parameters"]["color"] is not None:
                embed["color"]=webhook["webhook_parameters"]["color"]
    message["embeds"]=[embed]
    
    print_log(f"Sending message to {webhook["webhook_url"]}")
    print_log(f"{message}")
    print_log("")
    
    
    requests.post(webhook["webhook_url"], json = message)
    return

def set_name_and_code(s):
    if s["name"] is not None:
        if s["code"] is not None:
            return f'{s["name"]} ({s["code"]})'
        return s["name"]
    if s["code"] is not None:
        return f"Set with code {s["code"]}"
    return "A set"

def send_new_sets(webhook,changelog,dbname=None):
    if len(changelog)==0: # happens if first run
        return
    for s in changelog["new sets"]:
        title = set_name_and_code(s)
        series = ""
        if s["series"] is not None:
            series = f'in the *{s["series"]}* series '
        description = f"New set {series}is now available!"
        if s["date"] is not None:
            description += f'\n-# Release date: {s["date"]}'
            
        send_message(webhook,title,s["url"],dbname=dbname,description=description)
    for c in changelog["changed codes"]:
        send_message(webhook,set_name_and_code(c),c["data"]["url"],dbname=dbname,description=f'Set in the *{c["data"]["series"]}* series changed its code\n-# Old code: {c["old"]}')
    return

def send_new_promos(webhook,changelog,dbname=None):
    if len(changelog)==0: # happens if first run
        return
    for c in changelog["enlarged sets"]:
        send_message(webhook,set_name_and_code(c),c["data"]["url"],dbname=dbname,description=f'Set in the *{c["data"]["series"]}* series has {c["data"]["cards"]-c["old"]} new cards\n-# Set size increased from {c["old"]} to {c["data"]["cards"]}')
    return

def send_tournaments(webhook,changelog,dbname=None):
    if len(changelog)==0: # happens if first run
        return
    for t in changelog:
        send_message(webhook,f"{t["name"]}",t["url"],dbname=dbname,description=f'New tournament results\n-# Tournament date: {t["date"]}\n-# Format: {t["format"]}')
    return

#for which in ["international","japanese","pocket"]:
#    with open(f"{which}.json","w") as f:
#        json.dump(get_sets(which), f,indent=2)

#for which in ["pokemon","vgc","onepiece"]:
#    with open(f"{which}_tournaments.json","w") as f:
#        json.dump(get_tournaments(which), f,indent=2)
#assert False

filenames = {
    "sets":{
        "international": "international.json",
        "japanese": "japanese.json",
        "pocket": "pocket.json",
        "onepiece products": "onepiece_products.json",
        "onepiece promos": "onepiece_promos.json",
        "riftbound": "riftbound.json",
        "lorcana": "lorcana.json",
        "swu": "swu.json",
        "bandai/dcg": "bandai_dcg.json",
        "bandai/fw": "bandai_fw.json",
        "bandai/dbs": "bandai_dbs.json",
        "bandai/bss": "bandai_bss.json",
        "bandai/gundam": "bandai_gundam.json"
    },
    "tournaments":{
        "pokemon": "pokemon_tournaments.json",
        "vgc": "vgc_tournaments.json",
        "onepiece": "onepiece_tournaments.json"
    }
}

zero_data = {x:{y:[] for y in filenames[x]} for x in filenames}
first_run = {x:{y:False for y in filenames[x]} for x in filenames}

old_data = deepcopy(zero_data)
new_data = deepcopy(zero_data)

if not os.path.isdir("data"):
    print_log("Created data folder")
    os.makedirs("data")
for x in first_run:
    for y in first_run[x]:
        try:
            f = open("data/"+filenames[x][y],'r')
            old_data[x][y]=json.load(f)
            f.close()
        except:
            print_log(f"This is the first run for {x}/{y}")
            old_data[x][y]=[]
            first_run[x][y]=True
        else:
            print_log(f"Old data found for {x}/{y}")

while True:
    for which in first_run["sets"]:
        sleep(2) # for good measure
        try:
            new_data["sets"][which] = get_sets(which)
            print_log(f"New data found for sets/{which}")
        except:
            new_data["sets"][which] = old_data["sets"][which]
            print_log(f"Error trying to find new data for sets/{which}")
    for which in first_run["tournaments"]:
        sleep(2) # for good measure
        try:
            new_data["tournaments"][which] = get_tournaments(which)
            print_log(f"New data found for tournaments/{which}")
        except:
            new_data["tournaments"][which] = old_data["tournaments"][which]
            print_log(f"Error trying to find new data for tournaments/{which}")
    
    # compare old and new data
    changelogs = {
        "sets":{y:{} for y in filenames["sets"]},
        "tournaments":{y:[] for y in filenames["tournaments"]}
    }
    for which in new_data["sets"]:
        if first_run["sets"][which]:
            changelogs["sets"][which] = {}
            continue
        changelogs["sets"][which] = changelog_sets(old_data["sets"][which],new_data["sets"][which])
    for which in new_data["tournaments"]:
        if first_run["tournaments"][which]:
            changelogs["tournaments"][which] = {}
            continue
        changelogs["tournaments"][which] = changelog_tournaments(old_data["tournaments"][which],new_data["tournaments"][which])
    for t in changelogs["tournaments"]["pokemon"]:
        try:
            get_ptcg_tournament_format(t)
        except:
            print_log("Failed to find specific format for Pokémon TCG Tournament (this is expected for Japanese tournaments): "+t["name"])
    
    # send messages
    list_all = [
        "ptcg intl",
        "ptcg intl promo",
        "ptcg jpn",
        "ptcg jpn promo",
        "ptcg tournament",
        "vgc tournament",
        "ptcg pocket",
        "ptcg pocket promo",
        "onepiece product",
        "onepiece promo",
        "onepiece tournament",
        "lorcana",
        "riftbound",
        "swu",
        "bandai/dcg",
        "bandai/fw",
        "bandai/dbs",
        "bandai/bss",
        "bandai/gundam"
    ]
    for webhook in settings:
        filter_mode = webhook["filter_mode"]
        assert filter_mode in ["whitelist","blacklist"]
        list = webhook["filter_list"]
        if filter_mode=="blacklist":
            list = [x for x in list_all if x not in list]
        
        if "ptcg intl" in list:
            send_new_sets(webhook,changelogs["sets"]["international"],dbname="Pokémon TCG card database (international sets)")
        if "ptcg intl promo" in list:
            send_new_promos(webhook,changelogs["sets"]["international"],dbname="Pokémon TCG card database (international sets)")
        if "ptcg jpn" in list:
            send_new_sets(webhook,changelogs["sets"]["japanese"],dbname="Pokémon TCG card database (Japanese sets)")
        if "ptcg jpn promo" in list:
            send_new_promos(webhook,changelogs["sets"]["japanese"],dbname="Pokémon TCG card database (Japanese sets)")
        if "ptcg tournament" in list:
            send_tournaments(webhook,changelogs["tournaments"]["pokemon"],dbname="Pokémon TCG tournament database")
        if "vgc tournament" in list:
            send_tournaments(webhook,changelogs["tournaments"]["vgc"],dbname="Pokémon Video Game tournament database")
        if "ptcg pocket" in list:
            send_new_sets(webhook,changelogs["sets"]["pocket"],dbname="Pokémon TCG Pocket card database")
        if "ptcg pocket promo" in list:
            send_new_promos(webhook,changelogs["sets"]["pocket"],dbname="Pokémon TCG Pocket card database")
        if "onepiece product" in list:
            send_new_sets(webhook,changelogs["sets"]["onepiece products"],dbname="One Piece TCG card database (products)")
            pass
        if "onepiece promo" in list:
            send_new_sets(webhook,changelogs["sets"]["onepiece promos"],dbname="One Piece TCG card database (promos)")
            pass
        if "onepiece tournament" in list:
            send_tournaments(webhook,changelogs["tournaments"]["onepiece"],dbname="One Piece TCG tournament database")
        if "lorcana" in list:
            send_new_sets(webhook,changelogs["sets"]["lorcana"],dbname="Lorcana card database")
        if "riftbound" in list:
            send_new_sets(webhook,changelogs["sets"]["riftbound"],dbname="Riftbound card database")
        if "swu" in list:
            send_new_sets(webhook,changelogs["sets"]["swu"],dbname="Star Wars Unlimited card database")
        if "bandai/dcg" in list:
            send_new_sets(webhook,changelogs["sets"]["bandai/dcg"],dbname="Digimon card database")
        if "bandai/fw" in list:
            send_new_sets(webhook,changelogs["sets"]["bandai/fw"],dbname="DBS: Fusion World card database")
        if "bandai/dbs" in list:
            send_new_sets(webhook,changelogs["sets"]["bandai/dbs"],dbname="DBS: Masters card database")
        if "bandai/bss" in list:
            send_new_sets(webhook,changelogs["sets"]["bandai/bss"],dbname="Battle Spirits Saga card database")
        if "bandai/gundam" in list:
            send_new_sets(webhook,changelogs["sets"]["bandai/gundam"],dbname="Gundam Card Game card database")
    
    old_data = new_data
    for x in ["sets","tournaments"]:
        for which in old_data[x]:
            if len(old_data[x][which])==0:
                continue
            with open(f"data/{filenames[x][which]}","w") as f:
                json.dump(old_data[x][which], f,indent=2)
            first_run[x][y]=False
    new_data = deepcopy(zero_data)
    
    print_log(f'Sleeping for {sleep_hours} hours')
    sleep(sleep_hours*3600)
    #sleep(30)