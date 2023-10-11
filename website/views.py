from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from website.map import buildmap
from website.map import metadata
from website.map import build_date_map
from os import path, mkdir
from flask import send_file, flash
from . import db
from random import randint
import pandas as pd
import sys
from datetime import datetime
# create a new blueprint, which defines how the website can be accessed
views = Blueprint('views', __name__,)
logfile = "user_log.txt"


#* User eingeloggt?
@views.route("/")
def home():
    if (current_user.is_authenticated):
        return redirect(url_for("views.map"))
    else:
        return redirect(url_for("auth.login"))




#* map 
@views.route("/map/", methods=['GET', 'POST'])
@login_required
def map():


    #* POST: Filter mit Startzeitpunkt und Endzeitpunkt
    # Bei jeder Filteränderung wird die Map aktualisiert
    if request.method == 'POST':
        random_number = randint(1, 9999999999)

        date = request.form.get('date')
        build_date_map(current_user, date, random_number)        

        #* Metadaten hinzufügen
        df_metadata = metadata(current_user)
        # rendern, df_metadata für Seite greifbar machen
        trip_chart = "/chart"
        poi_chart = "/poi_chart"


        temp = render_template("map.html", Metadata=zip(
            df_metadata.columns, df_metadata.loc[0]), df_metadata=df_metadata, random_number = random_number, trip_chart=trip_chart, poi_chart=poi_chart)
        
        return temp




    #* GET: ertstellen der Map & Map.html
    if request.method == 'GET':

        random_number = randint(1, 9999999999)

        buildmap(current_user, random_number)
        # add metadata
        df_metadata = metadata(current_user)

        trip_chart = "/chart"
        poi_chart = "/poi_chart"

        return render_template("map.html", Metadata=zip(df_metadata.columns, df_metadata.loc[0]), df_metadata=df_metadata, random_number = random_number, trip_chart=trip_chart, poi_chart=poi_chart)







#* Zugriff auf erstellte Folium Map
@views.route("/displaymap/")
@login_required
def map1():
    random_number = request.args.get("random_number")

    temp = render_template("iframes/map"+random_number+".html")
    return temp









@views.route("/survey_part2/")
@login_required
def survey_part2():

    if current_user.survey_part2_answered:
        flash("Sie haben die Studie bereits erfolgreich ausgeführt!", category="error")
        return redirect(url_for("views.map"))

    return render_template("survey2.html")


@views.route("/receivedata_part2/", methods=['POST'])
@login_required
def receivedata_part2():

    saveSurveyData(request.data, "part2/")
    current_user.survey_part2_answered = True
    db.session.commit()
    with open(logfile, 'ab') as output:
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = time + " : "+ current_user.username + " answered survey part 2: "+str(current_user.survey_part2_answered) +"\n"
        output.write(msg.encode('utf8'))
    
    
    return ""

def saveSurveyData(data, directory):
    
    data = request.data
    
    if not path.exists('surveyData/'):
        mkdir("surveyData/")
    if not path.exists('surveyData/'+directory):
        mkdir("surveyData/"+directory)


    with open("surveyData/"+directory+current_user.username+".csv", "wb") as binary_file:
        
        # data starts with : 'data="Screen index","Type of[...]'
        #get rid of 'data='
        data = data[5:]
        binary_file.write(data)

    if not path.exists("surveyData/"+directory+current_user.username+".csv"):
        with open(logfile, 'ab') as output:
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = time + " : Error while saving survey data for user "+current_user.username+" in "+directory+"\n"
            output.write(msg.encode('utf8'))
    




# * Alle Bilder vom HOST Laden
# Bilder für Survey
@views.route('/get_image')
def get_image():
    img = request.args.get("image")
    directory ="./templates/img/"
    return send_file(directory+img, mimetype='image/gif')




@views.route('/chart')
def chart():
    csv_path = "data/" + current_user.username + "/report" + ".csv"
    df = pd.read_csv(csv_path)
    df = df.iloc[1:]

    labels = df['time'].to_list()
    values = df['total trip path distance (km)'].to_list()


    return render_template("trip-chart.html", labels=labels, values=values)







@views.route('/poi_chart')
def poi_chart():
    csv_path = "data/" + current_user.username + "/unique_stops" + ".csv"
    df = pd.read_csv(csv_path)

    trips = pd.read_csv("data/" + current_user.username + "/report" + ".csv")

    d = {'class': ['Home', 'work_education','free_time','health', 'shopping','no classification'], 'color': ['#38a9dc','#303030','#f59630','#cc0000','#d152b8','#a3a3a3'], 'duration':[0,0,0,0,0,0]}
    df2 = pd.DataFrame(d)

    for i in range(0, len(df2)):
        clas = df2.iloc[i][0]
        data = df[df['class'] == df2.iloc[i][0]]
        df2['duration'].iloc[i] = data['duration'].sum()


    labels = df2['class'].to_list()
    labels = ['Wohnort', 'Beruf','Freizeit','Körperliche Betätigung', 'Einkaufen','Unbekannt',"Trips"]
    values = df2['duration'].to_list()
    barColors = df2['color'].to_list()

    values.append(trips['total trip duration (min)'][0]*60)
    barColors.append("#0000ff")

    return render_template("poi_chart.html", labels=labels, values=values, barColors=barColors)