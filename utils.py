"""
Utils for making maps with ipyvolume.

This contains functions to convert between spherical latitude/longitude
and Cartesian x, y, z coordinates, and some functions to extract data
from GeoJSON (or TopoJSON, a slightly more compact version of GeoJSON).
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
    x = radius * cos_lat * sin(lon)
    y = radius * sin(lat)
    z = radius * cos_lat * cos(lon)
    return (x, y, z)


def lonlat2xyz(lon, lat, radius=1, unit='deg'):
    "Convert lat/lon pair to Cartesian x/y/z triple."

    if unit == 'deg':
        lat = lat * pi_div_180
        lon = lon * pi_div_180
    cos_lat = cos(lat)

    x = radius * cos_lat * sin(lon)
    y = radius * sin(lat)
    z = radius * cos_lat * cos(lon)
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
    "Yield all points in some GeoJSON/TopoJSON as [lon, lat] coordinate pairs."

    gj_type = gj['type']
    
    if gj_type == 'Point':
        yield gj['coordinates']
    elif gj_type in ['MultiPoint', 'LineString']:
        for coord in gj_coords:  # FIXME
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
        msg = f'Unkown GeoJSON/TopoJSON type: {gj_type}'
        raise ValueError(msg)

            
def extract_lines(gj: dict):
    """
    Yield lines in some GeoJSON/TopoJSON as lists of [lon, lat] coordinate pairs.

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
    elif gj_type == 'Topology':
        transform = gj.get('transform', {})
        scale = transform.get('scale', [1.0, 1.0])
        translate = transform.get('translate', [0.0, 0.0])
        for arc in gj['arcs']:
            line = []
            prev = [0, 0]
            for point in arc:
                prev[0] += point[0]
                prev[1] += point[1]
                line.append((prev[0] * scale[0] + translate[0], prev[1] * scale[1] + translate[1]))
            yield line
    elif gj_type in ['Point', 'MultiPoint']:
        pass
    else:
        msg = f'Unknown GeoJSON/TopoJSON type: {gj_type}'
        raise ValueError(msg)
