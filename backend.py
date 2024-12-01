from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from Sales_pred_func import sales_prediction  # Prediction with help of ML_Model
from Using_Inventory_Maximization import maxProfit
import re
import logging
import random, time
# from datetime import timedelta
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import smtplib


# Initialize Flask app
app = Flask(__name__)

# CORS(app)
CORS(app, origins=["http://localhost:3000"])

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'databases/database.db')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testing6864@gmail.com'  # Replace with your email
# app.config['MAIL_PASSWORD'] = 'test@6864'   # Replace with your email password
app.config['MAIL_PASSWORD'] = 'gmwn xmep lrlt cenc'
mail = Mail(app)

# Temporary in-memory store for email-verification code mapping
verification_data = {}

# Generate a secret key for session management
secret_key = os.urandom(24)
app.secret_key = secret_key

# app.permanent_session_lifetime = timedelta(minutes=10)  # Set session timeout as needed

# Initialize the serializer for token generation and verification
serializer = URLSafeTimedSerializer(app.secret_key)

# Log configuration for better debugging
logging.basicConfig(level=logging.DEBUG)

# Define databases
class Credentials(db.Model):
    __tablename__ = "Credentials"
    userId = db.Column('userId', db.Integer, primary_key = True, autoincrement = True)
    userName = db.Column('userName', db.Text, nullable = False)  # Increased length to 50
    email = db.Column('email', db.Text, nullable = False)  # Increased length to 100
    password = db.Column('password', db.Text, nullable = False)  # Increased length to 128 for password hash
    date = db.Column('date',db.String(12), nullable = False)

class CustomerInfo(db.Model):
    __tablename__ = "CustomerInfo"
    userId = db.Column('userId', db.Integer, primary_key = True)
    companyName = db.Column('companyName', db.Text, nullable = False)
    state = db.Column('state', db.Text, nullable = False)
    prodCategories = db.Column('prodCategories', db.Text, nullable = False)  # Text type for storing JSON data
    mobileNumber = db.Column('mobileNumber', db.Integer, nullable = False)
    city = db.Column('city', db.Text, nullable = False)

class Check(db.Model):
    __tablename__ = "Check"
    catId = db.Column('catId', db.Integer, primary_key = True, autoincrement = True)
    catName = db.Column('catName', db.Text, nullable = False)
    state = db.Column('state', db.Text, nullable = False)
    itemName = db.Column('itemName',db.Text, nullable = False)
    sales = db.Column('sales',db.Integer, nullable = False)

class Inventory(db.Model):
    __tablename__ = "Inventory"
    userId = db.Column('userId', db.Integer, primary_key = True, autoincrement = True)
    itemId = db.Column('itemId', db.Text, primary_key = True)
    itemName = db.Column('itemName', db.Text, nullable = False)
    quantity = db.Column('quantity', db.Integer, nullable = False)
    catName = db.Column('catName', db.Text, nullable = False)
    costPrice = db.Column('costPrice', db.Integer, nullable = False)
    sellingPrice = db.Column('sellingPrice', db.Integer, nullable = False)

# class UserHistory(db.Model):
#     __tablename__ = 'userHistory'
#     userId = db.Column(db.Integer,primary_key=True)
#     dateTime = db.Column(db.DateTime,primary_key=True)
#     budget = db.Column(db.Integer,nullable=False)
#     months = db.Column(db.Integer,nullable=False)
#     state = db.Column(db.String(20),nullable=False)
#     profit = db.Column(db.Integer,nullable=False)

#     # products = db.relationship('UserHistoryProducts', backref='user_history', lazy=True, cascade="all, delete-orphan")
#     products = db.relationship(
#         'userHistoryProducts',
#         backref='user_history',
#         lazy=True,
#         cascade="all, delete-orphan",
#         primaryjoin="and_(userHistory.userId == userHistoryProducts.userId, "
#                     "userHistory.dateTime == userHistoryProducts.dateTime)"
#     )


# class UserHistoryProducts(db.Model):
#     __tablename__ = 'userHistoryProducts'
#     userId = db.Column(db.Integer,primary_key=True)
#     dateTime = db.Column(db.DateTime,primary_key=True)
#     subcategory = db.Column(db.String(20),primary_key=True)
#     category = db.Column(db.String(20),nullable=False)
#     quantity = db.Column(db.Integer(),nullable=False)

#     user_history_id = db.Column(db.Integer, db.ForeignKey('UserHistory.userId'), nullable=False)
#     user_history_datetime = db.Column(db.DateTime, db.ForeignKey('UserHistory.dateTime'), nullable=False)
    

# Define a simple route for testing
@app.route('/')
def check():
    return "hello , welcome"

# Signup route for creating a new user
@app.route('/signup', methods=['POST','GET'])
def signup():
    try:
        data = request.json
        userName = data.get('userName')
        email = data.get('email')
        password = data.get('password')

        # Check if the email already exists
        existing_user = Credentials.query.filter_by(email=email).first()
        if existing_user:
            app.logger.debug(f"Email already in use: {email}")
            return jsonify({'message': 'Email already in use.'}), 400

        if len(password) < 6 or len(password) > 12:
            return jsonify({"message": "Password must be between 6 to 12 characters"}), 400

        if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$&])[A-Za-z\d@#$&]{6,}$', password):
            return jsonify({
                'message': 'Password must be at least 6 characters long, contain one uppercase letter, one lowercase letter, one number, and one special character (@, #, $, or &).'
            }), 400    
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        newUser = Credentials(userName=userName, email=email, password= hashed_password, date=datetime.now())
        # Add the new user to the database
        db.session.add(newUser)
        db.session.commit()
        user = Credentials.query.filter_by(email=email).first()

        # Return success response
        # app.logger.debug(f"New user created: {userName}, {email}")
        return jsonify({'message': 'User created successfully!','userId' : user.userId}), 200

    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        app.logger.error(f"Error during signup: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
    
# Route to handle login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    # Here we find user by email from database
    user = Credentials.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # User login successful
        # app.logger.info(f"User login: {user.userName}, {user.email}")
        return jsonify({"message": "Login successfully", "username": user.userName, "email": user.email,  "userId" : user.userId}), 200
    else:
        # Invalid credentials
        return jsonify({"message": "Invalid email or password"}), 400    

# Route to request password reset
@app.route('/forgotPassword', methods=['POST'])
def forgotPassword():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"message": "Email is required."}), 400

    # Generate a 6-digit verification code
    verificationCode = f"{random.randint(100000, 999999)}"

    # Save the verification code with a timestamp (valid for 10 minutes)
    verification_data[email] = {
        "code": verificationCode,
        "timestamp": time.time()
    }
    # Check if user exists
    user = Credentials.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404

    # Send email with reset link
    try:
        msg = Message("Your Password Reset Code - Team AlgroBiz", sender="testing6864@gmail.com", recipients=[email])
        # msg.body = '6 digit code : ' + str(verificationCode)
        msg.body = f"Your verification code is : {verificationCode}. This code is valid for 10 minutes."
        mail.send(msg)
        return jsonify({"message": "Password reset email sent"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to send email", "error": str(e)}), 500

@app.route('/verifyCode', methods=['POST'])
def verifyCode():
    data = request.get_json()
    email = data.get('email')
    code = data.get('verificationCode')

    if not email or not code:
        return jsonify({"message": "Email and verification code are required."}), 400

    # Check if the email exists in the verification data
    if email not in verification_data:
        return jsonify({"message": "Invalid email or verification code."}), 400

    stored_data = verification_data[email]
    stored_code = stored_data.get("code")
    timestamp = stored_data.get("timestamp")

    # Check if the code is valid and not expired (10 minutes)
    if stored_code == code and time.time() - timestamp <= 600:
        # Remove the code after successful verification
        del verification_data[email]
        return jsonify({"message": "Code verified successfully."}), 200
    else:
        return jsonify({"message": "Invalid or expired verification code."}), 400

# Route to reset the password
@app.route('/resetPassword', methods=['POST', 'GET'])
def resetPassword():
    data = request.json
    email = data.get('email')
    newPassword = data.get('newPassword')

    if not re.fullmatch(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$&])[A-Za-z\d@#$&]{6,}$', newPassword):
            return jsonify({
                'message': 'Password must be at least 6 characters long, contain one uppercase letter, one lowercase letter, one number, and one special character (@, #, $, or &).'
            }), 400

    # Find user by email and update password
    user = Credentials.query.filter_by(email = email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Hash the new password and update the user record
    hashedPassword = generate_password_hash(newPassword)
    user.password = hashedPassword
    db.session.commit()
    return jsonify({"message": "Password has been reset successfully"}), 200    

@app.route('/initForm', methods=['POST', 'GET'])
def initForm():
    try:
        userId = request.args.get('userId')
        # Get the JSON data from the request
        data = request.json
        companyName = data.get('companyName')
        state = data.get('state')
        prodCategories = data.get('prodCategories')  # Assuming this is a list or dictionary

        # if isinstance(prodCategories, list):
        prodCategories = ", ".join(prodCategories)    

        # Create a new CustomerInfo entry
        newCustomer = CustomerInfo(
            userId = userId,
            companyName = companyName,
            state = state,
            prodCategories = prodCategories
        )

        # Add the entry to the database
        db.session.add(newCustomer)
        db.session.commit()

        return jsonify({'message': 'Customer information added successfully!'}), 200

    except Exception as e:
        app.logger.error(f"Error adding customer: {str(e)}")
        return jsonify({'message': 'Failed to add customer information.'}), 500

def get_top_5_sales(cat_name, state):
    # Query to filter by catName and state, then order by sales in descending order
    top_5 = Check.query.filter_by(catName=cat_name, state=state).order_by(Check.sales.desc()).limit(5).all()
    
    # Return the top 5 results as a list of dictionaries
    result = []
    for item in top_5:
        result.append({
            'catName': item.catName,
            'itemName': item.itemName,
            'state': item.state,
            'sales': item.sales
        })
    
    return result

@app.route('/trends', methods = ['POST', 'GET'])
def trends():
    try:
        data = request.json
        state = data.get('state')
        catName = data.get('category')
        top_5_sales = get_top_5_sales(catName, state)

        return jsonify(top_5_sales), 200

    except Exception as e:
        app.logger.error(f"Error finding trend: {str(e)}")
        return jsonify({'message': 'Failed to find the top trending item.'}), 500

@app.route('/inventory/insert', methods = ['POST', 'GET'])
def inventoryInsert():
    try:
        userId = request.args.get('userId')
        data = request.json
        itemId = data.get('itemId')
        itemName = data.get('name')
        catName = data.get('category')
        quantity = data.get('quantity')
        costPrice = data.get('costPrice')
        sellingPrice = data.get('sellingPrice')

        newEntry = Inventory(userId = userId, itemId = itemId, itemName = itemName, quantity = quantity, catName = catName, costPrice = costPrice, sellingPrice = sellingPrice)
        db.session.add(newEntry)
        db.session.commit()

        return jsonify({'message' : 'Succefully entry added'}), 200

    except Exception as e:
        app.logger.error(f"Entry Didn't got inserted: {str(e)}")
        return jsonify({"message': 'Entry didn't got inserted."}), 500

@app.route('/products', methods=['GET', 'POST'])
def getProductsByCategory():
    category = request.args.get('category')
    userId = request.args.get('userId')
    if not category:
        return jsonify({"error": "Category is required"}), 400
    print(category)
    if category:
        products = Inventory.query.filter_by(userId = userId, catName=category).all()
        # for product in products:
        #     print(product)

        products_data = [
        {
            'itemId': product.itemId,
            'category': product.catName,
            'name': product.itemName,
            'quantity': product.quantity,
            'costPrice': product.costPrice,
            'sellingPrice': product.sellingPrice
        }
            for product in products
        ]
        # print(products_data)
        return jsonify(products_data), 200
    else:
        return jsonify({"error": "Category not specified"}), 400

@app.route('/inventory/delete', methods = ['POST', 'GET', 'DELETE'])
def inventoryDelete():
    try:
        itemId = request.args.get('itemId') 
        userId = request.args.get('userId')
        if not itemId:
            return jsonify({"error": "itemId is required"}), 400
        entry = Inventory.query.filter_by(userId = userId, itemId = itemId).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return jsonify({'message' : "entry deleted successfully"}), 200
        else:
            print(f"No entry found.")
    
    except Exception as e:
        app.logger.error(f"Entry didn't got deleted: {str(e)}")
        return jsonify({"message': 'Entry didn't got deleted."}), 500



@app.route('/inventory/modify', methods = ['POST', 'GET', 'PUT'])
def inventoryModify():
    try:
        userId = request.args.get('userId')
        data = request.json
        itemId = data.get('itemId')
        catName = data.get('category')
        itemName = data.get('name')
        quantity = data.get('quantity')
        costPrice = data.get('costPrice')
        sellingPrice = data.get('sellingPrice')

        entry = Inventory.query.filter_by(userId = userId, itemId = itemId).first()
        # print(entry)
        if entry:
            entry.itemName = itemName
            entry.catName = catName
            entry.quantity = quantity
            entry.costPrice = costPrice
            entry.sellingPrice = sellingPrice
            db.session.commit()
            return jsonify({'message' : "backend is ok"}), 200     
        else:
            print(f"No entry found.")
    
    except Exception as e:
        app.logger.error(f"Entry Didn't got modified: {str(e)}")
        return jsonify({"message': 'Entry didn't got modified."}), 500

@app.route('/profile', methods = ['POST', 'GET'])
def profile():
    try:
        userId = request.args.get('userId')

        entry1 = CustomerInfo.query.filter_by(userId = userId).first()
        entry2 = Credentials.query.filter_by(userId = userId).first()
        number = 9564656546
        city = 'Gandhinagar'
        categoryList = entry1.prodCategories.split(", ")
        if entry1 and entry2:
            return jsonify( {'userId' : userId, 'userName' : entry2.userName, 'userEmail' : entry2.email, 'mobileNumber' : number, 'companyName' : entry1.companyName, 'city' : city , 'state' : entry1.state , 'categoriesSold' : categoryList }), 200
        else:
            print(f"No entry found.")
    
    except Exception as e:
        app.logger.error(f"Cann't fetch user data : {str(e)}")
        return jsonify({"message': 'Cann't fetch user data."}), 500

@app.route('/editprofile', methods=['PUT'])
def editProfile():
    data = request.json
    userId = data.get('userId')
    entry1 = CustomerInfo.query.filter_by(userId = userId).first()
    entry2 = Credentials.query.filter_by(userId = userId).first()

    entry2.userName = data.get('userName')
    entry2.email = data.get('userEmail')
    entry1.mobileNumber = data.get('mobileNumber', entry1.mobileNumber)
    entry1.companyName = data.get('companyName')
    entry1.city = data.get('city', entry1.city)
    entry1.state = data.get('state')
    entry1.prodCategories = ", ".join(data.get('categoriesSold', []))  # Convert list to string

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile"}), 500

@app.route('/forecast', methods=['POST', 'GET'])
def forecast():
    try:    
        data = request.json
        state = data.get('state')
        catName = data.get('itemCategory')
        itemName = data.get('subCategory')
        months = data.get('months')
        prevSale = data.get('prevSale')

        # print(f"Forecast data received: state={state}, catName={catName}, itemName={itemName}, months={months}, prevSale={prevSale}")

        # Call the ML model prediction function
        predictedSale = sales_prediction(str(state), str(catName), str(itemName), int(months), int(prevSale))
        # print(f"Predicted sale: {predictedSale}")

        return jsonify({"predictedSale" : predictedSale}), 200
    
    except Exception as e:
        app.logger.error(f"Error in forecasting: {str(e)}")
        return jsonify({'message': 'Failed to forecast'}), 500
    
@app.route('/inventoryOptimization', methods = ['POST', 'GET'])
def inventoryOptimization():
    try:    
        data = request.json
        budget = data.get('budget')
        months = data.get('months')
        state = data.get('state')
        products = data.get('products')
        
        # print(products)
        max_profit, chosen_products = maxProfit(int(budget), len(products), str(state), int(months), products)
        # print(max_profit)
        # print(chosen_products)
        # product_list = []
        # for i in range(len(products)):
            # product_list.append(products[i]["subcategory"])
        quantity = []    
        for (item_index, qty) in chosen_products:
            # prod = str(product_list[item_index])
            quantity.append(qty)    
        
        return jsonify({"profit" : max_profit, "quantity" : quantity}), 200
    
    except Exception as e:
        app.logger.error(f"Error in inventoryoptimization : {str(e)}")
        return jsonify({'message': 'Error in inventoryoptimization.'}), 500

# @app.route('/saveInventoryOptimization/<userId>', methods=['POST'])
# def saveHistory(userId):
    
#     payload = request.get_json()

#     if payload == None:
#         return jsonify({'error' : 'No data provided'}),400
    
#     time = datetime.datetime.utcnow()
#     budget = payload.get('budget')
#     months = payload.get('months')
#     state = payload.get('state')
#     products = payload.get('products')
#     optimizedInventory = payload.get('optimizedInventory')

#     profit = optimizedInventory.get('profit')
#     quantities = optimizedInventory.get('quantities')

    
#     if(months > 12 or months < 1):
#         return jsonify({'error' : 'not a valid month'}),401
    
#     if(len(products) != len(quantities)):
#         return jsonify({'error' : 'invalid data handeled'}),402
    
#     dict = {}

#     for i in range(len(products)):
#         dict[products[i].get('subcategory')] = quantities[i],products[i].get('category')
    
#     dict=list(dict.items())

#     try: 
#         with db.session.begin():
#             db.session.add(UserHistory(userId = userId, profit = profit, budget = budget, months = months, state = state, datetime = time))

#             for tup in dict:
#                 db.session.add(UserHistoryProducts(userId = userId, datetime = time, quantity = tup[1][0], subcategory = tup[0], category = tup[1][1]))
    
#         db.sesssion.commit()
#     except Exception as e:
#         return jsonify({'error':'not able to commit to database'}),403
    
#     return jsonify({'message':'done!'}),200

# @app.route('/getInventoryOptimizations/<userId>', methods=['GET'])
# def getHistory(userId):
#     user_history_items = UserHistory.query.filter_by(userId=userId).all()
    

#     if not user_history_items:
#         return jsonify([])

#     user_history_data = [
#         {
#             'userId': item.userId,
#             'dateTime': item.dateTime.strftime('%Y-%m-%d %H:%M:%S'),  
#             'budget': item.budget,
#             'months': item.months,
#             'state': item.state,
#             'profit': item.profit
#         }
#         for item in user_history_items
#     ]

#     # Return the data as a JSON response
#     return jsonify(user_history_data), 200

# Main entry point to run the app
if __name__ == '__main__':
    app.run(debug=True)













































# @app.route('/signup', methods = ['GET','POST'])
# def signup():
#     if(request.method == 'POST'):
#         name = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')

#         # Check if username already exists
#         existing_user = Credentials.query.filter_by(username=name).first()
#         if existing_user:
#             flash('Username already taken. Please choose a different one.', 'error')
#             return render_template("signupPage.html")

#         # Check if password and confirm password match
#         if password != confirm_password:
#             flash('Passwords do not match.', 'error')
#             return render_template("signupPage.html")

#         # Add new user if validation passes
#         entry = Credentials(username = name,email = email,password = password,date = datetime.now())
#         db.session.add(entry)
#         db.session.commit()

#         return render_template("dashboard.html")
#     return render_template("signupPage.html")

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
    
#     # Check if user exists and password matches
#     user = Credentials.query.filter_by(username=username, password=password).first()

#     if user:
#         email = user.email
#         render_template("loginVerifyPage.html")
#         verification_code = random.randint(100000, 999999)
#         session['verificationCode'] = verification_code
#         mail.send_message('Verification code from AlgrowBiz ',
#                           sender=[params['gmail-user']],
#                           recipients = email ,
#                           body = "\n" + '6 digit code : ' + str(verification_code)
#                           )        
#     # if user:
#     #     # Login successful
#     #     return render_template("dashboard.html")
#     else:
#         # Login failed
#         flash('Invalid username or password', 'error')
#         return render_template("loginPage.html")

# @app.route('/verifyLogin', methods=['POST'])
# def verify():
#     temp = request.form.get('verificationCode')
#     if int(temp) == session.get('verificationCode'):
#         session.pop('verification_code', None)
#         return render_template("dashboard.html")
#     else:
#         # Code does not match
#         flash("Invalid code. Please try again.", "error")

# @app.route('/dashboard')
# def dashboard():
#     return render_template("dashboard.html")

# app.run(debug = True)    
