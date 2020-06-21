#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function


# Parte principal del programa donde se insertan en la base de datos las encuestas recibidas a través del formulario:
def update_survey(data_new, conexion):
    # Abrimos el cursor a la base de datos
    cursor = conexion.cursor()
    #Recorremos el dataframe "data_new" que contiene las nuevas encuestas enviadas en el formulario:
    for index, row in data_new.iterrows():
        #Recuperamos los datos de la reserva enviados en el formulario:
        fecha_encuesta = row['Marca temporal']
        satisfac = row['Satisfacción']
        expect = row['Expectativa']
        rep = row['Repetiría']
        recom = row['Recomendaciones']
        hab = row['Habitación']
        limp = row['Limpieza']
        rel_calid_pre = row['Relación calidad / precio']
        conf = row['Confort']
        ent = row['Entorno']
        acces = row['Accesibilidad']
        ubic = row['Ubicación']
        equip = row['Equipamiento']
        segm = row['Segmento']
        redes = row['Redes sociales']
        comen = row['Comentario']
        activ = row['Actividades']
        png = row['P.N. Garajonay']
        recom_png = row['Recomendación P.N.']
        idreserva = row['ID reserva']
        
        #Recuperamos el valor de "idcliente", usando el identificador de la reserva, para posteriormente usarlo en la inserción:
        q_reservas = """SELECT idcliente FROM reservas where idreserva = :idreserva"""
        idcliente = cursor.execute(q_reservas, {'idreserva': idreserva}).fetchone()[0]

        #Insertamos los datos de la encuesta en la tabla de "encuestas_satifaccion":
        insert_encuestas = """INSERT INTO encuestas_satifaccion (idcliente, fecha_encuesta, satisfaccion, expectativa, repetiria_estancia, recomendaciones, valoracion_habitacion, valoracion_limpieza, valoracion_calidad_precio, valoracion_confort, valoracion_entorno, valoracion_accesibilidad, valoracion_ubicacion, valoracion_equipamiento, segmento, redes_sociales, comentario, actividades, visita_PN_garajonay, recomendacion_PN_garajonay) VALUES(:idcliente, :fecha_encuesta, :satisfac, :expect, :rep, :recom, :hab, :limp, :rel_calid_pre, :conf, :ent, :acces, :ubic, :equip, :segm, :redes, :comen, :activ, :png, :recom_png);"""
        cursor.execute(insert_encuestas, {'idcliente': idcliente, 'fecha_encuesta': fecha_encuesta, 'satisfac': satisfac, 'expect': expect, 'rep': rep, 'recom': recom, 'hab': hab, 'limp': limp, 'rel_calid_pre': rel_calid_pre, 'conf': conf, 'ent': ent, 'acces': acces, 'ubic': ubic, 'equip': equip, 'segm': segm, 'redes': redes, 'comen': comen, 'activ': activ, 'png': png, 'recom_png': recom_png})
        
        print("La encuesta se ha registrado correctamente")
        conexion.commit()
