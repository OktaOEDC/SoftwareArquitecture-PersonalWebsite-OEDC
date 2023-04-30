import re
from datetime import datetime #Libreria para restar fechas

# Lamda hanlder es la funcion prinipal que corre mi lambda

def lambda_handler(event, context):
    #Se necesita una respuesta de tipo json con estos 4 valores en APIS proxy para su funcionamiento correcto
    baseResponse = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { "uuuh": "ya vamonos no?!"},
        "body": {}
    }

    # La fecha se encuentra en los path parameters con la llave del recurso proxy de la API
    dateRange: str = event['pathParameters']['dateRange'] 

    # Revisar que el usuario llamó a la API siguiendo mi sintaxis deseada 
    #  usando una regex (YYYYMMDD-YYYYMMDD es lo que quiero)
    if(re.match("[0-9]{8}-[0-9]{8}", dateRange)):
        # Separar y convertir la fecha de string a objetos fecha
        startDateStr, endDateStr = dateRange.split('-')
        startDate = datetime.strptime(startDateStr, '%Y%m%d')
        endDate = datetime.strptime(endDateStr, '%Y%m%d')

        #La fecha menor debe de ser la izquierda en esta API
        if(endDateStr < startDateStr):
            baseResponse["statusCode"] = 500
            baseResponse["body"] = "Fecha final es menor que la de inicio, favor de escribir primero la fecha inicial"
        else:
            # Hacer calculos de fechas
            days = (endDate-startDate).days
            hours = days * 24
            minutes = hours * 60
            answer = f"Hubo {days} dias o {hours} horas o {minutes} minutos entre ambas fechas"
            baseResponse["body"] = answer
        
    else:
        baseResponse["statusCode"] = 500
        baseResponse["body"] = "Rango de fechas no sigue la sintaxis YYYYMMDD-YYYYMMDD"

    return baseResponse
