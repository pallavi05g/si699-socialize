from flask import Flask, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from sqlalchemy import *
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '<enter app id>',
        'secret': '<enter secret key>'
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
    
@lm.user_loader
def load_user(id):
    return login_info.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
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
    return redirect(url_for('index'))

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
