# AWS lambdas ya viene con boto3 instalado si usas python 3.8 en adelante

import boto3
import botocore
import json

# Lamda hanlder es la funcion prinipal que corre mi lambda


def lambda_handler(event, context):
    #Se necesita una respuesta de tipo json con estos 4 valores en APIS proxy para su funcionamiento correcto
    baseResponse = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { "uuuh": "ya vamonos no?!"},
        "body": "..."
    }
    # Utilizaremos (al igual que en la tarea e) el cliente de DYNAMO DB, este objeto será nuestro medio de comunicación con dynamo
    dynamodb = boto3.client('dynamodb')
    # Esto es un copy paste del script de mi tarea 3 pero modificado para funcionar en lambda
    try: 
        #Si no nos dió una acción que hacer entonces adios
        option = event['httpMethod']
    except:
        baseResponse["statusCode"] = 500
        baseResponse["body"] = "Corre esta lambda denuevo y da un METODO correcto de corrida"
        return baseResponse
    # Haremos un switch case de 3 opciones (más default) una para creación/actualización,
    # otro para borrado, y otro para lecturas


    #C -> Create 
    #R -> Delete
    #U -> Update
    #D -> Delete
    if(option=='POST' or option=='PUT'):  # UPSERT ¿Que sinverguenza no?
        try:
            # Usaremos de la llamada a la lambda, el usuario matricula, nombre completo y URL del sitio personal
            # En un escenario más normal, hubiera hecho una oducmentación que dice como usar la lambda, pero en
            #     este caso mi tarea será lo unico que habrá
            requestBody = json.loads(event["body"])
            matricula = requestBody['matricula']
            fullname = requestBody["full_name"]
            personlWebsite = requestBody["personal_website"]
            city = requestBody["city"]

            # PUT_ITEM es para meter items en tablas, si ya existe uno lo sobreescribirá
            # esto lo identifica con la llave primaria (detalles en el documento)
            dynamodb.put_item(
                TableName="Students",  # Necesitamos nombre de tabla
                Item={
                    # Llave primaria es obligatoria
                    "id": {'S': matricula},
                    # Esto y el otro dato son los que ya existian en la tabla
                    "full_name": {'S': fullname},
                    "personal_website": {'S': personlWebsite},
                    "city": {'S': city}
                }
                # En mi tarea 2 explico porque los valores son diccionarios, pero en resumen deben de indicar
                #  el tipo de valor del valor, en este caso S es STRING, así esta definida la tabla
            )
            baseResponse["body"] = "Proceso de creación terminado"
            return baseResponse
        except Exception as e:
            # Error 500 generico para decirle al usuario que si salió mal
            baseResponse["statusCode"] = 500
            baseResponse["headers"]['exception'] = str(e)
            baseResponse["body"] = "Hubo un error inesperado creando/editando el record de la tabla Students"
            return baseResponse
    elif(option=='DELETE'):
        try:
            # Solo necesitamos la llave primaria para borrar
            matricula = event["queryStringParameters"]['matricula']

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
            baseResponse["body"] = "Proceso de borrado terminado"
            return baseResponse

        except botocore.exceptions.ClientError as e:
            # En caso de que no se cumpla la condición (no existe ese item)
            # se retornará un 404 como error
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                baseResponse["statusCode"] = 404
                baseResponse["body"] = "No existe tal record en la tabla"
                return baseResponse
        except:
            # Error 500 generico si hubo otro tipo de excpeción
            baseResponse["statusCode"] = 500
            baseResponse["body"] = "Error inesperado borrando record de la tabla Students, diste matricula?"
            return baseResponse
    elif(option=='GET'):
        try:
            # Solicitar llave primaria (en este caso matricula) para leer el record en la tabla
            matricula = event["queryStringParameters"]['matricula']

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
                baseResponse["body"] = json.dumps(response["Item"])
                return baseResponse
            else:
                # Retornar error 404 si no existe ese record
                baseResponse["statusCode"] = 404
                baseResponse["body"] = "No hay record para ese alumno"
                return baseResponse

        except:
            baseResponse["statusCode"] = 500
            baseResponse["body"] = "Error inesperado intentando leer record de la tabla Students, ¿diste matrícula?"
            return baseResponse
    else:
        # Si no puso un valor valido entonces
        baseResponse["body"] = "Corre esta lambda denuevo y da un METODO correcto de corrida"
        return baseResponse
