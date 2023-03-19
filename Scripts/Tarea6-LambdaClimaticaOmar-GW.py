import json
import boto3
import urllib3
from botocore.exceptions import ClientError

def getAPICreds():
    secretsmanager = boto3.client(service_name='secretsmanager')
    #Nombre de secreto
    secret_name = "api_creds_weather_omar"
    #Conseguir el secreto con ese nombre
    secrets_response = secretsmanager.get_secret_value(SecretId=secret_name)
    #Las credenciales estan aquí, en el SecretString
    return secrets_response['SecretString']

def isAuthorized(authHeader):
    #Este metodo es para verificar que el header de autentificación existe
    # Y, que viene con el usuario y contraseña correctos
    superSecretCred = getAPICreds()
    if(superSecretCred in authHeader):
        #Usuario y contraseña en BASIC auth se encodifican en base 64
        # en esta sintaxis:      user:password
        # pero en base64, así que reviso que en el header de autorizacion
        # este presente el substring con las credenciales de este ejercicio
        return True
    else:
        return False

def lambda_handler(event, context):
    # Revisar si el usuario dio el usuario y contraseña correctos
    try:
        if(isAuthorized(event["headers"]["Authorization"])):
            #Si es así seguimos
            pass
        else:
            #Si no entonces retornar un 401 (No autorizado), y decirle al usuario
            #  que no está autorizado
            return get_response(401, "No estas autorizado para usar esta API")
    except:
        return get_response(500, "No Auth provided or server broke")
    

    dynamoReader = boto3.resource("dynamodb")
    dynamoWriter = boto3.client("dynamodb")
    # En vez de buscar id directamente
    #  debemos buscar ID en los path parameters
    matricula = event["pathParameters"]["id"]


    
    
    # Esto es un copy paste del script de mi tarea 4 pero modificado para funcionar en lambda
    try: 
        #Si no nos dió una acción que hacer entonces adios
        option = event['httpMethod']
    except:
        return get_response(500,"Corre esta API/lambda con un metodo HTTP correcto")

    if(option=='POST' or option=='PUT'):  # UPSERT ¿Que sinverguenza no?
        try:
            # Usaremos de la llamada a la lambda, el usuario matricula, nombre completo y URL del sitio personal
            # En un escenario más normal, hubiera hecho una oducmentación que dice como usar la lambda, pero en
            #     este caso mi tarea será lo unico que habrá
            requestBody = json.loads(event["body"])
            fullname = requestBody["full_name"]
            personlWebsite = requestBody["personal_website"]
            city = requestBody["city"]

            # PUT_ITEM es para meter items en tablas, si ya existe uno lo sobreescribirá
            # esto lo identifica con la llave primaria (detalles en el documento)
            dynamoWriter.put_item(
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
            return get_response(200,"Creación/Actualización terminada")
        except Exception as e:
            # Error 500 generico para decirle al usuario que si salió mal
            return get_response(500, f"Error creando/actualizando estudiantes {str(e)}")
    elif(option=="GET"):
        students_table = dynamoReader.Table("Students")
        if matricula:
            try:
                student = students_table.get_item(
                    TableName="Students",
                    Key={"id": matricula}
                )
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
                return get_response(500, str(e))
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
