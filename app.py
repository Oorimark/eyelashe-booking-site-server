from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
from pymongo import MongoClient
from waitress import serve

app = Flask(__name__)
# cluster = MongoClient("mongodb+srv://lashdout:lashdoutpwd@cluster0.xcz3g.mongodb.net/?retryWrites=true&w=majority")
cluster = MongoClient("mongodb+srv://pythoneverywhere:pythoneverywherepwd@cluster0.xcz3g.mongodb.net/?retryWrites=true&w=majority")
db = cluster['Lasdoutbc_dataHouse']
collection = db['bookedDetails']
CORS(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'markpublicm@gmail.com'
app.config['MAIL_PASSWORD'] = 'xodvtzyiphvkhrmu'
app.config['MAIL_DEFAULT_SENDER'] = ('Lashedout_bc','markpublicm@gmail.com')
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# plain text mails
mail = Mail(app)

# html formatted mail
def htmlMail(id_, status, userDetails, bookingDetails, appointmentDate):
    with app.app_context():
        message = Message("Hello, A Booking has been made",recipients=['oorimark@gmail.com'])
        message.html = f"""
            <div>
                <h2>Booking information</h2>
                <hr />
                <h4> User Information </h4>
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
    print(data)
    collection.insert_one(data)
    # booked_details_collection.insert_one(data)

def update(id, status):
    try:
        booked_details_collection.update_one({'_id': id}, {'$set': {'status': status}})
        return 1
    except:
        return 0

def fetchData(ids):
    """ Fetch the status for each bookedService """
    response = dict()
    response_list = list()
    for id in ids:
        data = booked_details_collection.find_one({'_id': id})
        response[id] = data['status']
        response_list.append(response)
    return response_list

# ===============================================

@app.route("/fetch", methods=['POST'])
def FetchBookedService():
    data = request.json
    response = fetchData(data.get('ids'))
    pack_data = {'data': response}
    return jsonify(pack_data), 200

@app.route("/update/<id>/<status>", methods=['GET'])
def UpdateBookedService(id, status):
    response = update(id, status)
    if(response):
        res = ("The client has been informed")
    res = ("Something went wrong. call the developers attention")
    return res

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
    print(data, id_, status,  user_details, booking_details, appointment_date)
    res = htmlMail(id_, status, user_details, booking_details, appointment_date)

    try:
        insertData(id_, status, user_details, booking_details, appointment_date)
        return "success"
    except:
        return "Problem inserting to database", 400
    return "success"

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=50100, threads=2)