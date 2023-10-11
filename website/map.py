import folium
import pandas as pd
import datetime
import ast
import folium
import pandas as pd
from branca.element import Template, MacroElement
from datetime import datetime
from os import path, mkdir, listdir, remove
import datetime
import sys




# builds a little popup
def buildPopup(user, i, classified):

    data_stops = stopdata(user)

    html = ""

    time = data_stops['duration'].iloc[i]
    time = seconds_to_timestr(time)
    html += "<b>Verbrachte Zeit:</b><br>" + time +" <br><br>"

    visits = data_stops['stop_count'].iloc[i]
    html += "<b>Anzahl der Besuche:</b> <br>" + str(visits) +"<br><br>"

    html += "<b>Besucht am:</b><br>"



    for j in range(len(data_stops['starts'].iloc[i])):

        startdate = data_stops['starts'].iloc[i][j]
        startdate = startdate[0:10]

        duration = data_stops['durations'].iloc[i][j]
        duration = seconds_to_timestr(duration)

        html += startdate + '<br>' + duration + '<br><br>'


    html += "<b>Adresse:</b> <br>" + data_stops['adress'].iloc[i] +"<br><br>"



    if(classified):
        class_de =  {
            'Home' : 'Wohnort', 
            'work_education': 'Beruf',
            'free_time':'Freizeit',
            'health':'Körperliche Betätigung', 
            'shopping':'Einkaufen',
            'no classification':'Fortbewegung'
        }
        class_en = data_stops['class'].iloc[i]
        html += "<b>Datentyp:</b> <br>" + class_de[class_en] + "<br><br>"

        if not ((data_stops['name'].iloc[i] == 'no name') or (data_stops['name'].iloc[i] == 'Home Location') or (data_stops['name'].iloc[i] == 'Work Location')):
            html += "<b>Gefundener Ort:</b> <br>" + data_stops['name'].iloc[i] + "<br><br>"

    #html += "Adresse:<br>"+str(adress)
    iframe = folium.IFrame(html, width=200,  height=200)

    popup = folium.Popup(iframe, max_width=200)
    return popup





def buildPopup_date(stop, classified):

    # time
    startdate = stop['start'][0:10]
    starttime = stop['start'][11:16]

    enddate = stop['stop'][0:10]
    enddate = '<br>' + enddate + ', '
    if(startdate == enddate[4:14]):
        enddate = ''
    endtime = stop['stop'][11:16]



    html = ""

    html += "<b>Besucht von : </b></br>" + startdate + ', ' + starttime + 'Uhr' + '<br>bis: '+ enddate + endtime + 'Uhr<br><br>'

    html += "<b>Adresse:</b> <br>" + stop['adress'] +"<br><br>"


    if(classified):
        class_de =  {
            'Home' : 'Wohnort', 
            'work_education': 'Beruf',
            'free_time':'Freizeit',
            'health':'Körperliche Betätigung', 
            'shopping':'Einkaufen',
            'no classification':'Fortbewegung'
        }
        class_en = stop['class']
        html += "<b>Datentyp:</b> <br>" + class_de[class_en] + "<br><br>"


        if not ((stop['name'] == 'no name') or (stop['name'] == 'Home Location') or (stop['name'] == 'Work Location')):
            html += "<b>Gefundener Ort:</b> <br>" + stop['name'] + "<br><br>"

    iframe = folium.IFrame(html, width=200,  height=200)

    popup = folium.Popup(iframe, max_width=200)
    return popup




def saveMap(map, filenumber):
    dir = 'website/templates/iframes/'

    #check if directory exists and create one, if it doesn't
    if not path.exists(dir):
        mkdir(dir)
    
    #delete other file(s) to prevent memory overflow
    for f in listdir(dir):
        remove(path.join(dir, f))

    #save file
    map.save(dir+"map"+str(filenumber)+'.html')





# legend explaining loctypes
def addLegend(map):

    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>jQuery UI Draggable - Default functionality</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    
    <script>
    $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

    </script>
    </head>
    <body>

    
    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
        border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
        
    <div class='legend-title'>Datentypen</div>
    <div class='legend-scale'>
    <ul class='legend-labels'>
        <li><span style='background:#38a9dc;opacity:0.7;'></span>Wohnort</li>
        <li><span style='background:black;opacity:0.7;'></span>Beruf</li>
        <li><span style='background:#f49630;opacity:0.7;'></span>Freizeit</li>
        <li><span style='background:#cc0000;opacity:0.7;'></span>Körperliche Betätigung</li>
        <li><span style='background:#ff66ff;opacity:0.7;'></span>Einkaufen</li> 
        <li><span style='background:#0000ff;opacity:0.7;height:5px;margin-top: 5px;'></span>Fortbewegung</li>

    </ul>
    </div>
    </div>
    
    </body>
    </html>

    <style type='text/css'>
    .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
    .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
    .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
    .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: none;
        }
    .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
    .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)

    map.get_root().add_child(macro)








# *function for building the map with given data
def buildmap(user, filenumber):
    '''
    userStr = str(user)[1:-1].replace(" ","")
    #print(str(user))
    print(type(userStr)) 
    print(userStr)
    print("username: " +  user.username)
    '''

    # * load data
    csv_trip = "data/" + user.username + "/alldata.csv"
    data_trip = pd.read_csv(csv_trip)
    csv_stops = "data/" + user.username + "/unique_stops.csv"
    data_stops = pd.read_csv(csv_stops)


    # *create map
    center_point = data_trip['lat'].mean(), data_trip['lon'].mean()
    m = folium.Map(center_point, zoom_start=12)


    # *display Trips as line
    for i in range(0, len(data_trip)-1):
        loc1 = data_trip['lat'].iloc[i], data_trip['lon'].iloc[i]
        loc2 = data_trip['lat'].iloc[i+1], data_trip['lon'].iloc[i+1]

        loc = [loc1, loc2]
        
        folium.PolyLine(loc, weight=5, opacity=1, color="blue").add_to(m) #color="#0a1628").add_to(m)



    # * display stops
    for i in range(0, len(data_stops)):
        if(data_stops['class'].iloc[i]=='Home'):
            popup = buildPopup(user, i, True)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]), icon=folium.Icon(
            color='blue', icon='house', prefix='fa'), popup=popup).add_to(m)

        elif(data_stops['class'].iloc[i]=='work_education'):
            popup = buildPopup(user, i, True)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]), icon=folium.Icon(
            color='black', icon='briefcase', prefix='fa'), popup=popup).add_to(m)

        elif(data_stops['class'].iloc[i]=='free_time'):
            popup = buildPopup(user, i, True)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]), icon=folium.Icon(
            color='orange', icon='face-smile-beam', prefix='fa'),popup=popup).add_to(m)
        
        elif(data_stops['class'].iloc[i]=='shopping'):
            popup = buildPopup(user, i, True)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]), icon=folium.Icon(
            color='purple', icon='cart-shopping', prefix='fa'),popup=popup).add_to(m)

        elif(data_stops['class'].iloc[i]=='health'):
            popup = buildPopup(user, i, True)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]), icon=folium.Icon(
            color='red', icon='fa-heart-pulse', prefix='fa'),popup=popup).add_to(m)

        else:
            popup = buildPopup(user, i, False)
            folium.Marker((data_stops['lat'].iloc[i], data_stops['lon'].iloc[i]),  icon=folium.Icon(
            color='lightgray', icon="minus", prefix="fa"),popup=popup).add_to(m)
        


    addLegend(m)




    #save file
    saveMap(m,filenumber)

#checks if a number is NaN by comparing it to itself
#https://stackoverflow.com/questions/944700/how-can-i-check-for-nan-values
def isNaN(num):
    return num != num



#* builds new map with filtered date range
def build_date_map(user, date, filenumber):

    csv_path = "data/" + user.username + "/alldata.csv"
    data = pd.read_csv(csv_path)
    
    # data filtered by date
    newData = pd.DataFrame()

    date = str(date)


    # all data, same as main page
    if(date == 'Gesamt'):
        buildmap(user, filenumber)
        return

    # only data filtered by date
    else:
        for i in range(0, len(data)-1):
            dataDate = data['ts'].iloc[i]

            if date in dataDate:
                newData = pd.concat([newData, data.iloc[[i]]])

    # no data found
    if (newData.empty):
        location = data['lat'].mean(), data['lon'].mean()
        m4 = folium.Map(
            location,
            zoom_start=12)

        saveMap(m4,filenumber)


    #* create filtered map
    else:
        # create map
        center_point = newData['lat'].mean(), newData['lon'].mean()
        m = folium.Map(center_point, zoom_start=12)


        # display Trips as line
        for i in range(0, len(newData)-1):
            loc1 = newData['lat'].iloc[i], newData['lon'].iloc[i]
            loc2 = newData['lat'].iloc[i+1], newData['lon'].iloc[i+1]

            loc = [loc1, loc2]
            
            folium.PolyLine(loc, weight=5, opacity=1, color="blue").add_to(m) 


        data_stops = stopdata(user)
        stops_date = stopDates_df(date, data_stops)

        
            # * display stops
        for i in range(0, len(stops_date)):
            if(stops_date['class'].iloc[i]=='Home'):
                popup = buildPopup_date(stops_date.iloc[i], True)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]), icon=folium.Icon(
                color='blue', icon='house', prefix='fa'), popup=popup).add_to(m)

            elif(stops_date['class'].iloc[i]=='work_education'):
                popup = buildPopup_date(stops_date.iloc[i], True)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]), icon=folium.Icon(
                color='black', icon='briefcase', prefix='fa'), popup=popup).add_to(m)

            elif(stops_date['class'].iloc[i]=='free_time'):
                popup = buildPopup_date(stops_date.iloc[i], True)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]), icon=folium.Icon(
                color='orange', icon='face-smile-beam', prefix='fa'),popup=popup).add_to(m)
            
            elif(stops_date['class'].iloc[i]=='shopping'):
                popup = buildPopup_date(stops_date.iloc[i], True)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]), icon=folium.Icon(
                color='purple', icon='cart-shopping', prefix='fa'),popup=popup).add_to(m)

            elif(stops_date['class'].iloc[i]=='health'):
                popup = buildPopup_date(stops_date.iloc[i], True)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]), icon=folium.Icon(
                color='red', icon='fa-heart-pulse', prefix='fa'),popup=popup).add_to(m)

            else:
                popup = buildPopup_date(stops_date.iloc[i], False)
                folium.Marker((stops_date['lat'].iloc[i], stops_date['lon'].iloc[i]),  icon=folium.Icon(
                color='lightgray', icon="minus", prefix="fa"),popup=popup).add_to(m)


        addLegend(m)
        saveMap(m,filenumber)




# creates a new DataFrame, with Places visited on a specific date
def stopDates_df(date, df):
    datestop_df = pd.DataFrame(columns = ['lat','lon','start','stop','duration','class', 'name', 'adress'] )

    format = "%Y-%m-%d"
    date = datetime.datetime.strptime(date, format)

    for i in range(len(df)):

        for j in range(len(df['starts'].iloc[i])):
            
            startdate = df['starts'].iloc[i][j]
            startdate = get_datetime_date(startdate)
            stopdate = df['stops'].iloc[i][j]
            stopdate = get_datetime_date(stopdate)

            if(startdate <= date <= stopdate):
                stop = pd.DataFrame( [[df['lat'].iloc[i], df['lon'].iloc[i], df['starts'].iloc[i][j], df['stops'].iloc[i][j], df['durations'].iloc[i][j], df['class'].iloc[i], df['name'].iloc[i], df['adress'].iloc[i]]], columns = ['lat','lon','start','stop','duration','class', 'name', 'adress'] )
                datestop_df = pd.concat([datestop_df, stop])
    
    return datestop_df








def metadata(current_user):
    csv_path = "data/" + current_user.username + "/report" + ".csv"
    df = pd.read_csv(csv_path)
    df['time'].iloc[0]='Gesamt'
    return df


# unique_stops.csv
# convert str to list
def stopdata(current_user):
    csv_path = "data/" + current_user.username + "/unique_stops" + ".csv"
    df = pd.read_csv(csv_path)

    # convert list to str
    if(type(df['starts'].iloc[0])!= list):
        df['starts'] = df.apply(lambda x: ast.literal_eval(x.starts), axis=1)
        df['stops'] = df.apply(lambda x: ast.literal_eval(x.stops), axis=1)
        df['durations'] = df.apply(lambda x: ast.literal_eval(x.durations), axis=1)

    return df


# only date from datetimestring
def get_datetime_date(datestring):
    format = "%Y-%m-%d"
    date = datestring[0:10]
    date = datetime.datetime.strptime(date, format)
    return date



# input: seconds
# output: str: xTage, xh xmin
def seconds_to_timestr(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{} {} {}'.format(
            "" if int(days) == 0 else str(int(days)) + ' Tage,',
            "" if int(hours) == 0 else str(int(hours)) + 'h',
            "" if int(minutes) == 0 else str(int(minutes))  + 'min' )