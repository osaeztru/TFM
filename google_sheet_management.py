#!/usr/bin/env python
# -*- coding: utf-8 -*-


#pip install gspread
#pip install oauth2client
#pip install gspread_dataframe


from __future__ import print_function
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# Establecemos conexion a la hoja de Google Sheet donde se vuelcan los datos de nuestro Google Form:
def con_google_sheet(SCOPE, SECRETS_FILE, SPREADSHEET):
    # Authenticate using the signed key
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SECRETS_FILE,SCOPE)
    gc = gspread.authorize(credentials)

    # Find a workbook by name and open the first sheet
    workbook = gc.open(SPREADSHEET)
    # Get the first sheet
    sheet = workbook.sheet1
    return sheet

# Extraemos todos los datos de Google Sheet y los almacenamos en un dataframe de Pandas
def get_google_sheet_data(sheet, SPREADSHEET):
    # Extract all of the values into pandas dataframe "data"
    data = pd.DataFrame(sheet.get_all_records())
    
    # Create "Read" column if it doesn't exist
    if not 'Read' in data.columns:
        data = data.assign(Read = None)
    
    # Get new books (when Read is empty) into dataframe "data_new":
    data_new = data.loc[data['Read'] == '']
    
    #update Read = 'Y' in dataframe "data":
    data['Read'] = data['Read'].replace([''], 'Y')
    
    # Realizamos tratamientos específicos para cada formulario:
    if SPREADSHEET == 'Respuestas_Reservas_clientes' or SPREADSHEET == 'Respuestas_Reservas_intermediarios':
        #Como el numero de habitaciones viene en diferentes campos según el número de huéspedes, lo agregamos todo en un nuevo campo llamado "total_num_hab"
        data_new = data_new.assign(total_num_hab = None)
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 1, 'total_num_hab'] = data_new['Número de habitaciones 1']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 2, 'total_num_hab'] = data_new['Número de habitaciones 2']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 3, 'total_num_hab'] = data_new['Número de habitaciones 3']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 4, 'total_num_hab'] = data_new['Número de habitaciones 4']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 5, 'total_num_hab'] = data_new['Número de habitaciones 5']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 6, 'total_num_hab'] = data_new['Número de habitaciones 5']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 7, 'total_num_hab'] = data_new['Número de habitaciones 6']
        data_new.loc[data_new['Número de huéspedes'].astype(int) == 8, 'total_num_hab'] = data_new['Número de habitaciones 6']
        data_new = data_new.drop(['Número de habitaciones 1', 'Número de habitaciones 2', 'Número de habitaciones 3', 'Número de habitaciones 4', 'Número de habitaciones 5', 'Número de habitaciones 6'], axis=1)
    
    #Ordenamos las columnas del dataframe "data" para que esten en el mismo orden que la hoja de Google Sheet que vamos a updatear:
    if SPREADSHEET == 'Respuestas_Reservas_clientes':
        data = data[['Marca temporal', 'Fecha de entrada', 'Fecha de salida', 'Cunas', 'Número de huéspedes', 'Número de habitaciones 1', 'Número de habitaciones 2', 'Número de habitaciones 3', 'Número de habitaciones 4', 'Número de habitaciones 5', 'Número de habitaciones 6', 'DNI / Pasaporte', 'Nombre', 'Apellidos', 'Email', 'Teléfono de contacto', 'País', 'Titular de la tarjeta', 'Tipo de tarjeta', 'Número de tarjeta', 'Fecha de caducidad', 'Código CVC', 'Read']]
    elif SPREADSHEET == 'Respuestas_Reservas_intermediarios':
        data = data[['Marca temporal', 'Intermediario', 'Fecha de entrada', 'Fecha de salida', 'Cunas', 'Número de huéspedes', 'Número de habitaciones 1', 'Número de habitaciones 2', 'Número de habitaciones 3', 'Número de habitaciones 4', 'Número de habitaciones 5', 'Número de habitaciones 6', 'DNI / Pasaporte', 'Nombre', 'Apellidos', 'Email', 'Teléfono de contacto', 'País', 'Titular de la tarjeta', 'Tipo de tarjeta', 'Número de tarjeta', 'Fecha de caducidad', 'Código CVC', 'Read']]
        
    elif SPREADSHEET == 'Respuestas_Encuesta_satisfacción':
        data = data[['Marca temporal', 'Satisfacción', 'Expectativa', 'Repetiría', 'Recomendaciones', 'Habitación', 'Limpieza', 'Relación calidad / precio', 'Confort', 'Entorno', 'Accesibilidad', 'Ubicación', 'Equipamiento', 'Segmento', 'Redes sociales', 'Comentario', 'Actividades', 'P.N. Garajonay', 'Recomendación P.N.', 'ID reserva', 'Read']]
    
    # Update Google Sheet with dataframe "data":
    set_with_dataframe(sheet, data)
    
    return data_new

