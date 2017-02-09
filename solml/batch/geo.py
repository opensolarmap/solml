"""Provide common functions to work with geographic data.

This module provides functions to convert geographic coordinates to and from
cartographic coordinates. It provides a wrapper on geographiclib to compute
great-circle distances. geographiclib provides enhanced convergence compared to
the Vincenty algorithm.

A point on the earth can be located using geographic coordinates or
cartographic coordinates.

Geographic coordinates locate a point on a spheroid model of the earth with
two angles : latitude (phi) and longitude (lambda). There exist several
spheroid models of the earth. RGF93 is the standard in France. The world
standard is WGS84. However, the two references are very close, with a gap
smaller than 10 cm. Therefore, the two systems can be used interchangeably in
most applications.

Cartographic coordinates are used to map points to a planar map, with two
scalars : X and Y. A projection maps geographic coordinates to cartographic
coordinates. The projection Lambert 93 is used in France. It uses the RGF93
reference.

References :
http://geographiclib.sourceforge.net/
https://fr.wikipedia.org/wiki/Projection_conique_conforme_de_Lambert
http://geodesie.ign.fr/contenu/fichiers/documentation/rgf93/Lambert-93.pdf
http://geodesie.ign.fr/contenu/fichiers/documentation/algorithmes/notice/NTG_71.pdf
"""

from math import cos, sin, atan, tan, pi, sqrt, pow, log
from geographiclib.geodesic import Geodesic


# Define RGF93 and Lambert 93 constants

a = 6378137.
f = 1./298.257222101
phi1_deg = 44.
phi2_deg = 49.
lambd0_deg = 3.
phi0_deg = 46.5
x0 = 700000.
y0 = 6600000.


# Precompute some values

def deg2rad(theta):
    return (theta/180.)*pi

def rad2deg(theta):
    return (theta/pi)*180.

phi1 = deg2rad(phi1_deg)
phi2 = deg2rad(phi2_deg)
lambd0 = deg2rad(lambd0_deg)
phi0 = deg2rad(phi0_deg)
b = a*(1.-f)
e = sqrt(pow(a, 2.) - pow(b, 2.))/a

n = (
        (
            log(cos(phi2)/cos(phi1))
            +
            0.5*log(
                (1.-pow(e, 2.)*sin(phi1))
                /
                (1.-pow(e, 2.)*sin(phi2))
            )
        )
        /
        log(
            (tan(phi1*0.5+pi/4.)*pow((1.-e*sin(phi1)), e*0.5)*pow((1.+e*sin(phi2)), e*0.5))
            /
            (tan(phi2*0.5+pi/4.)*pow((1.+e*sin(phi1)), e*0.5)*pow((1.-e*sin(phi2)), e*0.5))
        )
    )
rho0 = (
        ((a*cos(phi1))/(n*sqrt(1.-pow(e, 2.)*pow(sin(phi1), 2.))))
        *
        pow(tan(phi1*0.5+pi/4.)*pow((1.-e*sin(phi1))/(1.+e*sin(phi1)), e*0.5), n)
    )

def cot(x):
    return 1./tan(x)  # = cos(x)/sin(x)

def function_rho(phi):
    return rho0 * pow(cot(phi*0.5+pi/4.)*pow((1.+e*sin(phi))/(1.-e*sin(phi)), e*0.5), n)

rho_phi0 = function_rho(phi0)


# Conversion functions

def carto2geo(x, y, precision_deg=1e-12):
    """Convert cartographic coordinates to geographic coordinates.

    Uses the inverse Lambert 93 projection. The coordinates are based on the
    RGF93 system. The is compatible (for most applications) with the WGS84
    system.
    """
    precision = deg2rad(precision_deg)

    rho = sqrt(pow(x-x0, 2.) + pow(y0-y+rho_phi0, 2.))
    theta = 2.*atan((x-x0)/(y0-y+rho_phi0+rho))

    lambd = theta/n + lambd0

    phi_last = 0.
    phi = 2*atan(pow(rho0/rho, 1./n))
    while abs(phi-phi_last) >= precision:
        phi_last = phi
        phi = 2*atan(pow(rho0/rho, 1./n)*pow((1.+e*sin(phi))/(1.-e*sin(phi)), e*0.5))-pi*0.5

    phi_deg = rad2deg(phi)
    lambd_deg = rad2deg(lambd)
    return (phi_deg, lambd_deg)


def geo2carto(phi_deg, lambd_deg):
    """Convert geographic coordinates to cartographic coordinates.

    Uses the Lambert 93 projection. The coordinates are based on the
    RGF93 system. The is compatible (for most applications) with the WGS84
    system.
    """

    phi = deg2rad(phi_deg)
    lambd = deg2rad(lambd_deg)

    theta = n*(lambd-lambd0)
    rho = function_rho(phi)

    x = x0 + rho*sin(theta)
    y = y0 + rho_phi0 - rho*cos(theta)

    return (x, y)


# Distance functions

def distance_geo(phi_a_deg, lambd_a_deg, phi_b_deg, lambd_b_deg):
    """Compute the great-circle distance between two points.

    This function takes WGS84 coordinates.
    """
    return Geodesic.WGS84.Inverse(phi_a_deg, lambd_a_deg, phi_b_deg, lambd_b_deg)['s12']

def distance_carto(x_a, y_a, x_b, y_b):
    """Compute the great-circle distance between two points.

    This function takes Lambert 93 coordinates.
    """
    phi_a_deg, lambd_a_deg = carto2geo(x_a, y_a)
    phi_b_deg, lambd_b_deg = carto2geo(x_b, y_b)
    return distance_geo(phi_a_deg, lambd_a_deg, phi_b_deg, lambd_b_deg)
