

from flask import Flask, request, jsonify, render_template, redirect, session

import os
from models.company import Company
from models.data import Data
from models.employee import Employee
from models.admin import Admin
from models.login import Login
from models.crypto import Crypto
from models.logs import Logs
from models.data import Data
from datetime import date, datetime
from pytz import timezone
import pytz

app = Flask(__name__)
app.secret_key="Secretasdasdasdads"
# Constant variable. Python will always make sure when the application start this is always false

user = Login()
# Home page. Used to log in into a specific account based on the username
COMPANY=False

@app.route("/", methods=["GET", "POST"])
def login():
    user = Login()
    # If the request method is GET. Sends the webpage to the client
    if request.method == "GET":
        return render_template("login.html"), 201

    # If the request method is POST. It will take the inputted data from the html form and check to see if the user is in the database
    if request.method == "POST":
        

        # Grabs the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password")

        # Check to see if the username and password matches from the logins.json file
        # See login.py to see how the function bellow works
        authenicate = user.login_authenticate(username, password)

        # If the function returns true
        if authenicate:
            session["user"]=username

            # Find the user data by the username.
            # Check login.py
            user_data = user.find_login_by_username(username)
            session["db"]=user_data.database
            # Creates another global variable. Allows all functions to use this variable. Makes the scope to the entire file
           

            # The company is now the user database
            # The database name is used to find the companies database related to that name
            COMPANY = Company(session["db"])
            LOGS=Logs(session["db"])
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}","Access Data")
            LOGS.add(action)
            LOGS.save()
            
            return redirect("/view")

        return render_template("exist.html"), 404
    


@app.route("/view", methods=["GET", "POST"])
def homepage():

    if session["user"] != None:
        COMPANY=Company(session["db"])
        if request.method == "GET":
            return render_template("home.html", company=COMPANY), 201
        if request.method == "POST":
            fname=request.form.get("first_name")
            department = request.form.get("department")
            LOGS=Logs(COMPANY.name)
            if fname=="" or fname==None:
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by deptartment: {department}")
                LOGS.add(action)
                LOGS.save()
                return redirect("/department/"+department)
            if department=="" or department==None:
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname}")
                LOGS.add(action)
                LOGS.save()
                return redirect("/fname/"+fname), 302
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname} and department: {department}")
            LOGS.add(action)
            LOGS.save()
            return redirect(f"/search/{fname}/{department}")
    return render_template("signin_error.html")
    


@app.route("/view/<employee_id>")
def view(employee_id):
    
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        employee = COMPANY.find_employee_by_id(employee_id)
        if employee != None:
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"View employee: {employee_id}")
            LOGS.add(action)
            LOGS.save()
            return render_template("view.html", employee=employee, company=COMPANY), 200

    return render_template("signin_error.html")


@app.route("/create", methods=["GET", "POST"])
def create_page():
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        if request.method == "GET":
            return render_template("create.html")

        if request.method == "POST":
            employee_fname = request.form.get("first_name")
            employee_lname = request.form.get("last_name")
            employee_id = request.form.get("employee_id")
            employee_department = request.form.get("employee_department")
            employee_salary = request.form.get("employee_salary")
            employee_age = request.form.get("employee_age")
            employee_email = request.form.get("employee_email")
            employee_phone = request.form.get("employee_phone")
            employee_address = request.form.get("employee_address")
            employee_gender = request.form.get("employee_gender")
            date_hired = request.form.get("date_hired")

            if COMPANY.check_ID(employee_id):
                new_emp = Employee(employee_fname, employee_lname, employee_id,
                                   employee_department, int(employee_salary), int(employee_age), employee_email, employee_phone, employee_address, employee_gender, date_hired)
                COMPANY.add(new_emp)
                COMPANY.save()
                today = date.today()
                time = datetime.now()
                action = Data(today.strftime(
                    "%b-%d-%Y"), f"{time.hour}:{time.minute}", f"Created Employee: {employee_fname}")
                LOGS.add(action)
                LOGS.save()
                return redirect("/view"), 302
            return "This ID is already taken", 404
    else:
        return render_template("signin_error.html"), 201


@app.route("/delete/<employee_id>")
def delete(employee_id):
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        if COMPANY.delete(employee_id):
            COMPANY.save()
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Deleted Employee: {employee_id}")
            LOGS.add(action)
            LOGS.save()
            return redirect("/view")
        elif COMPANY.delete(employee_id) == False:
            return "Unsucessful", 404

    return render_template("signin_error.html")

  

@app.route("/edit/<employee_id>", methods=["GET", "POST"])
def put_user(employee_id):

    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        emp = COMPANY.find_employee_by_id(employee_id)
        if request.method == "GET":
            return render_template("edit.html", emp=emp)
        if request.method == "POST":
            emp_fname = request.form.get("first_name")
            emp_lname = request.form.get("last_name")
            emp_id = request.form.get("employee_id")
            emp_department = request.form.get("employee_department")
            emp_salary = request.form.get("employee_salary")
            emp_age = request.form.get("employee_age")
            emp_email = request.form.get("employee_email")
            emp_phone = request.form.get("employee_phone")
            emp_address = request.form.get("employee_address")
            emp_gender = request.form.get("employee_gender")
            emp_hired = request.form.get("date_hired")

            if emp.first_name != emp_fname:
                emp.first_name = emp_fname
            if emp.last_name != emp_lname:
                emp.last_name = emp_lname
            if emp.employee_id != emp_id:
                emp.employee_id = emp_id
            if emp.employee_department != emp_department:
                emp.employee_department = emp_department
            if emp.employee_salary != emp_salary:
                emp.employee_salary = int(emp_salary)
            if emp.employee_age != emp_age:
                emp.employee_age = int(emp_age)
            if emp.employee_email != emp_email:
                emp.employee_email = emp_email
            if emp.employee_phone != emp_phone:
                emp.employee_phone = emp_phone
            if emp.employee_address != emp_address:
                emp.employee_address = emp_address
            if emp.employee_gender != emp_gender:
                emp.employee_gender = emp_gender
            if emp.date_hired != emp_hired:
                emp.date_hired = emp_hired
            COMPANY.save()
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Edit Employee: {employee_id}")      
            LOGS.add(action)
            LOGS.save()
            return render_template("view.html", employee=emp, company=COMPANY)

    return render_template("signin_error.html")


@app.route("/department/<employee_department>", methods=["GET", "POST"])
def show_department(employee_department):
    
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        if request.method == "GET":
            department = COMPANY.find_employees_by_department(employee_department)
            return render_template("department.html", department=department)
        if request.method == "POST":
                fname=request.form.get("first_name")
                department = request.form.get("department")
                if fname=="" or fname==None:
                    today=date.today()
                    time=datetime.now(tz=pytz.utc)
                    time=time.astimezone(timezone('US/Pacific'))
                    action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by deptartment: {department}")
                    LOGS.add(action)
                    LOGS.save()
                    return redirect("/department/"+department)
                if department=="" or department==None:
                    today=date.today()
                    time=datetime.now(tz=pytz.utc)
                    time=time.astimezone(timezone('US/Pacific'))
                    action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname}")
                    LOGS.add(action)
                    LOGS.save()
                    return redirect("/fname/"+fname)
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname} and department: {department}")
                LOGS.add(action)
                LOGS.save()
                return redirect(f"/search/{fname}/{department}")
    return render_template("signin_error.html")

@app.route("/fname/<employee_firstname>", methods=["GET", "POST"])
def show_firstname(employee_firstname):
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        if request.method == "GET":
            employees = COMPANY.find_employees_by_fname(employee_firstname)
            return render_template("department.html", department=employees)
        if request.method == "POST":
            fname=request.form.get("first_name")
            department = request.form.get("department")
            if fname=="" or fname==None:
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by deptartment: {department}")
                LOGS.add(action)
                LOGS.save()
                return redirect("/department/"+department)
            if department=="" or department==None:
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname}")
                LOGS.add(action)
                LOGS.save()
                return redirect("/fname/"+fname)
            today=date.today()
            time=datetime.now(tz=pytz.utc)
            time=time.astimezone(timezone('US/Pacific'))
            action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname} and department: {department}")
            LOGS.add(action)
            LOGS.save()
            return redirect(f"/search/{fname}/{department}")
    return render_template("signin_error.html")
   


@app.route("/search/<employee_firstname>/<employee_department>", methods=["GET", "POST"])
def show_dept_and_name(employee_firstname, employee_department):
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        if request.method == "GET":
            employees = COMPANY.find_employee_by_fname_department(employee_firstname, employee_department)
            return render_template("department.html", department=employees)
        if request.method == "POST":
                fname=request.form.get("first_name")
                department = request.form.get("department")
                if fname=="" or fname==None:
                    today=date.today()
                    time=datetime.now(tz=pytz.utc)
                    time=time.astimezone(timezone('US/Pacific'))
                    action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by deptartment: {department}")
                    LOGS.add(action)
                    LOGS.save()
                    return redirect("/department/"+department)
                if department=="" or department==None:
                    today=date.today()
                    time=datetime.now(tz=pytz.utc)
                    time=time.astimezone(timezone('US/Pacific'))
                    action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname}")
                    LOGS.add(action)
                    LOGS.save()
                    return redirect("/fname/"+fname)
                today=date.today()
                time=datetime.now(tz=pytz.utc)
                time=time.astimezone(timezone('US/Pacific'))
                action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Filter data by name: {fname} and department: {department}")
                LOGS.add(action)
                LOGS.save()
                return redirect(f"/search/{fname}/{department}")
    return render_template("signin_error.html")


@app.route("/logout", methods=["GET"])
def logout():
    COMPANY=Company(session["db"])
    LOGS=Logs(COMPANY.name)
    today=date.today()
    time=datetime.now(tz=pytz.utc)
    time=time.astimezone(timezone('US/Pacific'))
    action=Data(today.strftime("%b-%d-%Y"),f"{time.hour}:{time.minute}",f"Logout")
    LOGS.add(action)
    LOGS.save()
    session.clear()
    return redirect("/")
  




@app.route("/createAdmin", methods=["GET", "POST"])
def create_admin():
    if request.method == "GET":
        return render_template("createAdmin.html")

    if request.method == "POST":
        admin_username = request.form.get("username")
        admin_password = request.form.get("password")
        admin_database = request.form.get("database_name")
        enc_password = Crypto.enc_pass(admin_password)
        new_admin = Admin(admin_username, enc_password, admin_database)
        users = Login()
        new_user = users.find_login_by_username(admin_username)
        if new_user != None:
            return render_template("createerror.html")
        check_database_name = users.check_database_name(admin_database)
        if check_database_name:
            return render_template("createerror.html")
        users.add_login(new_admin)
        users.save()
        new_company = Company(new_admin.database)
        new_company.save()
        return redirect("/")    
    

@app.route("/confirm", methods=["GET", "POST"])
def delete_admin():
    if request.method == "GET":
        return render_template("delete_admin.html"), 200
    if request.method == "POST":
        admin_username = request.form.get("username")
        admin_password = request.form.get("password")
        admin_database = request.form.get("database")
        user = Login()
        authenicate = user.login_authenticate(admin_username, admin_password)
        if authenicate:
            user.delete_admin(admin_username)
            user.save()
            return redirect("/")
       
    return redirect("/")
    
@app.route("/viewlogs", methods=["GET"])
def get_logs():
    if session["user"] != None:
        COMPANY=Company(session["db"])
        LOGS=Logs(COMPANY.name)
        return render_template("logs.html", data=LOGS), 200
    return render_template("signin_error.html")


if __name__ == "__main__":
    app.run(debug=True)