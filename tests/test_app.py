import pytest
from app import create_app, db, User

@pytest.fixture()
def client():
    app=create_app({"TESTING":True,"SECRET_KEY":"test-secret","SQLALCHEMY_DATABASE_URI":"sqlite://","WTF_CSRF_ENABLED":False})
    with app.app_context():
        db.create_all()
        user=User(full_name="Test Admin",email="admin@test.local",role="admin")
        user.set_password("StrongPassword123!")
        db.session.add(user); db.session.commit()
    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()

def test_health(client):
    assert client.get("/health").json["status"]=="ok"

def test_login_dashboard(client):
    response=client.post("/login",data={"email":"admin@test.local","password":"StrongPassword123!"},follow_redirects=True)
    assert response.status_code==200
    assert b"Welcome, Test Admin" in response.data

def test_invalid_login(client):
    response=client.post("/login",data={"email":"admin@test.local","password":"wrong"})
    assert b"Invalid email or password" in response.data
