import json
import boto3
import urllib3
from botocore.exceptions import ClientError


def isAuthorized(authHeader):
    #Este metodo es para verificar que el header de autentificación existe
    # Y, que viene con el usuario y contraseña correctos
    if("YWRtaW46YWJjMTIzIUA=" in authHeader):
        #Usuario y contraseña en BASIC auth se encodifican en base 64
        # en esta sintaxis:      user:password
        # pero en base64, así que reviso que en el header de autorizacion
        # este presente el substring con las credenciales de este ejercicio
        return True
    else:
        return False

def lambda_handler(event, context):
    # Revisar si el usuario dio el usuario y contraseña correctos
    if(isAuthorized(event["headers"]["Authorization"])):
        #Si es así seguimos
        pass
    else:
        #Si no entonces retornar un 401 (No autorizado), y decirle al usuario
        #  que no está autorizado
        return get_response(401, "No estas autorizado para usar esta API")
    
    dynamo = boto3.resource("dynamodb")
    students_table = dynamo.Table("Students")
    # En vez de buscar id directamente
    #  debemos buscar ID en los path parameters
    matricula = event["pathParameters"]["id"]
    

    if matricula:
        try:
            student = students_table.get_item(Key={"id": matricula})
            api_key = get_secret()
            weather = get_weather(student, api_key)
            success_response = {
                "id": matricula,
                "full_name": student["Item"]["full_name"],
                "city": student["Item"]["city"],
                "weather": json.loads(weather)
            }
            return get_response(200, success_response)
        except ClientError as error:
            raise error
    else:
        return get_response(400, {"message": "Missing required field id"})


def get_weather(student, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid={1}"
    if "city" in student["Item"].keys():
        http = urllib3.PoolManager()
        response = http.request('GET', base_url.format(student["Item"]["city"], api_key))
        return response.data
    else:
        return json.dumps("No city assigned to student")


def get_secret():
    secretsmanager = boto3.client(service_name='secretsmanager')
    secret_name = "weather_api_profe"
    secrets_response = secretsmanager.get_secret_value(SecretId=secret_name)
    return secrets_response['SecretString']


def get_response(code, body):
    # El return no estaba completo para ser usado en una API proxy
    #  le faltaba headers y "isBase64Encoded", el cual de este ultimo
    #  la respuesta es falso
    return {
        "isBase64Encoded": False,
        "statusCode": code,
        "headers": { "headerChido": "ah pero el script estaba bien no B)? : no"},
        "body": str(body)
    }
