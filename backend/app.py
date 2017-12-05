from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from sqlalchemy import *
from sqlalchemy.orm import relationship
from flask_wtf import Form
from wtforms import *
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '',
        'secret': ''
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)

lm.login_view = 'index'

class login_info(UserMixin, db.Model):
    __tablename__ = 'login_info'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

    profiles = relationship('Person', backref='Person.person_id',primaryjoin='login_info.id==Person.person_id', lazy='dynamic')

class CreateForm(Form):
    title = StringField('title', validators=[DataRequired()])
    location = StringField('location', validators=[DataRequired()])
    dfrom = StringField('date_from', validators[DataRequired()])
    tfrom = DateTimeField('time_from', validators[DataRequired()], format='%m-%d-%Y')
    dto = DateField('date_to', validators[DataRequired()], format='%m-%d-%Y')
    tto = DateTimeField('time_to', validators[DataRequired()], format='%m-%d-%Y')


@lm.user_loader
def load_user(id):
    return login_info.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html',pagetitle='Socialaza',)

@app.route('/home')
def home():
    return render_template('home.html',pagetitle='Ann Arbor',)

@app.route('/activitydetail')
def activitydetail():
    return render_template('activitydetail.html', pagetitle='Activity Detail',)

@app.route('/messages')
def messages():
    return render_template('messages.html', pagetitle='Messages',)

@app.route('/search')
def search():
    return render_template('search.html', pagetitle='Search',)

@app.route('/notifications')
def notifications():
    return render_template('notifications.html',pagetitle='Notifications',)

@app.route('/editprofile')
def editprofile():
    return render_template('editprofile.html', pagetitle='Edit Profile',)

@app.route('/profile')
def profile():
    return render_template('profile.html', pagetitle='My Profile',)

@app.route('/interested')
def interested():
    return render_template('interested.html', pagetitle='Interested',)

@app.route('/history')
def history():
    return render_template('history.html', pagetitle='History',)

@app.route('/settings')
def settings():
    return render_template('settings.html', pagetitle='Settings',)

@app.route('/create', methods=['GET','POST'])
def create():
    form = CreateForm()
    return render_template('create-test.html', pagetitle='Create Activity', form=form)

@app.route('/createpreview')
def createpreview():
    return render_template('createpreview.html', pagetitle='Activity Preview',)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = login_info.query.filter_by(social_id=social_id).first()
    if not user:
        user = login_info(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('home'))

class Badge(db.Model):
    __tablename__ = 'badge'
    b_id = db.Column(db.Integer, primary_key=True)
    b_name = db.Column(db.String(64), nullable=False, unique=True)
    b_imgpath = db.Column(db.String(256), nullable=True)
    u_id = db.Column(db.String(256), ForeignKey(login_info.id),nullable=True)

class Activity(db.Model):
    __tablename__ = 'activity'
    act_id = db.Column(db.Integer, primary_key=True)
    act_name = db.Column(db.String(64), nullable=False, unique=True)
    act_color = db.Column(db.String(64), nullable=False, unique=True)
    act_imgpath = db.Column(db.String(256), nullable=True)

class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, primary_key=True)
    card_activity_type = db.Column(db.String(64), nullable=False, unique=True)
    card_title = db.Column(db.String(64), nullable=False)
    card_location = db.Column(db.String(64), nullable=False)
    card_date_from = db.Column(db.String(64), nullable=False)
    card_time_from = db.Column(db.String(64), nullable=False)
    card_date_to = db.Column(db.String(64), nullable=False)
    card_time_to = db.Column(db.String(64), nullable=False)
    card_people_count = db.Column(db.Integer, nullable=False)
    card_valid_date = db.Column(db.String(64), nullable=False)
    card_valid_time = db.Column(db.String(64), nullable=False)
    card_host_id = db.Column(db.String(64), nullable=False)
    card_imgpath = db.Column(db.String(256), nullable=True)
    isHost = db.Column(db.Boolean, default=False, nullable=False)
    isFavorite = db.Column(db.Boolean, default=False, nullable=False)
    isImageSet = db.Column(db.Boolean, default=False, nullable=False)

class Person(db.Model):
    __tablename__ = 'person'
    unique_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, ForeignKey(login_info.id) ,unique=True)
    person_name = db.Column(db.String(64), nullable=False)
    person_dob = db.Column(db.String(64), nullable=False)
    person_location = db.Column(db.String(64), nullable=False)
    person_imgpath = db.Column(db.String(256), nullable=True)
    person_badges = db.Column(db.String(256), nullable=True)
    person_interests = db.Column(db.String(256),nullable=False)
    isDoBHidden = db.Column(db.Boolean, default=False, nullable=False)

    login_info = relationship('login_info', foreign_keys='Person.person_id')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
