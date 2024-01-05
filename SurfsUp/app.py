# Import the dependencies.
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

## Create an app using flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

## Define homepage
@app.route("/")
def home():
    return(
        
        # Define available routes
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016.8.23<br/>"
        f"/api/v1.0/2016.8.23/2017.8.23"
    )

## Define precipitation analysis page
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create session from python to the database
    session = Session(engine)

    # Query precipitation data for the last year of available data
    past_year_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= dt.date(2016, 8 , 23)).order_by('date').all()

    session.close()

    # Create a dictionary from the data
    year_prcp = []
    for date, prcp in past_year_data:
        prcp_dict = {}
        prcp_dict[date] = prcp
        year_prcp.append(prcp_dict)

    return jsonify(year_prcp)
    

## Define the list of stations page
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations recording weather data"""

    # Create a session from python to the database
    session = Session(engine)

    #Query a list of stations from the station table
    station_names = session.query(station.name).all()

    session.close()

    all_names = list(np.ravel(station_names))

    return jsonify(all_names)

## Define the tobs page
@app.route("/api/v1.0/tobs")
def tobs():

    # Create a session link
    session = Session(engine)

    # Query temperature data for the last year of recorded data at the most active station
    past_year_temp = session.query(measurement.date, measurement.tobs).\
    filter((measurement.date >= dt.date(2016, 8 , 23)) & (measurement.station == 'USC00519281')).all()

    # Record only as a list of temperatures as indicated in the instructions
    temperature = [temp[1] for temp in past_year_temp]

    session.close()

    tobs = list(np.ravel(temperature))

    return jsonify(tobs)

# Define a page for average temperatures on 8/23/2016
@app.route("/api/v1.0/2016.8.23")
def start():

    # Create a session link
    session = Session(engine)

    # Query minimun, maximum, and average temperature for the date one year prior to the last recorded measurement
    start_stats = [func.min(measurement.tobs),
                   func.avg(measurement.tobs),
                   func.max(measurement.tobs)]

    one_year_temp = session.query(*start_stats).\
                    filter(measurement.date == dt.date(2016, 8, 23)).all()
    
    session.close()
    
    for min, avg, max in one_year_temp:
        temp_dict = {}
        temp_dict['Minimum Temp'] = min
        temp_dict['Average Temp'] = avg
        temp_dict['Maximum Temp'] = max
    
    return jsonify(temp_dict)
    
#Define a page for average temperatures on 8/23/2016 - 8/23/2017
@app.route("/api/v1.0/2016.8.23/2017.8.23")
def start_end():

    #Create a session link
    session = Session(engine)

    # Query minimum, maximum, and average temperature for the entire last year of data
    start_stats = [func.min(measurement.tobs),
                   func.avg(measurement.tobs),
                   func.max(measurement.tobs)]
    
    # Indicate all dates greater than the start date
    total_year_temp = session.query(*start_stats).\
                    filter(measurement.date >= dt.date(2016, 8, 23)).all()
    
    session.close()
    
    # Print min, avg, and max with their appropriate labels as a dictionary
    for min, avg, max in total_year_temp:
        temp_dict = {}
        temp_dict['Minimum Temp'] = min
        temp_dict['Average Temp'] = avg
        temp_dict['Maximum Temp'] = max

    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)