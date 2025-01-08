from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

with app.app_context():
    db.create_all()  # Ensure the tables are created
    # Check if the user already exists
    if not User.query.filter_by(email='john@example.com').first():
        user = User(username='john', email='john@example.com')
        db.session.add(user)
        db.session.commit()

    users = User.query.all()
    for user in users:
        print(user)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        username = request.form['username']
        password = request.form['password']
        # Add your authentication logic here
        return redirect(url_for('homepage'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/welcome/<int:user_id>')
def welcome(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('welcome.html', username=user.name)
    else:
        return "User not found"


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

