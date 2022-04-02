from flask import Flask, request
from dbconfig import *
from dotenv import load_dotenv

load_dotenv('.env')
app = Flask(__name__)

db = mongodb()


class Actor(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    password = db.StringField(required=True)
    role = db.StringField(required=True)

    meta = {'db_alias': 'user_db'}


class Notification(db.Document):
    recipient_id = db.ReferenceField(Actor)
    msg = db.StringField(min_length=1, required=True)
    is_read = db.BooleanField(required=True)

    meta = {'db_alias': 'notifs_db'}


@app.route('/fetch', methods=['GET'])
def get_notifications():
    recipient_id = request.json['recipient_id']
    if recipient_id is None or '':
        return "No user ID provided."
    else:
        notifs = Notification.objects(
            recipient_id=recipient_id).order_by("-_id")
        return notifs.to_json()


@app.route('/notify', methods=['POST'])
def send_notification():
    if 'recipient_id' not in request.json:
        return "No recipient given"
    if 'msg' not in request.json:
        return "Empty message!"
    else:
        rec_id = request.json['recipient_id']
        msg = request.json['msg']

        try:
            valid = False if Actor.objects(
                _id=rec_id).first() is None else True

            if not valid:
                raise Exception("Recipient does not exist!")
            Notification(recipient_id=rec_id, msg=msg, is_read=False).save()

        except Exception as e:
            return "Error while sending notification : " + str(e)

        return "Notification Sent!"


if __name__ == "__main__":
    app.run(port=8000, debug=True)