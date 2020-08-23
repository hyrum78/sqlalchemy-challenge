#import the goods
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#setup
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Sip the Flask
app = Flask(__name__)

@app.route("/")
def all_routes():
    return (
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/YYYY-MM-DD<br>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = end_date[0]
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)

    prcp_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= start_date).order_by((Measurement.date).desc()).all()
    prcp_scores = list(prcp_scores)

    session.close()

    return jsonify(prcp_scores)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    all_stations = session.query(Station.station, Station.name).all()
    station_list = list(np.ravel(all_stations))

    session.close()

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    temps_end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    temps_end = temps_end[0]
    temps_start = dt.datetime.strptime(temps_end, "%Y-%m-%d") - dt.timedelta(days=365)

    tobs_list = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= temps_start).filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()
    tobs_list = list(np.ravel(tobs_list))

    session.close()

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_temps(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query functions
    min_temps = func.min(Measurement.tobs)
    max_temps = func.max(Measurement.tobs)
    avg_temps = func.avg(Measurement.tobs)

    sel = [min_temps, max_temps, avg_temps]
    temps_output = session.query(*sel).filter(Measurement.date >= start).all()

    # temp dictionary
    start_temps = []

    for min_temps, max_temps, avg_temps in temps_output:
        temp_dict = {}
        temp_dict["Lowest Temp"] = min_temps
        temp_dict["Highest Temp"] = max_temps
        temp_dict["Average Temp"] = avg_temps
        start_temps.append(temp_dict)

    return jsonify(start_temps)


@app.route("/api/v1.0/<start>/<end>")
def range_temps(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # query functions
    min_temps = func.min(Measurement.tobs)
    max_temps = func.max(Measurement.tobs)
    avg_temps = func.avg(Measurement.tobs)

    sel = [min_temps, max_temps, avg_temps]
    temps_output = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # temp dictionary
    start_end_temps = []

    for min_temps, max_temps, avg_temps in temps_output:
        temp_dict = {}
        temp_dict["Lowest Temp"] = min_temps
        temp_dict["Highest Temp"] = max_temps
        temp_dict["Average Temp"] = avg_temps
        start_end_temps.append(temp_dict)

    return jsonify(start_end_temps)



if __name__ == "__main__":
    app.run(debug=True)