import re


# from geographiclib.geodesic import Geodesic
# Geodesic.WGS84.Inverse(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
# {'lat1': 41.395883, 'lon1': 2.041667, 'lat2': 41.520833, 'lon2': 2.458333, 'a12': 0.3372916433849669,
# 's12': 37476.27220013839, 'azi1': 68.12834904653883, 'azi2': 68.40421426320225}
# lat1 = φ1, latitude of point 1 (degrees)
# lon1 = λ1, longitude of point 1 (degrees)
# azi1 = α1, azimuth of line at point 1 (degrees)
# lat2 = φ2, latitude of point 2 (degrees)
# lon2 = λ2, longitude of point 2 (degrees)
# azi2 = α2, (forward) azimuth of line at point 2 (degrees)
# s12 = s12, distance from 1 to 2 (meters)
# a12 = σ12, arc length on auxiliary sphere from 1 to 2 (degrees)


def maidenhead_to_coordinates(locator: str, grid_center: bool = True) -> (float, float):
    """
    Returns a tuple with the latitude and longitude of the Maidenhead locator
    AA00AA
    First letter: -180 (A) to 160 (R) degrees of longitude

    :param locator: then Maidenhead locator
    :param grid_center: if True, return the center of the grid
    :return: tuple with latitude and longitude
    """
    if not validate_locator(locator):
        raise TypeError("Wrong locator format")
    locator = locator.upper()

    # What to add if grid center is requested
    delta_latitude = 0
    delta_longitude = 0

    # First char:  -180 (A) to 160 (R) degrees of longitude
    # Length: 20 degrees
    longitude = -180 + (ord(locator[0]) - ord('A')) * 20

    # Second char:  -90 (A) to 80 (R) degrees of latitude
    # Length: 10 degrees
    latitude = -90 + (ord(locator[1]) - ord('A')) * 10

    # Third char: number from 0 to 9, two degrees of longitude each
    position = int(locator[2]) * 2
    longitude += position

    # Fourth char: number from 0 to 9, one degree of latitude each
    position = int(locator[3]) * 1
    latitude += position

    if grid_center:
        delta_longitude = 1
        delta_latitude = 0.5

    if len(locator) > 4:
        # Fifth char: letter from A to X, 24 positions, 2 / 24 degrees of longitude each
        position = (ord(locator[4]) - ord('A')) * 2 / 24
        longitude += position

        # Sixth char: letter from A to X, 24 positions, 1 / 24 degrees of latitude each
        position = (ord(locator[5]) - ord('A')) * 1 / 24
        latitude += position

        if grid_center:
            delta_longitude = 1 / 24
            delta_latitude = 1 / 48

    if len(locator) > 6:
        # Seventh char: number from 0 to 9, 2 / 240 degrees of longitude each
        position = int(locator[6]) * 2 / 240
        longitude += position

        # Eight char: number from 0 to 9, 1 / 240 degrees of latitude each
        position = int(locator[7]) * 1 / 240
        latitude += position

        if grid_center:
            delta_longitude = 1 / 240
            delta_latitude = 1 / 480

    if len(locator) > 8:
        # TODO: To be implemented
        if grid_center:
            delta_longitude = 1 / 240
            delta_latitude = 1 / 480

    return round(latitude + delta_latitude, 6), round(longitude + delta_longitude, 6)


def validate_locator(locator: str) -> bool:
    """
    Checks whether the given str is a well-formed locator:
        JN11
        JN11AJ / JN11aj
    up to the 10th character

    :param locator: string in Maidenhead locator format
    :return:
    """
    if not isinstance(locator, str):
        raise TypeError("locator must be a string")
    if len(locator) % 2 == 1:
        raise ValueError("locator must be an even characters string")
    if not 4 <= len(locator) <= 10:
        raise ValueError("locator must have between 4 and 10 characters")

    locator = locator.upper()

    # maiden = re.compile
    # (r'^([A-Ra-r]{2})(\d{2})($|[A-Xa-x][A-Xa-x]?$|([A-Xa-x][A-Xa-x])(?:$|\d{2}$|\d{2}([A-Xa-x][A-Xa-x])$))')
    maiden = re.compile(r'^([A-R]{2})(\d{2})($|[A-X][A-X]?$|([A-X][A-X])(?:$|\d{2}$|\d{2}([A-X][A-X])$))')
    return maiden.match(locator) is not None
