#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
import pandas as pd
from datetime import datetime
from datetime import timedelta

import price_management
import google_gmail_management


# Parte principal del programa donde se valida si ya existen reservas en las fechas solicitadas y se actualiza la base de datos:
def update_booking(used, data_new, conexion):
    # Extraemos las reservas que ya existen en la base de datos y las almacenamos en un Dataframe de pandas:
    reservas_db = pd.read_sql_query("SELECT fecha_entrada, fecha_salida FROM reservas where estado_reserva in ('confirmada', 'provisional')", conexion)
    # Abrimos el cursor a la base de datos
    cursor = conexion.cursor()
    #Recorremos el dataframe "data_new" que contiene las nuevas reservas enviadas en el formulario:
    for index, row in data_new.iterrows():
        #Inicializamos el valor de la variable "existe_reserva"
        existe_reserva = ''
        #Recorremos el dataframe "reservas_db" que contiene las reservas existentes en la base de datos:
        for index, fila in reservas_db.iterrows():
            #Guardamos y formateamos las variables de fecha de entrada de la reserva, fecha de entrada existente en base de datos y fecha de salida existente en base de datos:
            fecha_entrada_reserva = datetime.strptime(row['Fecha de entrada'], '%d/%m/%Y')
            fecha_entrada_bd = datetime.strptime(fila['fecha_entrada'], '%d/%m/%Y')
            fecha_salida_bd = datetime.strptime(fila['fecha_salida'], '%d/%m/%Y')
            #Existe reserva cuando la fecha de entrada de la reserva es mayor o igual a una fecha de entrada ya existente y menor a una fecha de salida ya existente:
            if fecha_entrada_reserva >= fecha_entrada_bd and fecha_entrada_reserva < fecha_salida_bd:
                existe_reserva = 'Y'
                #Salimos del bucle cuando encontramos que ya existe reserva en las mismas fechas
                break
            #En caso contrario, no existe una reserva actual en las mismas fechas
            else:
                existe_reserva = 'N'
        #Si existe reserva enviamos email indicando que no se puede realizar la reserva porque ya existe una reserva en esa fecha.
        if existe_reserva == 'Y':
            print("No se puede realizar la reserva. Ya existe una reserva en esa fecha: " + row['Fecha de entrada'])
            email_subject = 'Casa Rural Los Aromos - Reserva no confirmada'
            email_content = 'Hola, su reserva no se puede procesar porque no hay disponibilidad en las fechas solicitadas. Por favor, pruebe otras fechas. Gracias'
            #Enviamos el email al cliente cuando la reserva es directa desde la página web:
            if used == 'client':
                email_to = row['Email']
            #Enviamos el email al intermediario cuando la reserva proviene desde un intermediario:
            elif used == 'interm':
                nombre_interm = row['Intermediario']
                q_interm = """SELECT email FROM intermediarios where nombre = :nombre_interm"""
                email_to = cursor.execute(q_interm, {'nombre_interm': nombre_interm}).fetchone()[0]
            google_gmail_management.send_email(email_to, email_subject, email_content)
        #Si no existe reserva en esa fecha, procedemos a introducir los datos de la nueva reserva en la base de datos:
        elif existe_reserva == 'N':
            #Recuperamos los datos de cliente y tarjeta enviados en el formulario:
            cliente_doc = row['DNI / Pasaporte']
            cliente_nom = row['Nombre']
            cliente_ape = row['Apellidos']
            cliente_mail = row['Email']
            cliente_tel = row['Teléfono de contacto']
            cliente_pais = row['País']
            tarjeta_num = row['Número de tarjeta']
            tarjeta_cad = row['Fecha de caducidad']
            tarjeta_cvc = row['Código CVC']
            tarjeta_tit = row['Titular de la tarjeta']
            tarjeta_tipo = row['Tipo de tarjeta']
            #Comprobamos si existe cliente para insertar o actualizar los datos de tarjeta y cliente:
            q_cliente = """SELECT count(1) FROM clientes where DNI_pasaporte = :cliente_doc"""
            r_cliente = cursor.execute(q_cliente, {'cliente_doc': cliente_doc}).fetchone()[0]
            if r_cliente == 0:
                #No existe cliente
                print("No existe cliente")
                #Insertamos datos de la tarjeta en la tabla de "tarjetas":
                insert_tarjeta = """INSERT INTO tarjetas (num_tarjeta, fecha_cad, cod_cvc, titular, tipo, python) VALUES(:tarjeta_num, :tarjeta_cad, :tarjeta_cvc, :tarjeta_tit, :tarjeta_tipo, 1);"""
                cursor.execute(insert_tarjeta, {'tarjeta_num': tarjeta_num, 'tarjeta_cad': tarjeta_cad, 'tarjeta_cvc': tarjeta_cvc, 'tarjeta_tit': tarjeta_tit, 'tarjeta_tipo': tarjeta_tipo})
                #Recuperamos el valor de "idtarjeta" para posteriormente usarlo para la inserción del nuevo cliente en la tabla "clientes" y actualizamos el valor de la columna python a 0 en la tabla "tarjetas":
                idtarjeta = cursor.execute("SELECT idtarjeta FROM tarjetas where python = 1").fetchone()[0]
                update_tarjeta = """UPDATE tarjetas SET python = 0 where idtarjeta = :idtarjeta;"""
                cursor.execute(update_tarjeta, {'idtarjeta': idtarjeta})
                #Insertamos nuevo cliente en la tabla de "clientes":
                insert_cliente = """INSERT INTO clientes (DNI_pasaporte, nombre, apellidos, email, telefono, pais, idtarjeta, repite_estancia, python) VALUES(:cliente_doc, :cliente_nom, :cliente_ape, :cliente_mail, :cliente_tel, :cliente_pais, :idtarjeta, 'no', 0);"""
                cursor.execute(insert_cliente, {'cliente_doc': cliente_doc, 'cliente_nom': cliente_nom, 'cliente_ape': cliente_ape, 'cliente_mail': cliente_mail, 'cliente_tel': cliente_tel, 'cliente_pais': cliente_pais, 'idtarjeta': idtarjeta})
                conexion.commit()
            else:
                #Existe cliente
                print("Existe cliente")
                #Recuperamos el valor de idtarjeta del cliente desde la tabla "clientes":
                q_tarjeta = """SELECT idtarjeta FROM clientes where DNI_pasaporte = :cliente_doc"""
                idtarjeta = cursor.execute(q_tarjeta, {'cliente_doc': cliente_doc}).fetchone()[0]
                #Validamos si el cliente tiene asociado una tarjeta (clientes pre-migración):
                if idtarjeta != None:
                    #El cliente tiene una tarjeta asociada.
                    #Actualizamos en la tabla "tarjetas" los datos de la tarjeta enviados en el formulario:
                    update_tarjeta = """UPDATE tarjetas SET num_tarjeta = :tarjeta_num, fecha_cad = :tarjeta_cad, cod_cvc = :tarjeta_cvc, titular = :tarjeta_tit, tipo = :tarjeta_tipo where idtarjeta = :idtarjeta;"""
                    cursor.execute(update_tarjeta, {'tarjeta_num': tarjeta_num, 'tarjeta_cad': tarjeta_cad, 'tarjeta_cvc': tarjeta_cvc, 'tarjeta_tit': tarjeta_tit, 'tarjeta_tipo': tarjeta_tipo, 'idtarjeta': idtarjeta})
                    #Actualizamos en la tabla "clientes" los datos del cliente enviados en el formulario:
                    update_cliente = """UPDATE clientes SET nombre = :cliente_nom, apellidos = :cliente_ape, email = :cliente_mail, telefono = :cliente_tel, pais = :cliente_pais, repite_estancia = 'si' where DNI_pasaporte = :cliente_doc;"""
                    cursor.execute(update_cliente, {'cliente_nom': cliente_nom, 'cliente_ape': cliente_ape, 'cliente_mail': cliente_mail, 'cliente_tel': cliente_tel, 'cliente_pais': cliente_pais, 'cliente_doc': cliente_doc})
                else:
                    #El cliente no tiene tarjeta asociada
                    #Insertamos datos de la tarjeta en la tabla de "tarjetas":
                    insert_tarjeta = """INSERT INTO tarjetas (num_tarjeta, fecha_cad, cod_cvc, titular, tipo, python) VALUES(:tarjeta_num, :tarjeta_cad, :tarjeta_cvc, :tarjeta_tit, :tarjeta_tipo, 1);"""
                    cursor.execute(insert_tarjeta, {'tarjeta_num': tarjeta_num, 'tarjeta_cad': tarjeta_cad, 'tarjeta_cvc': tarjeta_cvc, 'tarjeta_tit': tarjeta_tit, 'tarjeta_tipo': tarjeta_tipo})
                    #Recuperamos el valor de "idtarjeta" para posteriormente usarlo para la inserción del nuevo cliente en la tabla "clientes" y actualizamos el valor de la columna python a 0 en la tabla "tarjetas":
                    idtarjeta_new = cursor.execute("SELECT idtarjeta FROM tarjetas where python = 1").fetchone()[0]
                    update_tarjeta = """UPDATE tarjetas SET python = 0 where idtarjeta = :idtarjeta_new;"""
                    cursor.execute(update_tarjeta, {'idtarjeta_new': idtarjeta_new})
                    #Actualizamos en la tabla "clientes" los datos del cliente enviados en el formulario y el "idtarjeta" que hemos insertado anteriormente en la tabla "tarjetas":
                    update_cliente = """UPDATE clientes SET nombre = :cliente_nom, apellidos = :cliente_ape, email = :cliente_mail, telefono = :cliente_tel, pais = :cliente_pais, idtarjeta = :idtarjeta_new, repite_estancia = 'si' where DNI_pasaporte = :cliente_doc;"""
                    cursor.execute(update_cliente, {'cliente_nom': cliente_nom, 'cliente_ape': cliente_ape, 'cliente_mail': cliente_mail, 'cliente_tel': cliente_tel, 'cliente_pais': cliente_pais, 'idtarjeta_new': idtarjeta_new, 'cliente_doc': cliente_doc})
                conexion.commit()
            #Una vez que hemos insertado o actualizado los datos del cliente y su tarjeta, recuperamos el valor de idcliente de la tabla "clientes":
            q_cliente = """SELECT idcliente FROM clientes where DNI_pasaporte = :cliente_doc"""
            idcliente = cursor.execute(q_cliente, {'cliente_doc': cliente_doc}).fetchone()[0]
            #Recuperamos los datos de la reserva enviados en el formulario:
            fecha_res = row['Marca temporal']
            fecha_ent = row['Fecha de entrada']
            fecha_sal = row['Fecha de salida']
            num_noches = (datetime.strptime(row['Fecha de salida'], '%d/%m/%Y')-datetime.strptime(row['Fecha de entrada'], '%d/%m/%Y')).days
            num_personas = row['Número de huéspedes']
            num_habitaciones = row['total_num_hab']
            cuna = row['Cunas']
            fecha = row['Marca temporal']
            #Recuperamos el valor de idintermediario dependiendo desde donde se haya llamado a este script (cliente o intermediario):
            if used == 'client':
                idintermediario = 3
            elif used == 'interm':
                nombre_interm = row['Intermediario']
                q_interm = """SELECT idintermediario FROM intermediarios where nombre = :nombre_interm"""
                idintermediario = cursor.execute(q_interm, {'nombre_interm': nombre_interm}).fetchone()[0]
            #Establecemos el valor de idalojamiento para "La Casa Rural Los Aromos":
            idalojamiento = 1
            #Calculamos el precio de la reserva y de la limpieza en función del numero de huéspedes, de habitaciones y de noches:
            importe = price_management.get_booking_price(num_personas, num_habitaciones, num_noches)[0]
            limpieza = price_management.get_booking_price(num_personas, num_habitaciones, num_noches)[1]
            importe_total = importe+limpieza
            gasto_limpieza = 65
            #Miramos si la fecha de entrada es menos de una semana para posteriormente insertar el resto de datos de la reserva.:
            fecha_entrada = datetime.strptime(row['Fecha de entrada'], '%d/%m/%Y')
            if fecha_entrada - datetime.now() < timedelta(days=7):
                print("Faltan menos de 7 días")
                #La fecha de entrada es en menos de una semana: el cliente ya no tiene derecho a reembolso de la reserva y se le puede hacer el cobro de la totalidad de la reserva.
                #Esto genera una reserva en estado "confirmada", una factura en estado "Pagada", un gasto de limpieza en "Pendiente" (hasta que la limpieza se lleve a cabo y sea pagada, que pasará a estado "Pagado") y un gasto de intermediario (si aplica) en estado "Pagado".
                #Insertamos la nueva reserva en la tabla de "reservas" en estado "confirmada":
                insert_reserva = """INSERT INTO reservas (idcliente, idintermediario, idalojamiento, estado_reserva, fecha_reserva, fecha_entrada, fecha_salida, num_noches, num_personas, num_habitaciones, cuna, importe, limpieza, python) VALUES(:idcliente, :idintermediario, :idalojamiento, 'confirmada', :fecha_res, :fecha_ent, :fecha_sal, :num_noches, :num_personas, :num_habitaciones, :cuna, :importe, :limpieza, 1);"""
                cursor.execute(insert_reserva, {'idcliente': idcliente, 'idintermediario': idintermediario, 'idalojamiento': idalojamiento, 'fecha_res': fecha_res, 'fecha_ent': fecha_ent, 'fecha_sal': fecha_sal, 'num_noches': num_noches, 'num_personas': num_personas, 'num_habitaciones': num_habitaciones, 'cuna': cuna, 'importe': importe, 'limpieza': limpieza})
                #Recuperamos el valor de "idreserva" y actualizamos el valor de la columna python a 1 en la tabla "reservas":
                idreserva = cursor.execute("SELECT idreserva FROM reservas where python = 1").fetchone()[0]
                update_reserva = """UPDATE reservas SET python = 0 where idreserva = :idreserva;"""
                cursor.execute(update_reserva, {'idreserva': idreserva})
                #Insertamos un nuevo registro en la tabla de "facturas" con estado "Pagada":
                insert_factura = """INSERT INTO facturas (idreserva, importe_total, estado, fecha, python) VALUES(:idreserva, :importe_total, 'Pagado', :fecha, 0);"""
                cursor.execute(insert_factura, {'idreserva': idreserva, 'importe_total': importe_total, 'fecha': fecha})
                #Insertamos un nuevo gasto de limpieza en la tabla "gastos" con estado "Pendiente":
                insert_gasto_limp = """INSERT INTO gastos (idreserva, concepto, importe, estado, python) VALUES(:idreserva, 'limpieza', :gasto_limpieza, 'Pendiente', 0);"""
                cursor.execute(insert_gasto_limp, {'idreserva': idreserva, 'gasto_limpieza': gasto_limpieza})
                #En caso de que el script se llame desde el formulario de "intermediarios", se genera gasto de intermediario en estado "Pagado":
                if used == 'interm':
                    #Obtenemos la comisión del intermediario y calculamos el importe de la misma:
                    q_comision = """SELECT comision FROM intermediarios where idintermediario = :idintermediario"""
                    comision = cursor.execute(q_comision, {'idintermediario': idintermediario}).fetchone()[0]
                    imp_comision = comision*importe
                    insert_gasto_interm = """INSERT INTO gastos (idreserva, concepto, importe, estado, fecha, python) VALUES(:idreserva, 'intermediario', :imp_comision, 'Pagado', :fecha, 0);"""
                    cursor.execute(insert_gasto_interm, {'idreserva': idreserva, 'imp_comision': imp_comision, 'fecha': fecha}) 
                conexion.commit()
            else:
                print("Faltan más de 7 días")
                #La fecha de entrada es en más de una semana: el cliente todavía tiene derecho a reembolso si cancela la reserva.
                #Esto genera una reserva en estado "provisional" (desde que se hace una reserva hasta 7 días antes de la llegada) y una factura en estado "Pendiente". En este caso no se generan gastos.
                #Insertamos la nueva reserva en la tabla de "reservas" en estado "provisional":
                insert_reserva = """INSERT INTO reservas (idcliente, idintermediario, idalojamiento, estado_reserva, fecha_reserva, fecha_entrada, fecha_salida, num_noches, num_personas, num_habitaciones, cuna, importe, limpieza, python) VALUES(:idcliente, :idintermediario, :idalojamiento, 'provisional', :fecha_res, :fecha_ent, :fecha_sal, :num_noches, :num_personas, :num_habitaciones, :cuna, :importe, :limpieza, 1);"""
                cursor.execute(insert_reserva, {'idcliente': idcliente, 'idintermediario': idintermediario, 'idalojamiento': idalojamiento, 'fecha_res': fecha_res, 'fecha_ent': fecha_ent, 'fecha_sal': fecha_sal, 'num_noches': num_noches, 'num_personas': num_personas, 'num_habitaciones': num_habitaciones, 'cuna': cuna, 'importe': importe, 'limpieza': limpieza})      
                #Recuperamos el valor de "idreserva" y actualizamos el valor de la columna python a 1 en la tabla "reservas":
                idreserva = cursor.execute("SELECT idreserva FROM reservas where python = 1").fetchone()[0]
                update_reserva = """UPDATE reservas SET python = 0 where idreserva = :idreserva;"""
                cursor.execute(update_reserva, {'idreserva': idreserva})
                #Insertamos un nuevo registro en la tabla de "facturas" con estado "Pendiente":
                insert_factura = """INSERT INTO facturas (idreserva, importe_total, estado, python) VALUES(:idreserva, :importe_total, 'Pendiente', 0);"""
                cursor.execute(insert_factura, {'idreserva': idreserva, 'importe_total': importe_total})
                #En este caso no se genera ningún gasto.
                conexion.commit()
            #Una vez que hemos insertado/actualizado todos los datos de la reserva enviados en el formulario, enviamos email indicando que la reserva se ha hecho correctamente.
            print("La reserva se ha realizado correctamente")
            email_subject = 'Casa Rural Los Aromos - Reserva confirmada'
            email_content = 'Hola, Hemos procesado su solicitud de reserva y queda confirmada. Gracias'
            #Enviamos el email al cliente cuando la reserva es directa desde la página web:
            if used == 'client':
                email_to = cliente_mail
            #Enviamos el email al intermediario cuando la reserva proviene desde un intermediario:
            elif used == 'interm':
                nombre_interm = row['Intermediario']
                q_interm = """SELECT email FROM intermediarios where nombre = :nombre_interm"""
                email_to = cursor.execute(q_interm, {'nombre_interm': nombre_interm}).fetchone()[0]
            google_gmail_management.send_email(email_to, email_subject, email_content)
        #Actualizamos el Dataframe con las nuevas inserciones:
        reservas_db = pd.read_sql_query("SELECT fecha_entrada, fecha_salida FROM reservas where estado_reserva in ('confirmada', 'provisional')", conexion)

