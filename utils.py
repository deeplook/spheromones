"""
Utils for making maps with ipyvolume.

This contains functions to convert between spherical latitude/longitude
and Cartesian x, y, z coordinates, and some functions to extract data
from GeoJSON.
"""

from typing import Tuple
from math import radians, log, sin, cos, tan, asin, atan2, pi

pi_div_180 = pi / 180


def latlon2xyz(
    lat: float, 
    lon: float, 
    radius: float=1, 
    unit: str='deg'
) -> Tuple[float, float, float]:
    "Convert lat/lon pair to Cartesian x/y/z triple."

    if unit == 'deg':
        lat = lat * pi_div_180
        lon = lon * pi_div_180
    cos_lat = cos(lat)
    x = radius * cos_lat * cos(lon)
    y = radius * cos_lat * sin(lon)
    z = radius * sin(lat)
    return (x, y, z)


# like latlon2xyz() but with swapped parameters for saving the swapping elsewhere
def lonlat2xyz(
    lon: float, 
    lat: float, 
    radius: float=1, 
    unit: str='deg'
) -> Tuple[float, float, float]:
    "Convert lat/lon pair to Cartesian x/y/z triple."

    if unit == 'deg':
        lat = lat * pi_div_180
        lon = lon * pi_div_180
    cos_lat = cos(lat)
    x = radius * cos_lat * cos(lon)
    y = radius * cos_lat * sin(lon)
    z = radius * sin(lat)
    return (x, y, z)


def xyz2latlon(
    x: float, 
    y: float,
    z: float,
    radius: float=1,
    unit: str='deg'
) -> Tuple[float, float]:
    "Convert Cartesian x/y/z triple to lat/lon pair."

    lat = asin(z / radius)
    lon = atan2(y, x)
    if unit == 'deg':
        lat = lat / pi_div_180
        lon = lon / pi_div_180
    return (lat, lon)

def extract_coords(gj: dict):
    "Yield all points in some GeoJSON as [lon, lat] coordinate pairs."

    gj_type = gj['type']
    
    if gj_type == 'Point':
        yield gj_coords
    elif gj_type in ['MultiPoint', 'LineString']:
        for coord in gj_coords:
            yield coord
    elif gj_type in ['MultiLineString', 'Polygon']:
        for line in gj['coordinates']:
            for coord in line:
                yield coord
    elif gj_type == 'MultiPolygon':
        for poly in gj['coordinates']:
            for line in poly:
                for coord in line:
                    yield coord
    elif gj_type == 'GeometryCollection':
        for geom in gj['geometries']:
            for coord in extract_coords(geom):
                yield coord
    elif gj_type == 'FeatureCollection':
        for feat in gj['features']:
            for coord in extract_coords(feat):
                yield coord
    elif gj_type == 'Feature':
        geom = gj['geometry']
        for coord in extract_coords(geom):
            yield coord
    else:
        msg = f'Unkown GeoJSON type: {gj_type}'
        raise ValueError(msg)

            
def extract_lines(gj: dict):
    """
    Yield lines in some GeoJSON as lists of [lon, lat] coordinate pairs.

    This ignores Point and MultiPoint because they don't form lines.
    """
    gj_type = gj['type']

    if gj_type in ['LineString']:
        yield gj['coordinates']
    elif gj_type in ['MultiLineString', 'Polygon']:
        yield gj['coordinates']
    elif gj_type == 'MultiPolygon':
        for poly in gj['coordinates']:
            for line in poly:
                yield line
    elif gj_type == 'GeometryCollection':
        for geom in gj['geometries']:
            for line in extract_lines(geom):
                yield line
    elif gj_type == 'FeatureCollection':
        for feat in gj['features']:
            for line in extract_lines(feat):
                yield line
    elif gj_type == 'Feature':
        geom = gj['geometry']
        for line in extract_lines(geom):
            yield line
    else:
        msg = f'Unkown GeoJSON type: {gj_type}'
        raise ValueError(msg)
