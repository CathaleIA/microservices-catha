import os
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.endpoint import BotocoreHTTPSession
from datetime import datetime, timezone
import json
from decimal import Decimal
import requests

dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-write')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

DATA_API = os.environ['FAKE_API_URL']
APPSYNC_URL = os.environ['APPSYNC_API_URL']
REGION = os.environ['AWS_REGION']

def sign_and_post(query, variables):
    """Firma con SigV4 y envía mutación a AppSync"""
    session = boto3.session.Session()
    credentials = session.get_credentials()
    request = AWSRequest(
        method="POST",
        url=APPSYNC_URL,
        data=json.dumps({"query": query, "variables": variables}),
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(credentials, "appsync", REGION).add_auth(request)
    return BotocoreHTTPSession().send(request.prepare())

def lambda_handler(event, context):
    try:
        # 1. Llamar fuente externa
        response = boto3.client("lambda")._endpoint.http_session.send(
            boto3.session.Session().create_client("lambda")._endpoint.create_request(
                operation_model=None,
                request_dict={"url_path": DATA_API, "method": "GET"},
                request_context={},
            )
        )
        # 👆 opcional: puedes seguir usando requests si quieres, lo dejo igual que tu versión:
        response = requests.get(DATA_API, timeout=40)
        response.raise_for_status()
        data = response.json()
        print("Data de la api:", json.dumps(data))

        timestamp = data["timestamp"]
        motor = data["motor"]
        bancos = data["bancos"]

        # 2. Dynamo
        table.put_item(Item={
            "assetId": "GEN-00",
            "status": motor["modoOperacion"],
            "timestamp": timestamp,
            "presionAceite": Decimal(str(motor["presionAceite"])),
            "presionCombustible": Decimal(str(bancos["A1"]["presionCombustible"])),
            "presionTurbo": Decimal(str(bancos["A1"]["presionTurbo"])),
        })

        # 3. Timestream
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

        # 4. AppSync Mutation firmada con IAM
        mutation = """
        mutation Publish(            
            $assetId: String!, 
            $status: String!, 
            $timestamp: String!,
            $presionAceite: Float!,
            $presionCombustible: Float!,
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

        r = sign_and_post(mutation, variables)
        print("Respuesta appsync mutacion", r.status_code, r.text)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data ingested and published"})
        }

    except Exception as e:
        print("Error en lambda ingesta", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
