# student_enrollment_app/main.py
from flask import Flask, request, jsonify, render_template
from .database import db, Student, Course, Enrollment
from . import metrics
import os
import logging # <--- ADD THIS

# ADD THIS BLOCK: Configure logging to output to the console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Configure the database
    # Get the absolute path for the instance folder
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'enrollment.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # --- THIS IS THE CORRECTED SECTION ---
    # The modern way to initialize the database within the app factory
    with app.app_context():
        db.create_all()
        # Add some initial data if the DB is empty
        if not Course.query.first():
            courses = ['Math 101', 'History 202', 'Physics 301', 'Chemistry 101']
            for course_name in courses:
                db.session.add(Course(name=course_name))
            students = ['Alice', 'Bob', 'Charlie']
            for student_name in students:
                db.session.add(Student(name=student_name))
            db.session.commit()
            print("Database initialized and seeded.")
    # --- END OF CORRECTION ---

    @app.route('/')
    def index():
        metrics.send_metric('views.index', 1) # Metric for home page views
        courses = Course.query.all()
        students = Student.query.all()
        return render_template('index.html', courses=courses, students=students)

    @app.route('/enroll', methods=['POST'])
    def enroll():
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        
        existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing_enrollment:
            return jsonify({'status': 'error', 'message': 'Student already enrolled in this course.'}), 409

        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        
        metrics.send_metric('enrollments.success', 1) # Metric for successful enrollments
        return jsonify({'status': 'success', 'message': 'Enrolled successfully!'})

    @app.route('/drop', methods=['POST'])
    def drop():
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return jsonify({'status': 'error', 'message': 'Enrollment not found.'}), 404

        db.session.delete(enrollment)
        db.session.commit()
        
        metrics.send_metric('enrollments.dropped', 1) # Metric for dropped courses
        return jsonify({'status': 'success', 'message': 'Dropped course successfully!'})

    @app.route('/course/<int:course_id>/students')
    def course_students(course_id):
        course = Course.query.get_or_404(course_id)
        enrollments = Enrollment.query.filter_by(course_id=course_id).all()
        student_list = [e.student.name for e in enrollments]
        
        metrics.send_metric(f'views.course_details', 1)
        return jsonify({'course': course.name, 'students': student_list})

    return app

# This is for running locally for development
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
