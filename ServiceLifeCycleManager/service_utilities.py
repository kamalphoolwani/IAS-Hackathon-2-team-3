import mongoengine as db
import os
import dotenv
dotenv.load_dotenv()

database_name = 'SLCM_DB'
mduser = os.getenv('MONGODB_USER')
mdpass = os.getenv('MONGODB_PASS') 
cluster = os.getenv('MONGODB_CLUSTER')
PORT = os.getenv('PORT')
DB_URI ='mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority'.format(mduser,mdpass , cluster,database_name)


def mongodb():
    db.connect(host=DB_URI)
    return db

db = mongodb()


class slcm(db.Document):
    instance_id = db.IntField()
    service_type = db.StringField()
    service_name = db.StringField()
    state = db.StringField()
    ip = db.StringField()
    port = db.StringField()
    def to_json(self):
        return {
            "instance_id":self.instance_id,
            "service_type": self.service_type,
            "service_name" : self.service_name,
            "state":self.state,
            "ip" : self.ip,
            "port":self.port
        }

def savetodb(kwargs):
    try:
        data = slcm(**kwargs)
        data.save()
        return "success"
    except Exception as e: 
        return "failed with {}".format(e)


def fetchdb(kwargs):
    try:
        data = slcm.objects(**kwargs)
        return data
    except Exception as e:
        return  "failed with {}".format(e)

def updatedb(kwargs,kwargs2):
    try:
        data = slcm.objects(**kwargs).update(**kwargs2)
        return "success"
    except Exception as e:
        return  "failed with {}".format(e)
    
def inc_service(name , stype):
    try :
        obj = slcm.objects(service_name = name,service_type =stype)
        cur = obj.usedby
        obj.update(useddby = cur+1)
        return "success"
    except Exception as e:
            return e

def dec_service(name , stype):
    try :
        obj = slcm.objects(service_name = name,service_type =stype)
        cur = obj.usedby
        obj.update(useddby = cur-1)
        return cur-1
    except Exception as e:
            return e


# data =  {"service_id":1 , "service_name" : "service4","service_type" : "Asdasd","ip":"asdasdas","port":"fsdfsd"}
# data1 = {"service_name" : "service4"}
# data2 = { "service_name" : "serrvice5"}

# savetodb(data)

# print(updatedb(data1,data2))