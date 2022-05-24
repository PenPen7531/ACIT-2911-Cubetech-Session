from models.employee import Employee
import pytest
import webapp
from flask import session

@pytest.fixture
def client():
    # Creates the test environment

    client = webapp.app.test_client()

    with client.session_transaction(subdomain="blue") as session:
        # assume that a user is signed in
        session["user"] = "test_admin"
        session["db"]= "test_db"

    return client

@pytest.fixture
def invalid_client():
    # Creates the test environment

    invalid_client = webapp.app.test_client()

    with invalid_client.session_transaction(subdomain="blue") as session:
        # assume that a user is signed in
        session["user"] = None
        session["db"]= None

    return invalid_client

def login(client, username, password):
    return client.post('/', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def search_home(client, dep, fname):
    return client.post('/view', data=dict(
        department=dep,
        first_name=fname
    ), follow_redirects=True)

def department_search(client, dep, fname):
    return client.post('/department/Accounting', data=dict(
        department=dep,
        first_name=fname
    ), follow_redirects=True)

def add_employee(client):
    return client.post('/create', data=dict(
        first_name="Jeff",
        last_name="Wang",
        employee_id="A01", 
        employee_department="Accounting",
        employee_salary=25000,
        employee_age=23,
        employee_phone="604-464-3393",
        employee_email="jack@gmail.com",
        employee_address="2555 Test Me",
        employee_gender="IDK",
        date_hired="June 6, 1944"
    ), follow_redirects=True)

def delete_db(client, username, password, db):
    return client.post('/confirm', data=dict(
        username=username,
        password=password,
        database_name=db
    ), follow_redirects=True)

def edit_employee(client):
    return client.post('/edit/A01', data=dict(
        first_name="Jack",
        last_name="Mac",
        employee_id="A02", 
        employee_department="Sales",
        employee_salary=250500,
        employee_age=24,
        employee_phone="604-464-3393",
        employee_email="jack@gmail.com",
        employee_address="2555 Test Me",
        employee_gender="IDK",
        date_hired="June 6, 1944"
    ), follow_redirects=True)

def test_invalid_create(client):
    assert add_employee(client).status_code==201

def name_search(client, dep, fname):
    return client.post('/fname/Barker', data=dict(
        department=dep,
        first_name=fname
    ), follow_redirects=True)
def dep_name_search(client, dep, fname):
    return client.post('/search/Barker/Accounting', data=dict(
        department=dep,
        first_name=fname
    ), follow_redirects=True)

def add_db(client, username, password, db):
    return client.post('/createAdmin', data=dict(
        username=username,
        password=password,
        database_name=db
    ), follow_redirects=True)

def test_invalid_view(invalid_client):
    assert invalid_client.get("/view").status_code==200

def test_homepage(client):
    """checks that the homepage is working"""
    assert client.get("/").status_code == 201

def test_view(client):
    assert client.get("/view").status_code==201

def test_invalid_login(client):
    login(client, "Not_Valid", "Invalid").status_code==404

def test_valid_login(client):
    login(client, "test_admin", "test_password").status_code==201

def test_home_search(client):
    assert search_home(client, "Accounting", "Test_User").status_code==200
    assert search_home(client, None, "Test_User").status_code==200
    assert search_home(client, "Accounting", None).status_code==200

def test_invalid_employee_view(invalid_client):
    assert invalid_client.get("/view/62689cd551816cb3fcde6a55").status_code==200



def test_invalid_create_page(invalid_client):
    assert invalid_client.get("/create").status_code==201

def test_valid_create_get(client):
    assert client.get("/create").status_code==200

def test_add_employee(client):
    assert add_employee(client).status_code==404

def test_valid_employee_view(client):
    assert client.get("/view/A01").status_code==200

def test_edit_page(client):
    assert client.get("/edit/A01").status_code==200

def test_edit_employee(client):
    assert edit_employee(client).status_code==200

def test_invalid_edit(invalid_client):
    assert invalid_client.get("/edit/A01").status_code==200

def test_delete_employee(client):
    assert client.get("/delete/A02").status_code==302

def test_invalid_delete_emp(client):
    assert client.get("/delete/A79").status_code==404

def test_invalid_delete_no_creds(invalid_client):
    assert invalid_client.get("/delete/A01").status_code==200

def test_search_from_department(client):
    assert department_search(client, "Test", "Test").status_code==200
    assert department_search(client, None, "Test").status_code==200
    assert department_search(client, "Test", None).status_code==200

def test_invalid_search_from_dep(invalid_client):
    assert invalid_client.get("/department/A01").status_code==200

def test_search_from_name(client):
    assert name_search(client, "Test", "Test").status_code==200
    assert name_search(client, "Test", None).status_code==200
    assert name_search(client, None, "Test").status_code==200

def test_invalid_search_from_name(invalid_client):
    assert invalid_client.get("/fname/Jack").status_code==200

def test_search_from_name_dep(client):
    assert dep_name_search(client, "Test", "Test").status_code==200
    assert dep_name_search(client, "Test", None).status_code==200
    assert dep_name_search(client, None, "Test").status_code==200

def test_invalid_search_from_name_dep(invalid_client):
    assert invalid_client.get("/search/BadDep/BadName").status_code==200

def test_logout(client):
    assert client.get("/logout").status_code==302

def test_add_admin_page(client):
    assert client.get("/createAdmin").status_code==200

def test_add_admin(client):
    assert add_db(client, "test_admin", "test_password", "test_db").status_code==201

def test_invalid_add_admin(client):
    assert add_db(client, "admin", "new_pass", "new_db").status_code==200
    assert add_db(client, "new_user", "new_password", "bcit").status_code==200

def test_delete_db_page(client):
    assert client.get("/confirm").status_code==200

def test_delete_db(client):
    assert login(client, "test_admin", "test_password").status_code==201
    assert delete_db(client, "test_admin", "test_password", "test_db").status_code==201

def test_invalid_delete_db(client):
    assert delete_db(client,"not_admin", "not_password", "not_db").status_code==201

def test_view_logs(client):
    assert client.get("/viewlogs").status_code==200

def test_view_invalid_logs(invalid_client):
    assert invalid_client.get("/viewlogs").status_code==200

