.. Geo Hiking Track documentation master file, created by
   sphinx-quickstart on Mon Apr  1 21:08:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Geo Hiking Track's documentation!
============================================


The Geo Hiking Track Analyzer's Web API is a Python-based API designed for handling and analyzing geographic data, specifically GPS track points and waypoints. It provides a comprehensive framework for working with this data, including their time, latitude, longitude, and elevation.

This API is built around several key packages:

1. `geo_object/geo_point`: This package contains modules that define various classes for handling and manipulating geographic data. It includes classes like `BasicPoint`, `WayPoint`, `RawTrkPoint`, and others. These classes represent different types of geographic GPS points and provide methods for manipulating and analyzing these points.

2. `geo_object/geo_tracks`: This package contains modules that define various classes for handling and manipulating geographic track data. It includes classes like `BasicTracks`, `RawTracks`, `RawTrackObject`, and others. These classes represent different types of geographic tracks and provide methods for adding track points, getting track points, and calculating total time spent.

3. `geoanalyzer/tracks`: This package contains modules that provide functionalities for analyzing geographic track data. It includes classes like `TrackAnalyzer` and `GpxParser`. The `TrackAnalyzer` class is responsible for analyzing raw track data, smoothing the track data, performing analysis, and identifying rest points. The `GpxParser` class is used for extracting data from GPX files.

4. `visualization/map_drawer`: This module is responsible for creating interactive maps using the Folium library. It contains the `FoliumMapDrawer` class which provides an easy-to-use interface for drawing geographic data on a map.

The project follows a typical Object-Oriented Programming (OOP) design, with classes representing different entities (like points and tracks) and their behaviors. The use of inheritance helps to reduce code duplication and makes the code easier to understand and maintain.

The project also follows good coding practices such as using docstrings for documentation, raising exceptions for error handling, and using type hints for function parameters and return types. This makes the code more robust and easier to work with.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
