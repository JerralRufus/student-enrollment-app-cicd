# tests/test_app.py
import pytest
from student_enrollment_app.main import create_app
from student_enrollment_app.database import db, Student, Course, Enrollment

@pytest.fixture
def app():
    # Use an in-memory SQLite database for testing
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        # Add test data
        s1 = Student(name="TestStudent")
        c1 = Course(name="TestCourse")
        db.session.add_all([s1, c1])
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Student Course Enrollment System" in response.data

def test_enroll_student(client):
    """Test enrolling a student in a course."""
    student = Student.query.filter_by(name="TestStudent").first()
    course = Course.query.filter_by(name="TestCourse").first()
    
    response = client.post('/enroll', data={
        'student_id': student.id,
        'course_id': course.id
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    
    # Verify enrollment in DB
    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    assert enrollment is not None
