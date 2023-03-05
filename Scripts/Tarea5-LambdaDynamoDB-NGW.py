# AWS lambdas ya viene con boto3 instalado si usas python 3.8 en adelante

import boto3
import botocore

# Lamda hanlder es la funcion prinipal que corre mi lambda


def lambda_handler(event, context):
    # Utilizaremos (al igual que en la tarea e) el cliente de DYNAMO DB, este objeto será nuestro medio de comunicación con dynamo
    dynamodb = boto3.client('dynamodb')
    # Esto es un copy paste del script de mi tarea 3 pero modificado para funcionar en lambda
    try: 
        #Si no nos dió una acción que hacer entonces adios
        option = event["action"]
    except:
        return ("Corre esta lambda denuevo y da un valor C, R, U, o D en la llave 'action' del json de entrada")
    # Haremos un switch case de 3 opciones (más default) una para creación/actualización,
    # otro para borrado, y otro para lecturas


    #C -> Create 
    #R -> Delete
    #U -> Update
    #D -> Delete
    if(option=='C' or option=='U'):  # UPSERT ¿Que sinverguenza no?
        try:
            # Usaremos de la llamada a la lambda, el usuario matricula, nombre completo y URL del sitio personal
            # En un escenario más normal, hubiera hecho una oducmentación que dice como usar la lambda, pero en
            #     este caso mi tarea será lo unico que habrá
            matricula = event["entry"]["matricula"]
            fullname = event["entry"]["full_name"]
            personlWebsite = event["entry"]["personal_website"]

            # PUT_ITEM es para meter items en tablas, si ya existe uno lo sobreescribirá
            # esto lo identifica con la llave primaria (detalles en el documento)
            dynamodb.put_item(
                TableName="Students",  # Necesitamos nombre de tabla
                Item={
                    # Llave primaria es obligatoria
                    "id": {'S': matricula},
                    # Esto y el otro dato son los que ya existian en la tabla
                    "full_name": {'S': fullname},
                    "personal_website": {'S': personlWebsite}
                }
                # En mi tarea 2 explico porque los valores son diccionarios, pero en resumen deben de indicar
                #  el tipo de valor del valor, en este caso S es STRING, así esta definida la tabla
            )
            return ("proceso de creación/actualización terminado :)")
        except:
            # Excepcion generica para decirle al usuario que si salió mal
            return ("Hubo un error inesperado creando/editando el record de la tabla Students")
    elif(option=='D'):
        try:
            # Solo necesitamos la llave primaria para borrar
            matricula = event["entry"]["matricula"]

            # Para borrar usamos DELETE_ITEM
            dynamodb.delete_item(
                TableName="Students",
                Key={
                    "id": {'S': matricula}
                },
                ConditionExpression="attribute_exists(id)"
                # Creamos una condición de expresión, "atrtibute_exists(N)"
                # es para definir si la operación fue un exitó si se cumplió esa función
                # más detalles en documento
            )
            return ("proceso de borrado terminado :)")

        except botocore.exceptions.ClientError as e:
            # En caso de que no se cumpla la condición (no existe ese item)
            # se levantará esta exepción
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return ("No existe tal record en la tabla")
        except:
            # Exepción generica si hubo otro tipo de excpeción
            return ("Error inesperado borrando record de la tabla Students")
    elif(option=='R'):
        try:
            # Solicitar llave primaria (en este caso matricula) para leer el record en la tabla
            matricula = event["entry"]["matricula"]

            # Guardar respuesta en variable porque queremos leer información
            # Esto se hace con GET_ITEM
            response = dynamodb.get_item(
                TableName="Students",
                Key={
                    "id": {'S': matricula}
                }
            )
            # Verificar si existe la llave Item en la respuesta, este contiene el record en la base de datos
            if ("Item" in response):
                # Imprimirlo tal como está
                return (response["Item"])
            else:
                # Levantar excepción si no existe ese record
                return ("No hay record para ese alumno")

        except:
            return ("Error inesperado intentando leer record de la tabla Students")
    else:
        # Si no puso un valor valido entonces
        return ("Corre esta lambda denuevo y da un valor del 1 al 3 en la llave 'action' del json de entrada")
