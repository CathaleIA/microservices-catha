import os
import boto3
import requests
from datetime import datetime, timezone
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-write')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

DATA_API = os.environ['FAKE_API_URL']
APPSYNC_URL = os.environ['APPSYNC_API_URL']

def lambda_handler(event, context):

    try:
        response = requests.get(DATA_API, timeout=40)
        response.raise_for_status()
        data = response.json()

        print("Data de la api:", json.dumps(data))

        timestamp = data["timestamp"]
        motor = data["motor"]
        bancos = data["bancos"]

        table.put_item(Item={
            "assetId": "GEN-00",
            "status": motor["modoOperacion"],
            "timestamp": timestamp,
            "presionAceite": Decimal(str(motor["presionAceite"])),
            "presionCombustible": Decimal(str(bancos["A1"]["presionCombustible"])),
            "presionTurbo": Decimal(str(bancos["A1"]["presionTurbo"])),
        })

        records = []

        for key, value in motor.items():
            if isinstance(value, (int,float)):
                records.append({
                    'Dimensions': [{'Name': 'assetId', 'Value': 'GEN-00'}],
                    'MeasureName': key,
                    'MeasureValue': str(value),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(datetime.now(timezone.utc).timestamp() * 1000))
                })

        for banco, metrics in bancos.items():
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    records.append({
                        'Dimensions': [
                            {'Name': 'assetId', 'Value': 'GEN-00'},
                            {'Name': 'banco', 'Value': banco}
                        ],
                        'MeasureName': key,
                        'MeasureValue': str(value),
                        'MeasureValueType': 'DOUBLE',
                        'Time': str(int(datetime.now(timezone.utc).timestamp() * 1000))
                    })

        if records:
            timestream.write_records(
                DatabaseName=os.environ['TIMESTREAM_DB'],
                TableName=os.environ['TIMESTREAM_TABLE'],
                Records=records
            )
            print(f"✅ {len(records)} métricas insertadas en Timestream")


        # 4. Llamar a AppSync Mutation para disparar suscripción
        mutation = """
        mutation Publish(            
            $assetId: String!, 
            $status: String!, 
            $timestamp: String!,
            $presionAceite: Float!
            $presionCombustible: Float!
            $presionTurbo: Float!
        ) {
            publishUpdate(
                assetId: $assetId,
                status: $status,
                timestamp: $timestamp,
                presionAceite: $presionAceite,
                presionCombustible: $presionCombustible,
                presionTurbo: $presionTurbo
            ) {
                assetId
                status
                timestamp
                presionAceite
                presionCombustible
                presionTurbo
            }
        }
        """
        variables = {
            "assetId": "GEN-00",
            "status": motor["modoOperacion"],
            "timestamp": timestamp,
            "presionAceite": motor["presionAceite"],
            "presionCombustible": bancos["A1"]["presionCombustible"],
            "presionTurbo": bancos["A1"]["presionTurbo"],
        }

        # Autenticación via IAM si usas Cognito desde Lambda
        headers = {
            "Content-Type": "application/json"
        }

        r = requests.post(APPSYNC_URL, json={"query": mutation, "variables": variables}, headers=headers)
        print("Respuesta appsync mutacion", r.status_code, r.text)


        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data ingested and published"})
        }


    except Exception as e:
        print("Error en lambda ingesta", str(e))
        return {
            "statusCode": 500,
            "boby": json.dumps({"error:", str(e)})
        }
