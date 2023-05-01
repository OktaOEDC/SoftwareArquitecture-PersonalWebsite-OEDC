import re
from datetime import datetime #Libreria para restar fechas

# Lamda hanlder es la funcion prinipal que corre mi lambda

def lambda_handler(event, context):
    #HTML STRING: Aquí irán unos strings con html 
    htmlHeadString: str = "<!DOCTYPE html><html><head><title>Rango de fechas dinámico</title></head><body><h1>"
    htmlFooterString: str = "</h1></body></html>"
    htmlReturnString: str = ""

    #Se necesita una respuesta de tipo json con estos 4 valores en APIS proxy para su funcionamiento correcto
    baseResponse = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "uuuh": "ya vamonos no?!",
            "content-type": "text/html"
        },
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
            answer: str = "Fecha final es menor que la de inicio, favor de escribir primero la fecha inicial"
            htmlReturnString = htmlHeadString + answer + htmlFooterString
            baseResponse["body"] = htmlReturnString
            baseResponse["statusCode"] = 500
        else:
            # Hacer calculos de fechas
            days: int = (endDate-startDate).days
            hours: int = days * 24
            minutes: int = hours * 60
            answer: str = f"Hubo {days} dias o {hours} horas o {minutes} minutos entre ambas fechas"
            htmlReturnString = htmlHeadString + answer + htmlFooterString
            baseResponse["body"] = htmlReturnString
        
    else:
        answer: str = "Rango de fechas no sigue la sintaxis YYYYMMDD-YYYYMMDD"
        htmlReturnString = htmlHeadString + answer + htmlFooterString
        baseResponse["body"] = htmlReturnString
        baseResponse["statusCode"] = 500

    return baseResponse