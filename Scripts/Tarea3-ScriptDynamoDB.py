#!/usr/bin/env python3
# la primera linea es para declarar que se use python 3 cuando se corre como ejecutable
#  ej(./archivo.py)

import boto3
import botocore

# Utilizaremos el cliente de DYNAMO DB, este objeto será nuestro medio de comunicación con dynamo
dynamodb = boto3.client('dynamodb')

# Create or update, delete, o, find. Esas son las opciones
option = input(
    """
    Escriba la opción que desea hacer: \n
    1) Crear/Actualizar Record de estudiante
    2) Borrar record de estudiante
    3) Ver record de estudiante
    """
)
# Haremos un switch case de 3 opciones (más default) una para creación/actualización,
# otro para borrado, y otro para lecturas
match option:
    case '1':  # UPSERT
        try:
            # Solicitaremos al usuario matricula, nombre completo y URL del sitio personal
            matricula = input(
                "Ingrese matricula para el record que actualizará/creará (escriba ENTER al acabar de escribirla): ")
            fullname = input(
                "Ingrese nombre para el record que actualizará/creará (escriba ENTER al acabar de escribirla): ")
            personlWebsite = input(
                "Ingrese website para el record que actualizará/creará (escriba ENTER al acabar de escribirla): ")

            # PUT_ITEM es para meter items en tablas, si ya existe uno lo sobreescribirá
            # esto lo identifica con la llave primaria (detalles en el documento)
            dynamodb.put_item(
                TableName="Students",  # Necesitamos nombre de tabla
                Item={
                    "id": {'S': matricula},  # Llave primaria es obligatoria
                    # Esto y el otro dato son los que ya existian en la tabla
                    "full_name": {'S': fullname},
                    "personal_website": {'S': personlWebsite}
                }
                # En mi tarea 2 explico porque los valores son diccionarios, pero en resumen deben de indicar
                #  el tipo de valor del valor, en este caso S es STRING, así esta definida la tabla
            )
            print("proceso de creación/actualización terminado :)")
        except:
            # Excepcion generica para decirle al usuario que si salió mal
            print(
                "Hubo un error inesperado creando/editando el record de la tabla Students")
    case '2':
        try:
            # Solo necesitamos la llave primaria para borrar
            matricula = input(
                "Ingrese matricula para el record que borrará (escriba ENTER al acabar de escribirla): ")

            # Para borrar usamos DELETE_ITEM
            response = dynamodb.delete_item(
                TableName="Students",
                Key={
                    "id": {'S': matricula}
                },
                ConditionExpression="attribute_exists(id)"
                # Creamos una condición de expresión, "atrtibute_exists(N)"
                # es para definir si la operación fue un exitó si se cumplió esa función
                # más detalles en documento
            )
            print("proceso de borrado terminado :)")

        except botocore.exceptions.ClientError as e:
            # En caso de que no se cumpla la condición (no existe ese item)
            # se levantará esta exepción
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("No existe tal record en la tabla")
        except:
            # Exepción generica si hubo otro tipo de excpeción
            print("Error inesperado borrando record de la tabla Students")

    case '3':
        try:
            #Solicitar llave primaria (en este caso matricula) para leer el record en la tabla
            matricula = input(
                "Ingrese matricula porfavor (escriba ENTER al acabar de escribirla): ")

            #Guardar respuesta en variable porque queremos leer información
            #Esto se hace con GET_ITEM
            response = dynamodb.get_item(
                TableName="Students",
                Key={
                    "id": {'S': matricula}
                }
            )
            #Verificar si existe la llave Item en la respuesta, este contiene el record en la base de datos
            if ("Item" in response):
                #Imprimirlo tal como está
                print(response["Item"])
                print("proceso de lectura terminado :)")
            else:
                #Levantar excepción si no existe ese record
                print("No hay record para ese alumno")

            

        except:
            print("Error inesperado intentando leer record de la tabla Students")

    case _:
        # Si no puso un valor valido entonces
        print("Corre este script denuevo y escoje bien una opcion porfavor")
        pass
