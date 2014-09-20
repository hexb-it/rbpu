import urllib.request
import urllib.parse
import json
import csv
import os.path
import smtplib
import triang
import getpass

def get_json( latitude, longitude, before = '', page = '1'):
    data = urllib.parse.urlencode({'action':'radius-search',
    'latitude':str(latitude),
    'longitude':str(longitude),
    'distance':'2',
    'sort':'distance',
    'page':page,
    'before':before,
    'status%5B%5D':'0',
    'status%5B%5D':'2'})
    data = data.encode('utf-8')
    request = urllib.request.Request("http://redbullpicup.com/handlers/Stash.php")
    # adding charset parameter to the Content-Type header.
    request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
    f = urllib.request.urlopen(request, data)
    rawjson = f.read().decode('utf-8')
    return rawjson
    
def write_csv( res ):
    old = read_csv()
    with open('rbpu.csv', "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for val in res:
            writer.writerow([val])
        for val in old:
            writer.writerow([val])

def read_csv():
    res = []
    if os.path.isfile('rbpu.csv'):
        with open('rbpu.csv', "r") as output:
            reader = csv.reader(output, lineterminator='\n')
            for line in reader:
                res.append(line[0])
    return res

def check_new( new ):
    ret = []
    old = read_csv();
    for id in new:
        if id not in old:
            ret.append(id)
    #write_csv(ret)
    return ret

def create_email( myjson, new ):
    LatA = 0
    LonA = 0
    LatB = 0
    LonB = 0
    LatC = 0
    LonC = 0
    email = ''
    if new != []:
        email = 'Number of Pic Ups: ' + str(len(new)) + '\n\n'
        for item in new:
            email = email + item + '\n'
            for var in myjson[item]:
                email = email + var + ' : ' + str(myjson[item][var]) + '\n'
            DistA = get_distance(item, LatA, LonA)
            DistB = get_distance(item, LatB, LonB)
            DistC = get_distance(item, LatC, LonC)
            email = email + '\nlocation : https://www.google.com/maps/place/' + triang.locate(LatA, LonA, DistA, LatB, LonB, DistB, LatC, LonC, DistC) + '\n'
            email = email + '\n'
        return email

def send_email( email ):
    if email != None:
        username = input('Gmail username: ')
        password = getpass.getpass()
        target = input('Target: ')
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        msg = "\r\n".join([
        "From: "+target,
        "To: "+target,
        "Subject: New Redbull Pic Ups",
        "",
        email + '\nSent via: https://github.com/hexb-it/redbullpicup\nDeveloped by John Adams\n'
        ])
        server.sendmail(username, target, msg)

def parse_json(latitude, longitude):
    djson = json.loads(get_json(latitude, longitude))
    jsondata = djson['data']
    pages = jsondata['result']['paging']['pages']
    before = jsondata['result']['paging']['before']
    stashes =  jsondata['stashes']
    for num in range(2, int(pages)+1):
        djson = json.loads(get_json(latitude, longitude, before, str(num)))
        jsondata = djson['data']
        before = jsondata['result']['paging']['before']
        for item in jsondata['stashes']:
            stashes.append(item)
    return stashes
    
def format_json( stashes ):
    retDict = {}
    for stash in stashes:
        if stash['is_claimed'] != True:
            del stash['photo_alt_url']
            del stash['is_claimed']
            del stash['claimed_text']
            id = stash['id']
            del stash['id']
            retDict[id] = stash
    return retDict
    
def get_distance(id, lat, lon):
    fromweb = format_json(parse_json(lat, lon))
    distance =  fromweb[id]['distance']['meters']
    distance = float(distance)/1000
    return distance

def main():
    LatE = 0
    LonE = 0
    
    ejson = format_json(parse_json(LatE, LonE))
    new = check_new(ejson)
    
    send_email(create_email( ejson, new ))

    write_csv(new)

main()
