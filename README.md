# sqlalchemy-challenge
![surfs-up.png](Images/surfs-up.png)

# Background
[Project Details](project_instructions_README.md)

# Project Information
This project is broken up into the following sections:
### Climate Analysis and Exploration
    This was performed in the jupyter notebook climate.ipynb.  SQLAlchemy create_engine was utilized to connect to hawaii.sqlite data and `automap_base()` to reflect tables into classes with a reference to those classes called `Station` and `Measurement`.
    * Precipitation Analysis

    * Station Analysis
### Climate App
    This logic is in the python program app.py.   This program can be executed using python. The welcome page can be accessed via http://127.0.0.1:5000/
    The following routes are available for this app:
    
| Route                               | Description    
| ----------------------------------- |-------------------- |
|  `/`                                | Lists all available routes.  | 
| `/api/v1.0/precipitation`           | Lists the final twelve months of precipitation amounts for all stations (date, prcp).|
| `/api/v1.0/stations`                | Lists information about all stations (station, name, longitude, latitude, elevation). |
| `/api/v1.0/tobs`                    | Lists the final twelve months of temperature data for the most active station (date, temperature). |
| `/api/v1.0/<start>`                 | Lists the min, max, average temperature from the given start date to the end of the dataset (start date, most active station min temp, max temp, average temp). |
| `/api/v1.0/<start>/<end>`           | Lists the min, max, average temperature between the given start date and end date (start date, end date, most active station min temp, max temp, average temp).  |







### Bonus
    This analysis was performed in the jupyter notebook climate.ipynb.  
    * Temperature Analysis I
    * Temperature Analysis II
    * Daily Rainfall Average