from flask import Flask, render_template, request##import required libraries and modules
import requests, redis, json

conn = redis.StrictRedis(decode_responses=True)#connect to redis database using the StrictRedis
app = Flask(__name__)

@app.route('/temperature', methods=['POST'])#set a route with post method for posting ip addresses
def temperature():
    IP_Address = request.form['zip']#gets IP address using the form in the index.html
    newDataBase = "forza"#set a variable holding the database name
    if conn.exists(newDataBase) == 1:#check if database redis key exist, 1 means it exist
        print("Database exist")
        newData = conn.hmget(newDataBase, "ip")#get data from the database with key name ip
        if str(IP_Address) in newData:#checks if the ip supplied is in the database data
            print("Data exist in database")
            existingData = conn.hmget(newDataBase, "ip", "continent_name", "country_name", "region_name", "latitude", "longitude")#get data with specified fields from the database
            ip_add = existingData[0];ip_cont = existingData[1];ip_count = existingData[2];ip_state = existingData[3];ip_lat = existingData[4];ip_long = existingData[5]#assign each one to a variable using their index

        else:#otherwise key does not exist
            print("Data do not exist in the database")
            json_, json_object = removeNull(IP_Address, newDataBase)#call function removeNull, pass in the parameters and assing what it returns to variables
            ip_add = json_object['ip'];ip_cont = json_object['continent_name'];ip_count = json_object['country_name'];ip_state = json_object['region_name'];ip_lat = json_object['latitude'];ip_long = json_object['longitude']

        return render_template('temperature.html', temp=ip_add, cont=ip_cont, count=ip_count, lati=ip_lat, longi=ip_long, state=ip_state)

    else:
        print("Database Do not exist")#for when database does not exist, create a new by calling removeNull
        json_, json_object = removeNull(IP_Address, newDataBase)#assign returned data

        return json_

def cleanJson(IP_Address):
    json_obj = requests.get('http://api.ipstack.com/'+IP_Address+'?access_key=024e3f392effb6c46a4003ad68617a4f').json()#this function handles the get request of the API, convert it into json and gets required keys and values from it
    return {prop: val for prop, val in json_obj.items() if prop not in ["location", "zip", "type", "continent_code", "country_code", "region_code"]}#this returns a cleaned json with location and other fields removed

def removeNull(IP_Address, newDataBase):
    json_ = cleanJson(IP_Address)#function calls clenjson output, removes null values from the json to make it valid for dumping
    json_ = json.dumps(json_).replace("null",'"empty"')#replaces null with empty
    try:
        json_object = json.loads(json_)#set a try catch to load json objects and set the mapped data in the redis database
        newData = conn.hmset(newDataBase, json_object)
    except Exception as error:
        print("Error here: ",error)

    return (json_, json_object)#returns json_ (suitable for viewing in the browser) and json_object(already loaded json) for further operation

@app.route('/')
def index():
    return render_template('index.html')#the homepage of the app service

if __name__ == '__main__':
    app.run(host="localhost", port=5011, debug=True)#set port number for flask to run