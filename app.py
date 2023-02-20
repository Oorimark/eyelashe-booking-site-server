from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo import MongoClient
from waitress import serve
import json

# admin_blueprint = Blueprint('admin_blueprints', __name__, url_prefix="/setAdmin")
ADMIN_SETTINGS_DB_ID = "63f35d6f9fd0ec07e73aa55b"

app = Flask(__name__)
# app.register_blueprint(admin_blueprint)
cluster = MongoClient("mongodb+srv://pythoneverywhere:pythoneverywherepwd@cluster0.xcz3g.mongodb.net/?retryWrites=true&w=majority")

ADMIN_EMAIL = 'oorimark@gmail.com'
db = cluster['Lasdoutbc_dataHouse']
booked_details_collection = db['bookedDetails']
contact_message_collection = db['contactMessages']
admin_settings = db['adminSettings']
users_collection = db['users']

CORS(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'markpublicm@gmail.com'
app.config['MAIL_PASSWORD'] = 'xodvtzyiphvkhrmu'
app.config['MAIL_DEFAULT_SENDER'] = ('Lashedout_bc','markpublicm@gmail.com')
app.config['MAIL_ASCII_ATTACHMENTS'] = False

mail = Mail(app)

# html formatted mail
def test_mailing_service():
    with app.app_context():
        message = Message("Hello, how are you", recipients=['oorimark@gmail.com'])
        message.body = "How are you doing today?"
        mail.send(message)
        
def booked_service_cancellation_mail_template(id_, userDetailsID, bookingDetailsID):
    with app.app_context():
        message = Message(f"Hi, A Booking Cancellation by {userDetailsID}", recipients=[ADMIN_EMAIL])
        message.html = f""" 
            <div>
                <h2> Booking Cancellation Information </h2>
                <hr />
                <h4> User Information </h4>
                <p> Booking Id: {id_} </p>
                <p> User Id: {userDetailsID} </p>
                <p> Service Id: {bookingDetailsID} </p>
            </div>
        """
        mail.send(message)
    return "success"

def contact_mail_template(email, msg):
    with app.app_context():
        message = Message(f"A Contact Message from {email}", recipients=[ADMIN_EMAIL])
        message.body = msg
        mail.send(message)
        
def booked_service_mail_template(id_, status, userDetails, bookingDetails, appointmentDate):
    firstName = userDetails['firstName']
    lastName = userDetails['lastName']
    with app.app_context():
        message = Message(f"Hello, A Booking has been made by {firstName} {lastName}",recipients=[ADMIN_EMAIL])
        message.html = f"""
            <div>
                <h2>Booking information</h2>
                <hr />
                <h4> User Information </h4>
                <p> Booking ID: {id_} </p>
                <p> Status: {status}</p>
                <p> Full Name: {userDetails['firstName']} {userDetails['lastName']} </p>
                <p> Email: {userDetails['email']} </p>
                <p> Phone Number: {userDetails['phone']} </p>
                <hr />
                <h4> Booking Information </h4>
                <p> Name: {bookingDetails['name']} </p>
                <p> Price : {bookingDetails['price']} </p>
                <p> Description: {bookingDetails['description']}</p>
                <hr />
                <h4> Appointment Time </h4>
                <h3>{appointmentDate}</h3>
                <div style="
                    display: flex;
                    align-items: center;
                    column-gap: 4rem;
                    ">
                <a href="https://lashedoutbc.onrender.com/update/{id_}/approved" >
                    <div
                        id="accept"
                        style="
                            background-color: #B0223B;
                            padding: .7rem 2.7rem;
                            color: white;
                            border-radius: 3rem;
                            cursor: pointer;
                            ">
                        Accept
                    </div>
                </a>
                <a href="https://lashedoutbc.onrender.com/update/{id_}/rejected" >
                    <div
                        id="reject"
                        style="
                            border: .2rem solid #B0223B;
                            padding: .7rem 2.7rem;
                            border-radius: 3rem;
                            cursor: pointer;
                            "
                        >
                        Reject
                    </div>
                </a>
                </div>
            </div>
        """
        mail.send(message)
    return "success"

# =============== DATABASE =====================

""" Configuration """

""" Operations (Logic) """

def insertData(id_, status, user_details, booking_details, appointment_date):
    userDetailsID = user_details['id']
    serviceDetailsID = booking_details['id']
    data = {
        '_id': id_,
        'status': status,
        'userDetailsID': userDetailsID,
        'serviceDetailsID': serviceDetailsID,
        'appointmentDate': appointment_date
    }
    booked_details_collection.insert_one(data)
    # booked_details_booked_details_collection.insert_one(data)

def update(id, status):
    try:
        booked_details_collection.update_one({'_id': id}, {'$set': {'status': status}})
        return 1
    except:
        return 0

def fetchDataStatus(ids):
    """ Fetch the status for each bookedService """
    response_list = list()
    
    for id in ids:
        response = dict()
        data = booked_details_collection.find_one({'_id': id})
        if data:
            response['id'] = id
            response['status'] = data['status']
            response_list.append(response)
        else:
            raise Exception
    return response_list

def fetchData(id):
    data = booked_details_collection.find_one({'_id': id})
    return data

# ===============================================

@app.route("/fetch", methods=['POST'])
def FetchBookedService():
    data = request.json
    
    if data.get('ids'):
        try:
            response = fetchDataStatus(data.get('ids'))
        except:
            return jsonify({'error': 'service cannot be found'}), 400
        else:
            pack_data = {'data': response}
            return jsonify(pack_data), 200
    else:
        return "data received is empty", 400
    
@app.route("/deleteService", methods=['POST'])
def DeleteService():
    data = request.json
    id = data.get('id')

    try:
        # before deleting send an email to admin
        queried_data = fetchData(id)
        print(queried_data)
        _id , _, user_details, service_details, _ = queried_data.values()
        print(_id, user_details, service_details)
        booked_service_cancellation_mail_template(
            _id, user_details, service_details
        )
        booked_details_collection.delete_one({'_id': id})
        return "success", 200
    except:
        return "error", 400

@app.route("/sendContactMessage", methods=['POST'])
def ContactMessage():
    data = request.json
    email = data.get('email')
    msg = data.get('msg')
    
    contact_mail_template(email, msg) # send email
    contact_message_collection.insert_one(data) # send to db
    return "success", 200
    
@app.route("/update/<id>/<status>", methods=['GET'])
def UpdateBookedService(id, status):
    response = update(id, status)
    if(response):
        return ("The client has been informed")
    return ("Something went wrong. call the developers attention")

@app.route("/addUser", methods={'POST'})
def AddUsers():
    data = request.json
    try:
        users_collection.insert_one(data)
        return jsonify({"data": "success"}), 200
    except Exception as e:
        return jsonify({"data": "error", "err_details": e}), 400

@app.route("/testing")
def Testing():
    test_mailing_service()
    return "success"

@app.route("/")
def Home():
    return "Welcome to Lashdout"

@app.route("/send", methods=['POST'])
def Index():
    data = request.json
    id_ = data.get('id')
    status = data.get('status')
    user_details = data.get('userDetails')
    booking_details = data.get('bookingDetails')
    appointment_date = data.get('appointmentDate')
    res = booked_service_mail_template(id_, status, user_details, booking_details, appointment_date)

    try:
        insertData(id_, status, user_details, booking_details, appointment_date)
        return "success"
    except:
        return "Problem inserting to database", 400
    return "success"

@app.route("/changeAdminSettings", methods=['POST'])
def change_settings():
    changes = request.json
    print(changes)
    admin_settings.update_one({'_id': ADMIN_SETTINGS_DB_ID}, {'$set': changes})
    return "success"

@app.route("/fetchAdminSettings")
def fetch_admin_settings():
    settings = admin_settings.find()
    for setting in settings:
        admin_setting = setting
    return jsonify(admin_setting), 200

# """ BLUEPRINT 
#     NB: Move a folder ASAP
# """
# @admin_blueprint.route('/changeAdminSettings', methods=['POST'])
# def change_settings():
#     changes = request.json
#     print(changes)
#     admin_settings.update_one({'_id': ADMIN_SETTINGS_DB_ID}, {'$set': changes})
#     return "success"

mode = 'prod'
if __name__ == "__main__":
    if mode == 'dev':
        app.run(debug=True, port=8000)
    else:
        serve(app, host='0.0.0.0', port=50100, threads=2)