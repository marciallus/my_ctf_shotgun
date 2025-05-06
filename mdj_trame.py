import json
import requests
import time
from parse import parse

url_canon = "http://127.0.0.1:5000/cmd"

x = 0
y = 0
config = json.load(open('config.json'))
for team in config['teams']:
    print(team['name'] + " " + str(team['x']) + " " + str(team['y']))
    delta_x = team['x'] - x
    delta_y = team['y'] - y
    #move to dist
    cmd = "G0 X"+str(delta_x)+" Y"+str(delta_y) + ";"
    data = {"cmd":cmd,"from":0}
    print(data)
    response = requests.post(url=url_canon,data=data) # Move
    print(response.text)
    time.sleep(2)#must wait for end of move

    #getpos
    cmd = "M114;"    
    data = {"cmd":cmd,"from":0}
    print(data)
    
   
    parse_string = "X: {x} Y: {y}"
    

    response = requests.post(url=url_canon,data=data) # Move
    print(response.text)
    parsed = parse(parse_string, response.text)

    stop_flag = False

    while not stop_flag:

        response = requests.post(url=url_canon,data=data) # Move
        print(response.text)
        parsed1 = parse(parse_string, response.text)
        time.sleep(2)
        response = requests.post(url=url_canon,data=data) # Move
        print(response.text)
        parsed2 = parse(parse_string, response.text)
        stop_flag = parsed1['x'] == parsed2['x'] and parsed1['y'] == parsed2['y']
        print(stop_flag)

    #tir
    cmd = "M106;"    
    data = {"cmd":cmd,"from":0}
    print(data)
    response = requests.post(url=url_canon,data=data) # Move
    print(response.text)
    x += delta_x
    y += delta_y



