# pytest file for flask app endpoints
import os
import tempfile
import pytest
import app as my_app

@pytest.fixture
def client():
    # setup temporary sqlite db so it doesnt mess with real db
    db_file, db_path = tempfile.mkstemp()
    my_app.DB_NAME = db_path
    my_app.init_db()

    my_app.app.config["TESTING"] = True
    with my_app.app.test_client() as c:
        yield c

    os.close(db_file)
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_home_route(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"

def test_get_programs(client):
    res = client.get("/programs")
    assert res.status_code == 200
    progs = res.get_json()["programs"]
    assert "Fat Loss (FL)" in progs
    assert "Muscle Gain (MG)" in progs

def test_calc_calories_success(client):
    data = {"weight": 70, "program": "Fat Loss (FL)"}
    res = client.post("/calculate-calories", json=data)
    assert res.status_code == 200
    # 70 * 22 = 1540
    assert res.get_json()["daily_calories"] == 1540

def test_calc_calories_bad_program(client):
    data = {"weight": 70, "program": "Zumba"}
    res = client.post("/calculate-calories", json=data)
    assert res.status_code == 400

def test_save_and_fetch_client(client):
    payload = {
        "name": "Rohan",
        "age": 24,
        "weight": 75,
        "program": "Muscle Gain (MG)"
    }
    # save
    res = client.post("/clients", json=payload)
    assert res.status_code == 201
    
    # fetch
    res2 = client.get("/clients/Rohan")
    assert res2.status_code == 200
    assert res2.get_json()["name"] == "Rohan"
    assert res2.get_json()["calories"] == 75 * 35

def test_client_not_found(client):
    res = client.get("/clients/RandomGuy")
    assert res.status_code == 404

def test_log_adherence(client):
    payload = {
        "client_name": "Rohan",
        "week": "Week 1",
        "adherence": 80
    }
    res = client.post("/progress", json=payload)
    assert res.status_code == 201

def test_invalid_adherence_val(client):
    payload = {
        "client_name": "Rohan",
        "week": "Week 1",
        "adherence": 150
    }
    res = client.post("/progress", json=payload)
    assert res.status_code == 400
