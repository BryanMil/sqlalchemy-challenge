# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# Create our session (link) from Python to the DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measure = Base.classes.measurement
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"above add /YYYY-MM-DD<br/>"
        f"/api/v1.0/<start><br/>"
        f"above add /YYYY-MM-DD/YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measure.prcp, Measure.date).all()
    session.close()
  

    pquery = []
    for prcp, date in results:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        pquery.append(precipitation_dict)

    return jsonify(pquery) 


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results1 = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation ).all()
    session.close()
  
    squery = []
    for id, station, name, latitude, longitude, elevation in results1:
        station_dict = {}
        station_dict ["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation

        squery.append(station_dict)

    return jsonify(squery) 


@app.route("/api/v1.0/tobs")
def temp():

     # Create our session (link) from Python to the DB
    session = Session(engine)

    results3 = session.query(Measure.tobs, Measure.date, Measure.station).filter(func.strftime("%Y-%m-%d", Measure.date) >= "2016-08-23").filter(Measure.station == "USC00519281").all()
     
    session.close()
   
    tquery = []
    for date, tobs,station in results3:
        temp_dict = {}
        temp_dict ["date"] = date
        temp_dict ["tobs"] = tobs
        temp_dict ["station"] = station
        

        tquery.append(temp_dict)

    return jsonify(tquery) 

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_for_date_range(start, end):

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    # Create our session (link) from Python to the DB.

    session = Session(engine)

    # If we have both a start date and an end date.
    if end != None:
        temperature_data = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
            filter(Measure.date >= start).filter(
            Measure.date <= end).all()
    # If we only have a start date.
    else:
        temperature_data = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)).\
            filter(Measure.date >= start).all()

    session.close()

 # Convert the query results to a list.
    temperature_list = []
    no_temperature_data = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temperature_data = True
        temperature_list.append(min_temp)
        temperature_list.append(avg_temp)
        temperature_list.append(max_temp)
    # Return the JSON representation of dictionary.
    if no_temperature_data == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(temperature_list)


if __name__ == '__main__':
    app.run(debug=True)