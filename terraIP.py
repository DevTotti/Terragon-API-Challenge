from flask import Flask, render_template, request
import requests, redis, json

conn = redis.StrictRedis(decode_responses=True)

app = Flask(__name__)

@app.route('/temperature', methods=['POST'])
def temperature():
    IP_Address = request.form['zip']
    newDataBase = "refac"
    if conn.exists(newDataBase) == 1:
        print("Database exist")
        newData = conn.hmget(newDataBase, "ip")
        if str(IP_Address) in newData:
            print("Data exist in database")
            existingData = conn.hmget(newDataBase, "ip", "continent_name", "country_name", "region_name", "latitude", "longitude")
            ip_add = existingData[0];ip_cont = existingData[1];ip_count = existingData[2];ip_state = existingData[3];ip_lat = existingData[4];ip_long = existingData[5]

        else:
            print("Data do not exist in the database")
            json_, json_object = removeNull(IP_Address, newDataBase)
            ip_add = json_object['ip'];ip_cont = json_object['continent_name'];ip_count = json_object['country_name'];ip_state = json_object['region_name'];ip_lat = json_object['latitude'];ip_long = json_object['longitude']

        return render_template('temperature.html', temp=ip_add, cont=ip_cont, count=ip_count, lati=ip_lat, longi=ip_long, state=ip_state)
        
    else:
        print("Database Do not exist")
        json_, json_object = removeNull(IP_Address, newDataBase)

        return json_

def cleanJson(IP_Address):
    json_obj = requests.get('http://api.ipstack.com/'+IP_Address+
                            '?access_key=024e3f392effb6c46a4003ad68617a4f').json()
    return {prop: val for prop, val in json_obj.items() if prop not in
            ["location", "zip", "type", "continent_code", "country_code", "region_code"]}


def removeNull(IP_Address, newDataBase):
    json_ = cleanJson(IP_Address)
    json_ = json.dumps(json_).replace("null",'"NIL"')
    try:
        json_object = json.loads(json_)
        print(json_object)
        newData = conn.hmset(newDataBase, json_object)
    except Exception as error:
        print("Error here: ",error)

    return (json_, json_object)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="localhost", port=5011, debug=True)