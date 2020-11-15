import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome to the Climate App API!
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App API!<br>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"The following two routes require date entry as yyyy-mm-dd<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary (of dates and precipitation amounts for the 
# year of the data in our dataset).
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all dates and preceiptitation amounts for the last 12 months in the dataset"""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query to find out the final date in the data
    last_measurement_record = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Define variables for year, month and day of the last measurement record
    last_measurement_year = int(last_measurement_record[0][:4])
    last_measurement_month = int(last_measurement_record[0][5:7])
    last_measurement_day = int(last_measurement_record[0][8:10])

     # Calculate the date 1 year ago from the last data point in the database
    date_year_ago = dt.date(last_measurement_year,\
                            last_measurement_month,\
                            last_measurement_day) - \
                            dt.timedelta(days=365)


    # Query for all of the precipitation data for the last year of data
    results = session.query(Measurement.date,Measurement.prcp).\
                     filter(Measurement.date >= date_year_ago).\
                   order_by(Measurement.date)

    session.close()

  # Create a dictionary from the row data and append to a list of precipitation_twelve_months
    precipitation_twelve_months = []
    for measure_date,measure_prcp in results:
        measure_dict = {}
        measure_dict[measure_date] = measure_prcp

        precipitation_twelve_months.append(measure_dict)
    
    # Return JSON of the last 12 month's worth of precipitation data from our dataset
    return jsonify(precipitation_twelve_months)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of station ids, stations, station names, station latitude, station longititude,
       and elevation for all stations"""
 
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.id,Station.station,Station.name,\
                            Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for id,station,name,latitude,longitude,elevation in results:
        station_dict = {}
        station_dict["id"] = name
        station_dict["station"] = station
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation

        all_stations.append(station_dict)
    
    # Return JSON of all_stations
    return jsonify(all_stations)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a year's worth of temperature data for the most active station in our dataset"""  
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Figure out the most active station id
    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()[0]
    # Figure out the last date in the measurement table for the most active station
    most_active_last_measurement_record = session.query(Measurement.date).\
                                              filter_by(station= most_active_station).\
                                               order_by(Measurement.date.desc()).first()

    most_active_last_measurement_year = int(most_active_last_measurement_record[0][:4])
    most_active_last_measurement_month = int(most_active_last_measurement_record[0][5:7])
    most_active_last_measurement_day = int(most_active_last_measurement_record[0][8:10])

    # Calculate the a year ago from the last measurement date of the most active
    # station
    most_active_date_year_ago = dt.date(most_active_last_measurement_year,\
                                    most_active_last_measurement_month,\
                                    most_active_last_measurement_day) - dt.timedelta(days=365)

    # Now get the temperature data for the most active station for the last tweleve months
    # of data
    results = session.query(Measurement.date,Measurement.tobs).\
                     filter(Measurement.station== most_active_station,\
                            Measurement.date >= most_active_date_year_ago)

    session.close()

   # Create a dictionary from the row data and append to most_active_temp_twelve_months
    most_active_temp_twelve_months = []
    for measure_date,measure_tobs in results:
        measure_dict = {}
        measure_dict[measure_date] = measure_tobs

        most_active_temp_twelve_months.append(measure_dict)

    # Return JSON of the most active stations temperature data for the
    # last year of data in our dataset
    return jsonify(most_active_temp_twelve_months)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for 
# a given start or start-end range.  When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
# for all dates greater than and equal to the start date.  When given the start and the end date, 
# calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps_for_date_range(start,end=None):
    """Return max,min,avg for the most active station between the two dates given
       or after a start date if no end date is given""" 

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Figure out the most active station id
    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()[0]
    if end == None:
        # query for the max, min, avergage for the most active station starting with our given start date
        results = session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start,
                                Measurement.station == most_active_station).all()
    else:
        # query for the max, min, avergage for the most active station for the given date range
        results = session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
                         filter(Measurement.date >= start,
                                Measurement.date <= end,
                                Measurement.station == most_active_station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    max_min_avg = []

    for temp_max,temp_min,temp_avg in results:
        temp_dict = {}
        temp_dict['Start_Date'] = start

        # Only include end date if one was given
        if end != None:
            temp_dict['End_Date'] = end

        temp_dict['Most Active Station'] = most_active_station
        temp_dict['Maximum_Temp'] = temp_max
        temp_dict['Minimum_Temp'] = temp_min
        temp_dict['Average_Temp'] = temp_avg

        # Append the information into max_min_avg list
        max_min_avg.append(temp_dict)
        
    # Return JSON of the max, min and avg for the given date(s)
    return jsonify(max_min_avg)


if __name__ == '__main__':
    app.run(debug=True)

