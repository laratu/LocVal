from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
from .models import User,State
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


auth = Blueprint('auth',__name__)

REQUIRE_PW_TO_LOAD_DB = True
#second parameter is the password for loading the database
PW_DB = generate_password_hash("apfelkuchen", method="sha256")


#file from which the users' usernames will be added to the local sqlalchemy database
LOG_IN_DATA_FILE  = "logindata.csv"
logfile = "user_log.txt"



@auth.route("/login/", methods=["GET", "POST"])
def login():

    #manages login, redirectes and informs user if log-in failed
    if request.method =="POST":
        username_login = request.form.get("username")
        password_login = request.form.get("password")


        user = User.query.filter_by(username=username_login).first()

        if user:
            # successful login
            if check_password_hash(user.password, password_login):
                login_user(user, remember=True)

                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : User "+user.username+" logged in.\n"
                    output.write(msg.encode('utf8'))

                return redirect(url_for("views.map"))
            
            # Login with wrong password
            else:
                flash("Password for user '"+ username_login +"' incorrect.", category="error")
                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : Unsuccessful login attempt by user "+user.username+"."+user.password +"\n"
                    output.write(msg.encode('utf8'))

        # username not found
        else:
            flash("No user named '"+username_login+"' has been found.", category="error")
            with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : Unsuccesful Login with not existing username: "+username_login+"\n"
                    output.write(msg.encode('utf8'))

            if not User.query.first():
                flash("No users in database found.", category="error")
        
        return redirect(url_for("auth.login"))

    #sends log-in page to user
    if request.method =="GET":
        #checks if database needs to be loaded, and does so
        load_database()
        return render_template("login.html")

@auth.route("/logout/")
@login_required
def logout():
    #print("User "+current_user.username+" logged out.")
    with open(logfile, 'ab') as output:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = time + " : User "+current_user.username+" logged out.\n"
        output.write(msg.encode('utf8'))
    logout_user()
    return redirect(url_for("auth.login"))

#Force-reloads database. Only needed if data is added after running the server
@auth.route("/loaddb/", methods=["GET", "POST"])
def loaddb():
    #sends simple form to confirm PW_DB if REQUIRE_PW_TO_LOAD_DB is set to True
    if request.method =="GET":

            if not REQUIRE_PW_TO_LOAD_DB:
                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : Force reload of database...\n"
                    output.write(msg.encode('utf8'))
                load_users()
                return redirect(url_for("auth.login"))

            return '''<form method="POST">
            Enter password to reload database.<br>Note that the database is usually loaded after creation and only needs to be reloaded manually, if new data has been added after its creation.
            <div class="form-group">
                <input
                Enter password to load database
                type="password"
                class="form-control"
                id="password"
                name="load_db_password"
                />
            </div>
            <button type="submit" >Submit</button>
        
        </form>'''

    #validates PW_DB if REQUIRE_PW_TO_LOAD_DB is set to True and loads database
    if request.method =="POST":

        pw_db_form = request.form.get("load_db_password")
        if not check_password_hash(PW_DB, pw_db_form):
            return "wrong pw, pw can be found in auth.py"
        else:
            with open(logfile, 'ab') as output:
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg = time + " : Force reload of database...\n"
                output.write(msg.encode('utf8'))
            load_users()
            return redirect(url_for("auth.login"))






    
def load_database():
    if(State.query.count()==0):
        state = State()
        state.db_loaded = False
        state.sigLoc_loaded = False
                        
        db.session.add(state)
        db.session.commit()
    
    #if db is empty
    if State.query.first().db_loaded == False:
        load_users()
        State.query.first().db_loaded = True
        db.session.commit()



#loads log-in data from LOG_IN_DATA_FILE (csv) in a local sqlanchemy database in order to work with flask-login
def load_users():
    #read data and put it in a dataframe (if it exists)
    if path.exists(LOG_IN_DATA_FILE):

        df = pd.read_csv(LOG_IN_DATA_FILE)

        with open(logfile, 'ab') as output:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = time + " : Add users to database...\n"
            output.write(msg.encode('utf8'))
        
        #some variables to provide interesting information
        new = 0
        old = 0
        p = 0


        # delte users which are no longer in login.csv
        existing_users = User.query.all()
        for user in existing_users:

            if user.username not in filter(lambda x: isinstance(x,str), df["username"]):
                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : User: " + user.username + "will be deleted" + "\n"
                    output.write(msg.encode('utf8'))

                db.session.delete(user)
                db.session.commit()





        # add or update users from login-file
        for index, row in df.iterrows():
            username_df = row['username']

            #if user with same username is already in database, don't add them again
            if User.query.filter_by(username=username_df).first():
                old=old+1


                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : remaining User: " + username_df + "\n"
                    output.write(msg.encode('utf8'))

                #however, check if they have a new password and set it, if so
                existing_user = User.query.filter_by(username=username_df).first()
                
                if not check_password_hash(existing_user.password, row['password']):
                    existing_user.password = generate_password_hash(row['password'], method="sha256")
                    db.session.commit()
                    p=p+1
                    
            else:
                #build new user
                new_user = User()
                new_user.username = username_df
                new_user.password = generate_password_hash(row['password'], method="sha256")
                new_user.sigLoc_loaded = False
                new_user.survey_part1_answered = False
                new_user.survey_part2_answered = False
                
                #add new user
                db.session.add(new_user)
                db.session.commit()
                new = new+1

                with open(logfile, 'ab') as output:
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = time + " : new User: " + new_user.username + "\n"
                    output.write(msg.encode('utf8'))
                




        number_of_users = User.query.count()

        with open(logfile, 'ab') as output:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = time + " : database is updated!\n"
            msg += str(number_of_users)+" users in database.\n"
            output.write(msg.encode('utf8'))




        # no users in database
        if number_of_users == 0:
            flash("No users found in database.", category="error")
            with open(logfile, 'ab') as output:
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msg = time + " : No users found in database!\n"
                output.write(msg.encode('utf8'))

    else:
        number_of_users = User.query.count()
        with open(logfile, 'ab') as output:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = time + " : No file "+ LOG_IN_DATA_FILE +" found!\n"
            msg += str(number_of_users)+" users in database.\n"
            output.write(msg.encode('utf8'))