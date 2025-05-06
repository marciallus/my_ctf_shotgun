from flask import Flask
from flask import request
from parse import parse
import requests
import time
import math
import json

app = Flask(__name__)
config = json.load(open('config.json'))
for team in config['teams']:
    print(team['name'] + " " + str(team['x']) + " " + str(team['y']))

canon_url = "http://192.168.1.11:5000/cmd"

last_pos_x = 0 # mm
last_pos_y = 0 # mm

last_x_order = 0 # mm
last_y_order = 0 # mm

last_x_order_time = 0
last_y_order_time = 0

# speed_x = (360/44) # mm/s
# speed_y = (40/24) # mm/s


speed_x = 1000
speed_y = 1000

treshold = 10 # mm

deg_to_canon = (7.4 / 360)

#MAX is 7.4mm for 360 deg
#MAX TIME for 360 Deg is 44s




@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def send_cmd_to_canon(cmd):
    print("requesting canon: " + cmd)
    try:
        x = requests.get('http://192.168.1.11:5000/cmd/' + cmd, timeout=1) # to do change value
        return x
    except:
        print("timeout")
    return None


def get_current_pos():
    print("get_current_pos")
    x = last_pos_x + (time.time() - last_x_order_time) * speed_x * math.copysign(1,last_x_order)
    y = last_pos_y + (time.time() - last_y_order_time) * speed_y * math.copysign(1,last_y_order)
    is_moving() # update the position

    if 0 == last_x_order:
       x = last_pos_x
    
    if 0 == last_y_order:
        y = last_pos_y

    print("get_current_pos returning: " + str(x) + " " + str(y))
    return x,y

def is_moving():
    """ check if the machine is moving 
    and update x and y  position"""    

    global last_pos_x
    global last_pos_y
    global last_x_order_time
    global last_y_order_time
    global last_x_order
    global last_y_order


    print("last_pos_x: " + str(last_pos_x) + " last_pos_y: " + str(last_pos_y))
    print("last_x_order: " + str(last_x_order) + " last_y_order: " + str(last_y_order))
    print("last_x_order_time: " + str(last_x_order_time) + " last_y_order_time: " + str(last_y_order_time))

    
    print("" + str(time.time() - last_x_order_time) +" < " + str(abs(last_x_order )/speed_x))
    print("" + str(time.time() - last_y_order_time) +" < " + str(abs(last_y_order )/speed_y))

    if (time.time() - last_x_order_time) < (abs(last_x_order )/speed_x):
        return True
    
    print("x finished moving")
    last_pos_x = last_x_order + last_pos_x
    last_x_order = 0;

    if (time.time() - last_y_order_time) < (abs(last_y_order )/speed_y):
        return True

    print("y finished moving")
    last_pos_y = last_y_order + last_pos_y
    last_y_order = 0;

    
    return False

def start_move(x, y):
    """ start the move """
    global last_x_order_time
    global last_y_order_time
    global last_x_order
    global last_y_order


    last_x_order_time = time.time()
    last_y_order_time = time.time()

    last_x_order = x
    last_y_order = y
    
    print("start move x: " + str(x) + " y: " + str(y))
    print("last_pos_x: " + str(last_pos_x) + " last_pos_y: " + str(last_pos_y))
    print("last_x_order: " + str(last_x_order) + " last_y_order: " + str(last_y_order))
    print("last_x_order_time: " + str(last_x_order_time) + " last_y_order_time: " + str(last_y_order_time))

    curr_x, curr_y = get_current_pos()
    
    status = send_cmd_to_canon('G0 Z' + str((x+curr_x)*deg_to_canon) +' F10') # to do change value
    print("status: " + str(status))

    status = send_cmd_to_canon('G0 Y' + str(y+curr_y) +' F100') # to do change value
    print("status: " + str(status))


def parse_move_cmd(cmd):
    """ parse G0 move command"""


    print("parsing")
    print("command: "+cmd)

    try:
        # check if the command is valid
        if "G0" not in cmd:
            return False
        
        if ("X" not in cmd or "Y" not in cmd):
            return False
        
        if ";" not in cmd:
            return False

        # parse the command
        parse_string = "G0"
        if "X" in cmd:
            parse_string += "X{x}" 
        if "Y" in cmd:
            parse_string += "Y{y}"
        parse_string += ";"
        print("parse_string: " + str(parse_string))
        parsed = parse(parse_string, cmd)
        print("parsed: " + str(parsed))
        if parsed is None:
            return False
        
        print(parsed)

        x, y = get_current_pos()
        parsed_x = int(parsed['x'])
        parsed_y = int(parsed['y'])
        print("x: " + str(x) + " y: " + str(y))
        print("parsed['x']: " + str(parsed_x) + " parsed['y']: " + str(parsed_y))

        if x+parsed_x > 360 or x+parsed_x< 0 or y+parsed_y > 40 or y+parsed_y < 0:     
            return False
        print("start moving")
        start_move(parsed_x, parsed_y)

    except:
        print("execpt")
        
        return False
    return True

def tir( team_from):
    for team in config['teams']:
       
        x, y = get_current_pos()
        if abs(team['x'] - x) < treshold and abs(team['y'] - y) < treshold:
            try:
                print("tir from " + str(team_from) + " to " + str(team['name']))
                print("requesting allumage canon")
                if int(team_from) != 0:
                    print("requesting tir canon")
                    status = send_cmd_to_canon('M104 S65;') # to do change value
                    time.sleep(3)
                    print("requesting fin tir canon")
                    status = send_cmd_to_canon('M104 S0;') # to do change value
                    print("status: " + str(status))
                    x = requests.post(url='http://10.45.0.1:5000/canon/', 
                                    header={"Content-type":"application/json"},
                                    data='{"source":1,"cible":0}',
                                    timeout=1) # to do change value
   

            except:
                print("timeout")
                
            return True
    return False

@app.route("/cmd", methods = ['POST'])
def cmd():
    data = request.form
    if "cmd" not in data:
        return "No command"

    command = request.form.get('cmd')  # get the command
    command = command.replace(" ", "")  # remove spaces
    command = command.upper()  # make it uppercase
    command = command.split("#")[0]  # remove comments
    if  ("M114" in command):
      
        x,y = get_current_pos()
        return "X: " + str(x) + " Y: " + str(y)        
    

    if is_moving():
        return "Already moving wait for it to finish"

    if ("G28;" in command):
        start_move(-last_pos_x, -last_pos_y)
        return "Homing"
    
    if ("G0" in command):
        if parse_move_cmd(command):
            return "OK"
        
    if ("M106" in command):
        if "from" in data:
            tir(data.get('from'))
            return "OK"

    return "malformed command"


