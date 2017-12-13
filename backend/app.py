from __future__ import print_function
from flask import Flask, redirect, url_for, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from oauth import OAuthSignIn
from sqlalchemy import *
from sqlalchemy.orm import relationship
from flask_wtf import Form
from wtforms import StringField,SelectField,DateField,DateTimeField
from wtforms.validators import DataRequired
from random import randint
import sqlite3
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
   'facebook': {
        'id': '1874301032583415',
        'secret': 'b9bcd6f1e730bb2f16462f224669b61e'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)

lm.login_view = 'index'

conn = sqlite3.connect('db1.sqlite')
print("Opened database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS profiledata (name TEXT, dob TEXT, location TEXT, interests TEXT)')
print("Table created successfully")

conn.close()

class login_info(UserMixin, db.Model):
    __tablename__ = 'login_info'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

    profiles = relationship('Person', backref='Person.person_id',primaryjoin='login_info.id==Person.person_id', lazy='dynamic')

class CreateCard(Form):
    activity_type = SelectField('activity_type', validators=[], choices=[('choose','Choose Activity Type'),('tour','Local Tours'),('adv','Adventure'),('food','Food'),('camping','Camping'),('trekking','Trekking'),('movie','Movies/Plays')], default=1)
    title = StringField('title', validators=[], render_kw={"placeholder": "Add Title"})
    location = StringField('location', validators=[], render_kw={"placeholder": "Add Location"})
    date_from = StringField('date_from', validators=[], render_kw={"placeholder": "mm/dd/yyyy"})
    time_from = StringField('time_from', validators=[],  render_kw={"placeholder": "hh/mm am/pm"})
    date_to = StringField('date_to', validators=[], render_kw={"placeholder": "mm/dd/yyyy"})
    time_to = StringField('time_to', validators=[], render_kw={"placeholder": "hh/mm am/pm"})
    people_count = StringField('people_count', validators=[], render_kw={"placeholder": "Enter Number of People"})
    valid_date = StringField('valid_date', validators=[], render_kw={"placeholder": "mm/dd/yyyy"})
    valid_time = StringField('valid_time', validators=[], render_kw={"placeholder": "hh:mm am/pm"})

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
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_activity_type = db.Column(db.String(64), nullable=False)
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

    def __init__(self, card_activity_type, card_title, card_location, card_date_from, card_time_from, card_date_to, card_time_to, card_people_count, card_valid_date, card_valid_time, card_host_id, card_imgpath, isHost, isFavorite, isImageSet ):
        self.card_activity_type = card_activity_type
        self.card_title = card_title
        self.card_location = card_location
        self.card_date_from = card_date_from
        self.card_time_from = card_time_from
        self.card_date_to = card_date_to
        self.card_time_to = card_time_to
        self.card_people_count = card_people_count
        self.card_valid_date = card_valid_date
        self.card_valid_time = card_valid_time
        self.card_host_id = card_host_id
        self.card_imgpath = card_imgpath
        self.isHost = isHost
        self.isFavorite = isFavorite
        self.isImageSet = isImageSet

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

@lm.user_loader
def load_user(id):
    return login_info.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html', pagetitle='Socialaza')

@app.route('/home')
def home():
    cardData = Card.query.all()
    return render_template('home.html', pagetitle='Ann Arbor',cardData=cardData)

@app.route('/activitydetail/<id>/')
def activitydetail(id):
    card = Card.query.get_or_404(id)
    return render_template('activitydetail.html', pagetitle='Activity Detail', card=card)

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
    cardData = Card.query.all()
    return render_template('interested.html', pagetitle='Interested', cardData=cardData)

@app.route('/history')
def history():
    cardData = Card.query.all()
    return render_template('history.html', pagetitle='History', cardData=cardData)

@app.route('/review')
def review():
    return render_template('review.html', pagetitle='Review',)

@app.route('/settings')
def settings():
    return render_template('settings.html', pagetitle='Settings',)

@app.route('/create', methods=['GET','POST'])
def create():
    # create = CreateForm()
    form = CreateCard()#request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            var1 = Card(
            card_activity_type = form.activity_type.data,
            card_title = form.title.data,
            card_location = form.location.data,
            card_date_from = form.date_from.data,
            card_time_from = form.time_from.data,
            card_date_to = form.date_to.data,
            card_time_to = form.time_to.data,
            card_people_count = form.people_count.data,
            card_valid_date = form.valid_date.data,
            card_valid_time = form.valid_time.data,
            card_host_id = current_user.username,
            card_imgpath = 'test',
            isHost = True,
            isFavorite = False,
            isImageSet = False)
            db.session.add(var1)
            db.session.commit()
            return redirect(url_for('activitydetail', id = var1.card_id))
        else:
            flash(form.errors)
            return render_template('create.html', pagetitle='Create Activity', form=form)
    elif request.method == 'GET':
        return render_template('create.html', pagetitle='Create Activity', form=form)

# @app.route('/createpreview', methods=['GET','POST'])
# def createpreview():
#     return render_template('createpreview.html', pagetitle='Activity Preview')

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

@app.route('/generate-data')
def generate_data():
    samplecard_1 = Card(card_activity_type='food',card_title='Lunch at Zingermann\'s',card_location='Zingermann\'s Delicatessen, 422 Detroit Street, Ann Arbor, MI 48104', card_date_from='6 Dec, 2017', card_time_from='12 PM', card_date_to='6 Dec, 2017', card_time_to='1 PM', card_people_count = 2, card_valid_date='6 Dec, 2017',card_valid_time='10 AM', card_host_id='Ling Zhong',card_imgpath='x',isHost=False,isFavorite=False,isImageSet=False)
    samplecard_2 = Card(card_activity_type='food',card_title='Lunch at AMA\'s',card_location='Ama Bistro Family Restaurant, 215 S State Street, Ann Arbor, MI 48104', card_date_from='7 Dec, 2017', card_time_from='12 PM', card_date_to='6 Dec, 2017', card_time_to='1 PM', card_people_count = 2, card_valid_date='6 Dec, 2017',card_valid_time='10 AM', card_host_id='Ling Zhong',card_imgpath='x',isHost=False,isFavorite=False,isImageSet=False)
    samplecard_3 = Card(card_activity_type='sports',card_title='Ice Skating during Winter break',card_location='Yost Ice Arena, 1116 S State Street, Ann Arbor, MI', card_date_from='14 Dec, 2017', card_time_from='1 PM', card_date_to='14 Dec, 2017', card_time_to='1 PM', card_people_count = 8, card_valid_date='11 Dec, 2017',card_valid_time='10 PM', card_host_id='Pallavi Gupta',card_imgpath='x',isHost=True,isFavorite=False,isImageSet=False)
    
    samplecard_4 = Card(card_activity_type='tour',card_title='UMMA Tour',card_location='University of Michigan Museum of Art, 525 S State St, Ann Arbor, MI 48109', card_date_from='11 Dec, 2017', card_time_from='2 PM', card_date_to='11 Dec, 2017', card_time_to='4 PM', card_people_count = 5, card_valid_date='9 Dec, 2017',card_valid_time='8 PM', card_host_id='Purva Sane',card_imgpath='x',isHost=True,isFavorite=False,isImageSet=False)
    
    samplecard_5 = Card(card_activity_type='adv',card_title='Skiing over Winter Break',card_location='Mount Brighton, 4141 Bauer Rd, Brighton, MI 48116', card_date_from='15 Dec, 2017', card_time_from='10 AM', card_date_to='18 Dec, 2017', card_time_to='11 PM', card_people_count = 7, card_valid_date='10 Dec, 2017',card_valid_time='3 AM', card_host_id='Purva Sane',card_imgpath='x',isHost=True,isFavorite=False,isImageSet=False)
    
    samplecard_5 = Card(card_activity_type='sports',card_title='Ice Skating during Winter break',card_location='Yost Ice Arena, 1116 S State Street, Ann Arbor, MI', card_date_from='14 Dec, 2017', card_time_from='1 PM', card_date_to='14 Dec, 2017', card_time_to='1 PM', card_people_count = 8, card_valid_date='11 Dec, 2017',card_valid_time='10 PM', card_host_id='Pallavi Gupta',card_imgpath='x',isHost=True,isFavorite=False,isImageSet=False)
    
    samplecard_6 = Card(card_activity_type='movie',card_title='Ferdinand Movie Outing',card_location='Quality 16, 3686 Jackson Road, Ann Arbor, MI 48103', card_date_from='15 Dec, 2017', card_time_from='8 PM', card_date_to='15 Dec, 2017', card_time_to='10 PM', card_people_count = 4, card_valid_date='12 Dec, 2017',card_valid_time='9 AM', card_host_id='Ling Zhong',card_imgpath='x',isHost=False,isFavorite=False,isImageSet=False)
    
    samplecard_7 = Card(card_activity_type='camping',card_title='Camping at Sleeping Bear Dunes',card_location='Sleeping Bear Dunes National Lakesho', card_date_from='19 Dec, 2017', card_time_from='6 AM', card_date_to='24 Dec, 2017', card_time_to='11 PM', card_people_count = 7, card_valid_date='12 Dec, 2017',card_valid_time='11 PM', card_host_id='Pallavi Gupta',card_imgpath='x',isHost=False,isFavorite=False,isImageSet=False)
    
    db.session.add(samplecard_1)
    db.session.add(samplecard_2)
    db.session.add(samplecard_3)
    db.session.add(samplecard_4)
    db.session.add(samplecard_5)
    db.session.add(samplecard_6)
    db.session.add(samplecard_7)

    db.session.commit()
    return redirect(url_for('home'))

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

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
    print('Hello world!', file=sys.stderr)
    if request.method == 'POST':
        try:
            name = request.form['name']
            dob = request.form['dob']
            location = request.form['location']
            interests = request.form['interests']
        
            with sqlite3.connect("db1.sqlite") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO profiledata (name,dob,location,interests) VALUES (?,?,?,?)",(name,dob,location,interests) )            
                con.commit()
                msg = "Record successfully added"
                print(msg)
        except:
            con.rollback()
            msg = "error in insert operation"
        finally:
            return redirect(url_for('home'))
            con.close()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
