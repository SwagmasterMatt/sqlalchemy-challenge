# Import the dependencies.
from flask import Flask, jsonify, request
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect , desc






#################################################
# Database Setup
#################################################

#create the engine
engine = create_engine("sqlite:///J:/UNC Bootcamp/sqlalchemy-challenge/Climate_Analysis/Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup+
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Query to get the first and last date
first_date = session.query(measurement.date).order_by(measurement.date).first()
last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
first_date = dt.datetime.strptime(first_date[0], '%Y-%m-%d')
last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
        f'Temperature Option 1: enter a start date between {first_date} and {last_date} to return temperatures after the start date<br/>'
        f'<form action="/api/v1.0/temp/start" method="post">'
        f'Start date: <input type="date" name="start_date">'
        f'<input type="submit" value="Submit"><br/>'
        f'</form>'
        f'Temperature Option 2: enter a start date and end date between {first_date} and {last_date} to return temperatures between the start and end date<br/>'
        f'<form action="/api/v1.0/temp/start/end" method="post">'
        f'Start date: <input type="date" name="start_date"><br/>'
        f'End date: <input type="date" name="end_date">'
        f'<input type="submit" value="Submit">'
        f'</form>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Starting from the most recent data point in the database. 
    session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= dt.date(2016, 8, 23)).all()

    # Jsonify the results with date as the key and prcp as the value.
    precipitation = {date: prcp for date, prcp in results}
        # Save the query results as a Pandas DataFrame. Explicitly set the column names
    df = pd.DataFrame(results, columns=['date', 'precipitation'])


    # Sort the dataframe by date
    df.set_index(df['date'], inplace=True)
    df = df.sort_index()
    dict = {
        "Text 1": "Results for Precipitation from 2016-08-23 to 2017-08-23",
        "Unordered Results": precipitation,
        "Text 2": "Results ordered by date",
        "Ordered Results": df.to_dict()
    }
    return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query to get the stations list
    stations = session.query(Station.station, Station.name).all()
    # Jsonify the results
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query to get the most active station
    most_active = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    # Query to get the last 12 months of temperature observation data (tobs).
    results = session.query(measurement.date, measurement.tobs, measurement.station).filter(measurement.date >= dt.date(2016, 8, 23)).filter(measurement.station == most_active[0]).all()
    # Jsonify the results
    return jsonify(results)



@app.route("/api/v1.0/temp/start", methods=['POST'])
def start():
    start = dt.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    
    #enforce the date is within the range
    try:
        if start >= first_date and start <= last_date:
            pass
    except ValueError:
        return f"Error: Date not in range. Please enter a date between {first_date} and {last_date}", 400
    

    # Query to get the min, avg, and max temperatures for a given start date.
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    # Jsonify the results
    return jsonify(results)

@app.route("/api/v1.0/temp/start/end", methods=['POST'])
def start_end():
    start = dt.datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end = dt.datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    
    #enforce the date is within the range
    try:
        if start >= first_date and end <= last_date:
            pass
    except ValueError:
        return f"Error: Date not in range. Please enter a date between {first_date} and {last_date}", 400
    
    # Query to get the min, avg, and max temperatures for a given start-end range.
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    # Jsonify the results
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)