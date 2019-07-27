

import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station




#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    
    return (
    f"Welcome to the Surfs API! !<br/>" 
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end><br/>"
    )



"""TODO: Handle API route with variable path to allow getting info
for a specific character based on their 'superhero' name """

@app.route("/api/v1.0/precipitation")
def dateprep():
    
    session = Session(engine)

    query_date_to = [x for x in session.query(func.max(Measurement.date))]
    datestr = str(query_date_to[0][0])

    yearofdate = datestr.split('-')
    yearofdate
    query_date_from = dt.date(int(yearofdate[0]), int(yearofdate[1]), int(yearofdate[2]))  - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores

    precip12months = session.query(Measurement.date, Measurement.prcp).filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date_from ).all()

    finallist = []

    for date, prcp in precip12months:
        finaldict = {}
        finaldict["date"] = date
        finaldict["prcp"] = prcp
        
        finallist.append(finaldict)


    return jsonify(finallist)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    cols = [Station.id , Station.station , Station.name , Station.latitude , Station.longitude , Station.elevation]

    stations = session.query(*cols).order_by(Station.station).all()

    stationsdf = pd.DataFrame(stations)

    stationsdf.set_index('id', inplace=True)

    finallist = [i for i in stationsdf['name']]

    return jsonify(finallist)


@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    query_date_to = [x for x in session.query(func.max(Measurement.date))]
    datestr = str(query_date_to[0][0])

    stationcounts = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    mostactivestation = stationcounts[0][0]

    yearofdate = datestr.split('-')
    yearofdate
    query_date_from = dt.date(int(yearofdate[0]), int(yearofdate[1]), int(yearofdate[2]))  - dt.timedelta(days=365)

    
    MostActiveStn12months = session.query(Measurement.tobs).filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date_from).filter(Measurement.station == mostactivestation).all()
    MostActiveStn12monthsDf = pd.DataFrame(MostActiveStn12months)

    finallist = [i for i in MostActiveStn12monthsDf['tobs']]

    return jsonify(finallist)


@app.route("/api/v1.0/<start>")
def start_only(start):

    #print('start = ', start)    
    session = Session(engine)

    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    finallist = []

    for a,b,c in temps:
        finaldict = {}
        finaldict["Min"] = a
        finaldict["Avg"] = b
        finaldict["Max"] = c
        
        finallist.append(finaldict)

    return jsonify(finallist)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    
    session = Session(engine)

    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    finallist = []

    for a,b,c in temps:
        finaldict = {}
        finaldict["Min"] = a
        finaldict["Avg"] = b
        finaldict["Max"] = c
        
        finallist.append(finaldict)

    return jsonify(finallist)


if __name__ == "__main__":
    app.run(debug=True)
