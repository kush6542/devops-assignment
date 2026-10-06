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

def test_home_reports_version(client):
    res = client.get("/")
    assert res.get_json()["app"] == "ACEest Fitness Management"
    assert "version" in res.get_json()

def test_programs_have_workout_and_diet(client):
    progs = client.get("/programs").get_json()["programs"]
    assert "Beginner (BG)" in progs
    for details in progs.values():
        assert details["factor"] > 0
        assert details["workout"]
        assert details["diet"]

@pytest.mark.parametrize("program, factor", [
    ("Fat Loss (FL)", 22),
    ("Muscle Gain (MG)", 35),
    ("Beginner (BG)", 26),
])
def test_calc_calories_each_program(client, program, factor):
    res = client.post("/calculate-calories", json={"weight": 80, "program": program})
    assert res.status_code == 200
    assert res.get_json()["daily_calories"] == 80 * factor

def test_calc_calories_accepts_numeric_string(client):
    res = client.post("/calculate-calories", json={"weight": "60.5", "program": "Beginner (BG)"})
    assert res.status_code == 200
    assert res.get_json()["daily_calories"] == int(60.5 * 26)

@pytest.mark.parametrize("payload", [
    {},
    {"program": "Fat Loss (FL)"},
    {"weight": 70},
    {"weight": "abc", "program": "Fat Loss (FL)"},
    {"weight": 0, "program": "Fat Loss (FL)"},
    {"weight": -5, "program": "Fat Loss (FL)"},
])
def test_calc_calories_invalid_input(client, payload):
    res = client.post("/calculate-calories", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()

def test_add_client_without_weight(client):
    res = client.post("/clients", json={"name": "Asha", "program": "Beginner (BG)"})
    assert res.status_code == 201
    assert client.get("/clients/Asha").get_json()["calories"] is None

def test_add_client_updates_existing(client):
    client.post("/clients", json={"name": "Vikram", "weight": 70, "program": "Fat Loss (FL)"})
    res = client.post("/clients", json={"name": "Vikram", "weight": 80, "program": "Muscle Gain (MG)"})
    assert res.status_code == 201
    saved = client.get("/clients/Vikram").get_json()
    assert saved["program"] == "Muscle Gain (MG)"
    assert saved["calories"] == 80 * 35

@pytest.mark.parametrize("payload", [
    {"program": "Fat Loss (FL)"},
    {"name": "   ", "program": "Fat Loss (FL)"},
    {"name": "Meena"},
    {"name": "Meena", "program": "Yoga"},
    {"name": "Meena", "program": "Fat Loss (FL)", "weight": "heavy"},
])
def test_add_client_invalid_input(client, payload):
    res = client.post("/clients", json=payload)
    assert res.status_code == 400

@pytest.mark.parametrize("adherence", [0, 100])
def test_log_adherence_boundaries(client, adherence):
    res = client.post("/progress", json={"client_name": "Rohan", "week": "Week 2", "adherence": adherence})
    assert res.status_code == 201
    assert res.get_json()["adherence"] == adherence

@pytest.mark.parametrize("payload", [
    {"week": "Week 1", "adherence": 50},
    {"client_name": "Rohan", "adherence": 50},
    {"client_name": "Rohan", "week": "Week 1"},
    {"client_name": "Rohan", "week": "Week 1", "adherence": -1},
    {"client_name": "Rohan", "week": "Week 1", "adherence": "high"},
])
def test_log_adherence_invalid_input(client, payload):
    res = client.post("/progress", json=payload)
    assert res.status_code == 400
