import os
import boto3
import requests
from datetime import datetime, timezone
import json

dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-write')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

APPSYNC_URL = os.environ['APPSYNC_API_URL']

def lambda_handler(event, context):
    print(f"Región de Lambda: {os.environ.get('AWS_REGION')}")
    print(f"DB: {os.environ['TIMESTREAM_DB']}") 
    print(f"Tabla: {os.environ['TIMESTREAM_TABLE']}")
    print(f"Endpoint Timestream: {timestream.meta.endpoint_url}")
    # 1. Simulación: Obtener datos de una API externa
    # En producción aquí haces requests.get() a tu API o DB
    assets_data = [
        {"assetId": "GEN-01", "status": "RUNNING", "potencia": 250, "temp": 75},
        {"assetId": "GEN-02", "status": "STOPPED", "potencia": 0, "temp": 30}
    ]

    for asset in assets_data:
        timestamp = datetime.now(timezone.utc).isoformat()

        # 2. Guardar último estado en DynamoDB
        table.put_item(Item={
            "assetId": asset['assetId'],
            "status": asset['status'],
            "timestamp": timestamp
        })

        # 3. Guardar histórico en Timestream
        timestream.write_records(
            DatabaseName=os.environ['TIMESTREAM_DB'],
            TableName=os.environ['TIMESTREAM_TABLE'],
            Records=[
                {
                    'Dimensions': [
                        {'Name': 'assetId', 'Value': asset['assetId']},
                    ],
                    'MeasureName': 'potencia',
                    'MeasureValue': str(asset['potencia']),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(datetime.utcnow().timestamp() * 1000))
                },
                {
                    'Dimensions': [
                        {'Name': 'assetId', 'Value': asset['assetId']},
                    ],
                    'MeasureName': 'temperatura',
                    'MeasureValue': str(asset['temp']),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(datetime.utcnow().timestamp() * 1000))
                }
            ]
        )

        # 4. Llamar a AppSync Mutation para disparar suscripción
        mutation = """
        mutation Publish($assetId: String!, $status: String!, $timestamp: String!) {
          publishUpdate(assetId: $assetId, status: $status, timestamp: $timestamp) {
            assetId
            status
            timestamp
          }
        }
        """
        variables = {
            "assetId": asset['assetId'],
            "status": asset['status'],
            "timestamp": timestamp
        }

        # Autenticación via IAM si usas Cognito desde Lambda
        headers = {
            "Content-Type": "application/json"
        }

        requests.post(APPSYNC_URL, json={"query": mutation, "variables": variables}, headers=headers)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Data ingested and published"})
    }
