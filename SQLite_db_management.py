#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
import sqlite3


# Establecemos conexión a la base de datos SQLite:
def con_sqlite_db(sqlite_db):
    # Abre conexion con la base de datos
    conexion = sqlite3.connect(sqlite_db)
    return conexion
