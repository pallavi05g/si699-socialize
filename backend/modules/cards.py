#from flask import render_template, flash, redirect, session, url_for, request, g
#from flask_login import login_user, logout_user, current_user, login_required
#from datetime import datetime
#from app import app, db, lm, User
#
#int card_count = 0;
#def create_init_cards():
#    con = sql.connect("db.sqlite")
#    if not mycard:
##        mycard = card(card_id=card_id+1, card_activity_type="food",card_title="Lunch at Zingermann\'s",card_location="Zingermann\'s Delicatessen, Ann Arbor, MI", card_date_from="6 Dec, 2017", card_time_from="12 PM", card_date_to="6 Dec, 2017", card_time_to="1 PM", card_people_count = 2, card_valid_date="6 Dec, 2017",card_valid_time="10 AM", card_host_id="Ling Zhong",card_imgpath=null,isHost=false,isFavorite=false,isImageSet=false)
##        db.session.add(mycard)
##        db.session.commit()
#        
#        
#        mycard = insert(card).values(
#            card_id=card_id+1, card_activity_type="food",card_title="Lunch at Zingermann\'s",card_location="Zingermann\'s Delicatessen, Ann Arbor, MI", card_date_from="6 Dec, 2017", card_time_from="12 PM", card_date_to="6 Dec, 2017", card_time_to="1 PM", card_people_count = 2, card_valid_date="6 Dec, 2017",card_valid_time="10 AM", card_host_id="Ling Zhong",card_imgpath=null,isHost=false,isFavorite=false,isImageSet=false
#        
#    )
#        db.session.commit()
#        