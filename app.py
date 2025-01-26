from flask import Flask, render_template, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = "my secret key 18910paloma"
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    sets = db.relationship('Set', backref='user', lazy=True)
    quizzes = db.relationship('Quiz', backref='user', lazy=True)
    notes = db.relationship('Noted', backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username

class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tm = db.Column(db.String(80), nullable=True)  # Term
    df = db.Column(db.String(200), nullable=True)  # Definition
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qe = db.Column(db.String(200), nullable=False)
    an = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Noted(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()  # Ensure the tables are created
    # Check if the user already exists
    if not User.query.filter_by(email='john@example.com').first():
        user = User(username='john', email='john@example.com', password='defaultpassword')
        db.session.add(user)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('welcome', user_id=user.id))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not User.query.filter_by(email=email).first():
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('welcome', user_id=user.id))
        else:
            return "User already exists!"
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/welcome/<int:user_id>')
@login_required
def welcome(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('welcome.html', username=user.username)
    else:
        return "User not found"

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/studysetcreator', methods=['GET', 'POST'])
@login_required
def studysetcreator():
    if request.method == 'POST':
        terms = request.form.getlist('term')
        definitions = request.form.getlist('definition')
        if terms and definitions:
            for term, definition in zip(terms, definitions):
                new_set = Set(tm=term, df=definition, user_id=current_user.id)
                db.session.add(new_set)
            db.session.commit()
            sets = Set.query.filter_by(user_id=current_user.id).all()
            print(f"Current user ID: {current_user.id}, Sets: {sets}")  # Debugging line
            return render_template('studysetdisplay.html', sets=sets)
    return render_template('studyset.html')

@app.route('/notecreator', methods=['GET', 'POST'])
@login_required
def notecreator():
    if request.method == 'POST':
        notes = request.form.getlist('note')
        if notes:
            for note in notes:
                new_note = Noted(no=note, user_id=current_user.id)
                db.session.add(new_note)
            db.session.commit()
            return render_template('notedisplay.html', notes=Noted.query.filter_by(user_id=current_user.id).all())
        else:
            return "No text provided", 400
    
    return render_template('note.html')

@app.route('/quizcreator', methods=['GET', 'POST'])
@login_required
def quizcreator():
    if request.method == 'POST':
        questions = request.form.getlist('question')
        answers = request.form.getlist('answer')
        if questions and answers:
            for question, answer in zip(questions, answers):
                new_quiz = Quiz(qe=question, an=answer, user_id=current_user.id)
                db.session.add(new_quiz)
            db.session.commit()
            quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
            return render_template('quizdisplay.html', quizzes=quizzes)
        else:
            return "No text provided", 400
    return render_template('quiz.html')

@app.route('/studysetdisplay')
@login_required
def studysetdisplay():
    sets = Set.query.filter_by(user_id=current_user.id).all()
    return render_template('studysetdisplay.html', sets=sets)

@app.route('/quizdisplay')
@login_required
def quizdisplay():
    quizzes = Quiz.query.filter_by(user_id=current_user.id).all()
    return render_template('quizdisplay.html', quizzes=quizzes)

@app.route('/notedisplay')
@login_required
def notedisplay():
    return render_template('notedisplay.html', notes=Noted.query.filter_by(user_id=current_user.id).all())



if __name__ == '__main__':
    app.run(debug=True)

