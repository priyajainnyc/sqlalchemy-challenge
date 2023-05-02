# Import the dependencies.

import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

# Create an instance of the Flask class
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Create Flask Routes - route 'decorator' to tell Flask which URL triggers the function below
# Start at the landing page /

@app.route("/")
def welcome():
    # List all the available routes
    return (
        f"Welcome to the SQL-Alchemy Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
# Convert the query results to a dictionary by using date as the key and prcp as the value
# Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    mostrecent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    print(mostrecent_date)

    # Calculate the date one year from the last date in data set.
    latest_date = dt.datetime.strptime(mostrecent_date[0], '%Y-%m-%d').date()
    start_date = latest_date - dt.timedelta(days=365)

    # Perform a query to retrieve all the date and precipitation values
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).order_by(measurement.date).all()

    # Close session
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    prcp_dict = {} 
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    # Return the JSON representation of your dictionary for the last year in the database.
    return jsonify(prcp_dict)

# Create a route that returns a JSON list of stations from the database
@app.route("/api/v1.0/stations")
def stations(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve all of the station values
    total_stations = session.query(station.id, station.station, station.name).all()
    
    # Close session
    session.close()  
    
    # Convert the query results to a dictionary using for loop
    list_stations = []

    for st in total_stations:
        station_dict = {}

        station_dict["id"] = st[0]
        station_dict["station"] = st[1]
        station_dict["name"] = st[2]

        list_stations.append(station_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(list_stations)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs") 
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    mostrecent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    latest_date = dt.datetime.strptime(mostrecent_date[0], '%Y-%m-%d').date()
    start_date = latest_date - dt.timedelta(days=365)
    
    # Create query for all tobs for 12 months from most recent date
    stationtemps_mostactive = session.query(measurement.date, measurement.tobs).filter(func.strftime(measurement.date) >= start_date, measurement.station == 'USC00519281').group_by(measurement.date).order_by(measurement.date).all()
    
    # Close session
    session.close() 
    
    tobs_values = []
    for date, tobs in stationtemps_mostactive:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_values.append(tobs_dict) 
          
    return jsonify(tobs_values) 

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date

# Use format http://127.0.0.1:5000/api/v1.0/2017-07-01

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, TMAX for specified start for all dates greater than or equal to start date
    start_results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    
    # Close session
    session.close()

    start_tobs = []
    for date, min, avg, max in start_results:
        start_tobs_dict = {}
        start_tobs_dict["Date"] = date
        start_tobs_dict["TMIN"] = min
        start_tobs_dict["TAVG"] = avg
        start_tobs_dict["TMAX"] = max
        start_tobs.append(start_tobs_dict) 

    return jsonify(start_tobs)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

# Use format http://127.0.0.1:5000/api/v1.0/2016-07-01/2016-07-04

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query TMIN, TAVG, TMAX for specified start and end date for dates from start to end date, inclusive.
    start_end_results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Close session
    session.close()
    
    start_end_tobs = []
    for date, min, avg, max in start_end_results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["Date"] = date
        start_end_tobs_dict["TMIN"] = min
        start_end_tobs_dict["TAVG"] = avg
        start_end_tobs_dict["TMAX"] = max
        start_end_tobs.append(start_end_tobs_dict) 
        
    return jsonify(start_end_tobs)

if __name__ == "__main__":
    app.run(debug=True)

# Close session
session.close()