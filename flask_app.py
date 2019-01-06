import numpy as np
from datetime import datetime
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
   
   
    # Query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for precip in results:
        precip_dict = {}
        precip_dict["date"] = precip.date
        precip_dict["prcp"]= precip.prcp
        
        all_precipitation.append(precip_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    #Query to retrieve all stations
    stations=session.query(Station.station,Station.name).all()

    all_stations = []
    for station in stations:
        stat_dict = {}
        stat_dict["name"] = station.name

        all_stations.append(stat_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""
    #Latest Date in the database
    
    end_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    for date in end_date:
        split_last_date=date.split('-')
    
        split_last_date
        last_year=int(split_last_date[0])
        last_month=int(split_last_date[1]) 
        last_day=int(split_last_date[2])

    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)

    # Query for dates and temperature observations from year ago
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date>=query_date).order_by(Measurement.date).all()

    all_tobs = []
    for row in results:
        tobs_dict = {}
        tobs_dict["date"]= row.date
        tobs_dict["tobs"] = row.tobs

        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/start")

#Return a JSON list of the minimum temperature,
#the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and
#equal to the start date.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates in the start and end date inclusive.

def calc_temp_start(start_date):
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start_date).order_by(Measurement.date.desc()).all()
    
    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)
@app.route("/api/v1.0/start/end")

def calc_temp_startend(start_date,end_date):         
    """ When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive. """    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).order_by(Measurement.date.desc()).all()
    # Convert the query results to a Dictionary using date as the key and tobs as the value.
    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)

if __name__ == '__main__':
    app.run(debug=True)
