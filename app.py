from flask import Flask, render_template, request, flash, redirect,  url_for,session, jsonify
import requests
from flask_mail import Mail, Message
import stripe
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import datetime
from dateutil import parser
import pdb
from sqlalchemy import and_





# Create the Flask app instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['MAIL_SERVER']='smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'MAIL_USERNAME'
app.config['MAIL_PASSWORD'] = 'MAIL_PASSWORD'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
stripe.api_key = 'stripe key'
YOUR_DOMAIN = 'http://localhost:5000'
app.secret_key = 'your_secret_key_here'
full_name=""
admin_full_name = "Coaching Studio NY"
admin_email="MAIL_USERNAME"
start_time =""
date=""
phone=""
message=""
##### appointment class ####################

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    status = db.Column(db.String)
    payment_status = db.Column(db.String)
    date = db.Column(db.String)
    start_time = db.Column(db.String)  # Change the type to String
    end_time = db.Column(db.String)  

class BookedSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    booking_time = db.Column(db.String)
    user_email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending') 
    ##  flag for availablitity slot
    flag =db.Column((db.String), default="False")


###########send mail function ####################
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400

    # Handle the specific event type you're interested in
    if event.type == 'checkout.session.completed':
        # Payment was successful
        session = event.data.object
        # You can now update your database or perform other actions here

    return jsonify({'status': 'success'}), 200





@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1OArefL1PTlx4hpydZUEJ8yE',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url="http://coachingstudiony.com/success" ,
            cancel_url="http://coachingstudiony.com/",
            payment_intent_data={
                'metadata': {
                    'webhook_endpoint': 'http://coachingstudiony.com/'
                }
            }
        )
   
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

###########send mail function ####################
def send_mail():
    global full_name, email, date, start_time,phone,message
    subject = "Appointment Booked "
    if  len(message)>0:
        admin_message =  f"Hi Etsy, \n\n  Appointment has been booked for \n\n Name: {full_name} \n\n Email: {email}  \n\n Phone: {phone} \n\n Date: {date} {start_time}  \n\n Message: {message}" 
    else:
         admin_message =  f"Hi Etsy, \n\n  Appointment has been booked for \n\n Name: {full_name} \n\n Email: {email}  \n\n Phone: {phone} \n\n Date: {date} {start_time}"
      
    share_message = f"Hi {full_name},\n\nYour appointment with The Coaching Studio NY has been booked for {date} {start_time}.\n\nFor questions or to change your appointment, you can reach us at 347-369-7385 or email us at MAIL_USERNAME.\n\nAll the best,\n\nThe Coaching Studio"
    subject = "Appointment Booked"
    method = "checkout"
    msg = Message(subject, sender='MAIL_USERNAME', recipients=[email])
    msg.body = share_message
    mail.send(msg)
    msg = Message(subject, sender=email , recipients=['MAIL_USERNAME'])
    msg.body = admin_message
    mail.send(msg)
    return redirect(url_for('hello_world'))
    
@app.route('/success', methods=['GET', 'POST'])
def success():
    last_appointment = Appointment.query.order_by(Appointment.id.desc()).first()
    if last_appointment:
        last_appointment.payment_status = "paid"
        db.session.commit()
    return send_mail()
    


@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    return render_template('cancel.html')
    

# Route and view function for booking an appointment
@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    global full_name, email, date, start_time,phone,message
    full_name = request.form['full_name']
    email = request.form['email']
    date_str = request.form['date']
    start_time = request.form['time']
    phone = request.form['phone']
    message = request.form['address']
    # Create a new Appointment record
    new_appointment = Appointment(
        full_name=full_name,
        email=email,
        status="Pending",
        payment_status="Unpaid",
        date=date_str,
        start_time=start_time,
        phone = phone
    )

    # Add and commit the new appointment to the database
    db.session.add(new_appointment)
    db.session.commit()

    # Create a new BookedSlot record
    booked_slot = BookedSlot(
        appointment_id=new_appointment.id,
        booking_time=start_time,
        user_email=email,
        status="booked",
        flag=False  # Use False without quotes for a boolean value
    )

    # Add and commit the booked slot to the database
    db.session.add(booked_slot)
    db.session.commit()
        # Attempt to parse the date string
    parsed_date = parser.parse(date_str)

    # Format the parsed date in the desired format
    date = parsed_date.strftime("%B %d, %Y")
    return create_checkout_session()
    
##### edit  appointment and admin view ####################

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if request.method == 'POST':
        appointment.full_name = request.form['full_name']
        appointment.email = request.form['email']
        appointment.status = request.form['status']
        appointment.payment_status = request.form['payment_status']
        if request.form['date'] and  request.form['time']:
            appointment.date = request.form['date']
            appointment.start_time = request.form['time']
        db.session.commit()           
        parsed_date = parser.parse(appointment.date)
        date_str = parsed_date.strftime("%B %d, %Y")
        # Format the parsed date in the desired format
        subject = "Appointment Updated"
        message = f"Hi {appointment.full_name},\n\nYour appointment with The Coaching Studio NY has been updated by our team .\n\n Your appointment is at {date_str}  {appointment.start_time} \n\n Your appointment status is {appointment.status} and payment status is status {appointment.payment_status} .\n\nFor questions or to change your appointment, you can reach us at 347-369-7385 or email us at MAIL_USERNAME.\n\nAll the best,\n\nThe Coaching Studio"
        msg = Message(subject, sender='MAIL_USERNAME', recipients=[appointment.email])
        msg.body = message
        mail.send(msg)
        
        return redirect(url_for('admin_view'))
    
    return render_template('edit_appointment.html', appointment=appointment)

@app.route('/admin_view', methods=['GET', 'POST'])
def admin_view():
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return redirect(url_for('login'))

    appointments = Appointment.query.all()
    booked_slots = db.session.query(BookedSlot, Appointment).join(Appointment).all()
    availability_slots = [slot for slot, _ in booked_slots if slot.status == "Unavailable"]
    # Sort  by ID in descending order
    appointments = sorted(appointments, key=lambda x: x.id, reverse=True)
    booked_slots = sorted(booked_slots, key=lambda x: x[0].id, reverse=True)
    availability_slots = sorted(availability_slots, key=lambda x: x.id, reverse=True)


    if request.method == 'POST':
        # Handle delete and update actions
        if request.form['action'] == 'delete':
            appointment_id = int(request.form['appointment_id'])
            appointment = Appointment.query.get(appointment_id)
            if appointment:
                db.session.delete(appointment)
                db.session.commit()
        # Handle other actions like update
        return redirect(url_for('admin_view'))
    

    return render_template('admin_view.html', appointments=appointments , booked_slots= booked_slots ,availability_slots=availability_slots )

@app.route('/create_unavailability_slot', methods=['POST'])
def create_unavailability_slot():
    print(request.form)
    date = request.form['date']
    start_time = request.form['time']
    new_appointment = Appointment(
        status="Unavailable",
        payment_status="Unpaid",
        date=date,
        start_time=start_time,
    )
    db.session.add(new_appointment)
    db.session.commit()

    booked_slot = BookedSlot(
        appointment_id=new_appointment.id,
        booking_time=start_time,
        status="Unavailable",
        flag = "True"
    )
    db.session.add(booked_slot) 
    db.session.commit()

    return redirect(url_for('admin_view'))


@app.route('/delete_unavailability_slot/<int:slot_id>/<int:appointment_id>', methods=['POST'])
def delete_unavailability_slot(slot_id, appointment_id):
    unavailable_slot = BookedSlot.query.get_or_404(slot_id)
    unavailable_appointment = Appointment.query.get_or_404(appointment_id)

    # Delete the unavailable slot and appointment
    db.session.delete(unavailable_slot)
    db.session.delete(unavailable_appointment)

    db.session.commit()

    return redirect(url_for('admin_view'))

@app.route('/add_unavailable', methods=['GET', 'POST'])
def add_unavailable():
    return render_template('unavailable_slots.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_authenticated' in session and session['admin_authenticated']:
        return redirect(url_for('admin_view'))

    if request.method == 'POST':
        # Perform authentication check (replace this with your actual authentication logic)
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '123456':
            session['admin_authenticated'] = True
            return redirect(url_for('admin_view'))
        else:
            error = True
            return render_template('login.html', error=error)

    return render_template('login.html')  # tte the login template



##### rendering main index page ####################
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')






# Define a route and view function for sending email

@app.route('/contact_us', methods=['POST'])
def contact_us():
    method = "contact"
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    admin_email = "your email"
    user_message = request.form['message'] 
    for_message = f"Name : {full_name} \n\n Email: {email} \n\n Phone: {phone} \n\n Message: {user_message} "
    subject = "Contact Us"
    msg = Message(subject, sender=email, recipients=[admin_email])
    msg.body = for_message
    mail.send(msg)
    return hello_world()


###### api to fetch slots 
@app.route('/api/slots', methods=['GET'])
def get_slots():
    selected_date = request.args.get('date')  
    booked_slots = Appointment.query.filter(
        Appointment.date == selected_date,
        Appointment.status != 'Unavailable'
    ).all()

    unavailable_slots = Appointment.query.filter(
        and_(
            Appointment.date == selected_date,
            Appointment.status == 'Unavailable'
        )
    ).all()

    # Convert the records to a list of dictionaries
    booked_slots_list = [{'id': slot.id, 'booking_time': slot.start_time, 'status': slot.status} for slot in booked_slots]
    unavailable_slots_list = [{'id': slot.id, 'booking_time': slot.start_time, 'status': slot.status} for slot in unavailable_slots]
    return jsonify({'booked_slots': booked_slots_list, 'unavailable_slots': unavailable_slots_list})
      


# Run the app
if __name__ == '__main__':
    app.run(debug=False)
