# Geo Hiking Track Analyzer

This Python-based project is designed for handling and analyzing geographic data, specifically GPS track points and waypoints. It provides a comprehensive framework for working with this data, including their time, latitude, longitude, and elevation.

## Usage

To use the `cli.py` script, you need to provide the path to the GPX file you want to load and the directory where you want to save the output map. You can do this using the `--gpx-file` and `--output-map` options, respectively.

Here's an example of how to use the `cli.py` script:

```bash
python cli.py --gpx-file /path/to/your/gpx/file --output-map /path/to/output/directory
```
This command will parse the GPX file, analyze the tracks, generate a map with the tracks, rest points, and waypoints, and save the map to the specified output directory.  Please ensure that the GPX file exists and the output directory is writable before running the command.
Please replace `/path/to/your/gpx/file` and `/path/to/output/directory` with the actual paths to your GPX file and output directory, respectively.

## Developer

### Packages

#### geo_object/geo_point

The `geo_object/geo_point` package is a collection of modules that define various classes for handling and manipulating geographic data, specifically GPS track points and waypoints.

- `basic_point.py`: Defines the `BasicPoint` class, which serves as a base for all other types of geographic GPS points. It includes properties for time, latitude, longitude, and elevation.

- `raw_geo_points.py`: Contains the `WayPoint` and `RawTrkPoint` classes, which extend the `BasicPoint` class. The `WayPoint` class includes an additional property for notes, while the `RawTrkPoint` class represents raw track point data extracted directly from GPX files.

- `analyzed_geo_points.py`: Contains classes for the analyzed geographic points. The `AnalyzedTrkPoint` class extends the `BasicPoint` class and includes additional properties for displacement information. The `RestTrkPoint` class represents a resting point in the track, and the `RestTrkPointCandidate` and `SeedRestPoint` classes are used for identifying resting points in the track.

The `geo_object/geo_point` package follows a typical Object-Oriented Programming (OOP) design, with classes representing different entities (like points and tracks) and their behaviors. The use of inheritance (with the `BasicPoint` class serving as a base class) helps to reduce code duplication and makes the code easier to understand and maintain.

The package also follows good coding practices such as using docstrings for documentation, raising exceptions for error handling, and using type hints for function parameters and return types. This makes the code more robust and easier to work with.

#### geo_object/geo_tracks

The `geo_object/geo_tracks` package is a collection of modules that define various classes for handling and manipulating geographic track data.

- `basic_track.py`: Defines the `BasicTracks` class, which serves as a base for all other types of geographic tracks. It includes methods for adding track points, getting track points, and calculating total time spent.

- `raw_geo_tracks.py`: Contains the `RawTracks` and `RawTrackObject` classes, which extend the `BasicTracks` class. The `RawTracks` class represents raw track data extracted directly from GPX files. The `RawTrackObject` class is a container for holding a track composed by the list of `RawTrkPoint` and `WayPoint`.

- `analyzed_geo_tracks.py`: Contains classes for the analyzed geographic tracks. The `AnalyzedTracks` class extends the `BasicTracks` class and includes additional methods for total integral xy displacement. The `AnalyzedTrackObject` class extends the `RawTrackObject` class and includes additional properties for rest points, first point hours, great turn points, and great turn vectors.

The `geo_object/geo_tracks` package follows a typical Object-Oriented Programming (OOP) design, with classes representing different entities (like tracks) and their behaviors. The use of inheritance (with the `BasicTracks` class serving as a base class) helps to reduce code duplication and makes the code easier to understand and maintain.

The package also follows good coding practices such as using docstrings for documentation, raising exceptions for error handling, and using type hints for function parameters and return types. This makes the code more robust and easier to work with.

#### Example

To use these packages, import the desired classes and create instances as needed. For example, to create a new `WayPoint`:

```python
from src.geo_objects.geo_points.raw_geo_points import WayPoint

waypoint = WayPoint(time, lat, lon, elev, note)

```

To use these packages, import the desired classes and create instances as needed. For example, to create a new `RawTrackObject`:

```python
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint, WayPoint

raw_track_object = RawTrackObject()
raw_track_object.add_track_point(RawTrkPoint(time, lat, lon, elev))
raw_track_object.add_way_point(WayPoint(time, lat, lon, elev, note))
```

### geoanalyzer/tracks

The `geoanalyzer/tracks` package is a collection of modules that provide functionalities for analyzing geographic track data.

- `track_analyzer.py`: This module contains the `TrackAnalyzer` class which is responsible for analyzing raw track data. It smooths the track data, performs analysis, and identifies rest points. The module also includes several helper functions for calculating numerical differences, smoothing tracks, and finding rest points.

- `gps_parser.py`: This module contains the `GpxParser` class which is used for extracting data from GPX files. It parses the GPX file and extracts geographical data, including waypoints and track points. The extracted data is used to populate a `RawTrackObject` with instances of `WayPoint` and `RawTrkPoint`, which can then be further processed or analyzed.

Here's an example of how to use the `TrackAnalyzer` class:

```python
from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject

# Assume raw_track_object is an instance of RawTrackObject
analyzer = TrackAnalyzer(raw_track_object)
analyzed_tracks = analyzer.get_main_track()

```

## Sample GPS Data

Here's a small sample of GPS data in GPX format. This data can be used to demonstrate the features of the `geoanalyzer` package. The GPX file format is a standard GPS data format that contains waypoints, routes, and tracks.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="GitHub Copilot">
  <metadata>
    <name>Sample Track</name>
    <desc>This is a sample track for demonstration purposes.</desc>
  </metadata>
  <trk>
    <name>Sample Track</name>
    <trkseg>
      <trkpt lat="37.422289" lon="-122.084053">
        <ele>30.0</ele>
        <time>2022-01-01T00:00:00Z</time>
      </trkpt>
      <trkpt lat="37.42231" lon="-122.084107">
        <ele>31.0</ele>
        <time>2022-01-01T00:01:00Z</time>
      </trkpt>
      <trkpt lat="37.422319" lon="-122.08422">
        <ele>32.0</ele>
        <time>2022-01-01T00:02:00Z</time>
      </trkpt>
      <!-- More track points can be added here -->
    </trkseg>
  </trk>
  <wpt lat="37.422289" lon="-122.084053">
    <ele>30.0</ele>
    <time>2022-01-01T00:00:00Z</time>
    <name>Start Point</name>
  </wpt>
  <wpt lat="37.422319" lon="-122.08422">
    <ele>32.0</ele>
    <time>2022-01-01T00:02:00Z</time>
    <name>End Point</name>
  </wpt>
  <!-- More waypoints can be added here -->
</gpx>
```


## find_rest_point Function

The `find_rest_point` function is a part of the `track_analyzer` module and is designed to identify rest points from a list of GPS track points. 

A rest point is a location where the tracked object (for example, a person or vehicle) has stopped moving for a significant period of time. Identifying rest points can be useful in various applications, such as analyzing travel patterns or detecting unusual behavior.

The function takes as input a list of track points, where each track point is an instance of the `BasicPoint` class or its subclasses. Each track point represents a location at a specific time, and includes attributes such as latitude, longitude, and speed.

The process of finding rest points involves the following steps:

1. **Rest Point Candidate Identification**: The function first identifies "Rest Point Candidates". A Rest Point Candidate is a point where the speed is less than 0.1. If the following point's speed is also less than 0.1, it is considered as a second Rest Point Candidate. If the following point's speed is greater than 0.1, the function checks if the total X, Y drifting distance is less than 20 meters. If it is, this high-speed point is considered as an anomaly and is tolerated.

2. **SeedPoint Creation**: If the total accumulated time is greater than 60 seconds and the total drifting is less than 20 either in X or Y distance, the function creates a SeedPoint. A SeedPoint is a point that satisfies certain conditions and is used as a starting point for creating a RestTrkPoint.

3. **RestTrkPoint Creation**: Once a SeedPoint is found, the function creates a RestTrkPoint. A RestTrkPoint represents a confirmed rest point and includes information such as location (latitude, longitude, elevation) and time (start time, end time). The location of the RestTrkPoint is taken from the SeedPoint's location. The RestTrkPoint collection is completed when the last point is more than 20 meters away from the SeedPoint location and the moving speed is greater than 0.1.

The function returns a list of RestTrkPoints, representing all the rest points identified from the input list of track points.