#!/usr/bin/env python
# -*- coding: utf-8 -*-


import google_sheet_management
import SQLite_db_management
import booking_management


# use creds to create a client to interact with the Google Drive API
SCOPE = ['https://www.googleapis.com/auth/drive']
SECRETS_FILE = 'Pbpython-key.json'
SPREADSHEET = "Respuestas_Reservas_intermediarios"

# SQLite database file
sqlite_db = 'los_aromos.db'

# Indicamos el formulario desde donde es usado este script (formulario de intermediario):
used = 'interm'

def main():
    sheet = google_sheet_management.con_google_sheet(SCOPE, SECRETS_FILE, SPREADSHEET)
    data_new = google_sheet_management.get_google_sheet_data(sheet, SPREADSHEET)
    conexion = SQLite_db_management.con_sqlite_db(sqlite_db)
    booking_management.update_booking(used, data_new, conexion)


main();
