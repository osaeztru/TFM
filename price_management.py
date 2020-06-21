#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function


#Calculamos el precio de la reserva y de la limpieza en función del número de huéspedes, de habitaciones y de noches:
def get_booking_price(personas, habitaciones, noches):
    if personas == 1 and habitaciones == 1:
        price = 70*noches
        cleaning = 70
    if personas == 2 and habitaciones == 1:
        price = 70*noches
        cleaning = 75
    if personas == 2 and habitaciones == 2:
        price = 75*noches
        cleaning = 75
    if personas == 3 and habitaciones == 2:
        price = 85*noches
        cleaning = 80
    if personas == 3 and habitaciones == 3:
        price = 90*noches
        cleaning = 80
    if personas == 4 and habitaciones == 2:
        price = 100*noches
        cleaning = 85
    if personas == 4 and habitaciones == 3:
        price = 105*noches
        cleaning = 85
    if personas == 4 and habitaciones == 4:
        price = 110*noches
        cleaning = 85
    if personas == 5 and habitaciones == 3:
        price = 115*noches
        cleaning = 90
    if personas == 5 and habitaciones == 4:
        price = 120*noches
        cleaning = 90
    if personas == 6 and habitaciones == 3:
        price = 130*noches
        cleaning = 95
    if personas == 6 and habitaciones == 4:
        price = 135*noches
        cleaning = 95
    if personas == 7 and habitaciones == 4:
        price = 145*noches
        cleaning = 100
    if personas == 8 and habitaciones == 4:
        price = 160*noches
        cleaning = 100
    else:
        price == 0
        cleaning == 0
    
    return price, cleaning
