import boto3
import os
import json
from botocore.exceptions import ClientError

# Inicializamos los clientes
dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-query')

# Obtenemos la tabla DynamoDB desde variable de entorno
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    print("🔧 Lambda ejecutada")
    print("📦 Evento recibido:", json.dumps(event))

    try:
        field = event['info']['fieldName']
        print(f"🔍 Campo solicitado: {field}")

        # Consulta el estado actual desde DynamoDB
        if field == 'getStatus':
            asset_id = event['arguments']['assetId']
            print(f"🧩 Consultando estado para assetId: {asset_id}")

            response = table.get_item(Key={'assetId': asset_id})
            item = response.get('Item')
            # print("📄 Respuesta DynamoDB:", json.dumps(item))

            if item and all(k in item for k in ['assetId', 'status', 'timestamp']):
                return item
            else:
                print("⚠️ Item no encontrado o incompleto")
                return None

        # Consulta histórico desde Timestream
        elif field == 'getMetrics':
            asset_id = event['arguments']['assetId']
            start = event['arguments']['start']
            end = event['arguments']['end']

            print(f"📈 Consultando métricas para assetId: {asset_id} entre {start} y {end}")

            query = f"""
            SELECT time, measure_name, measure_value::double
            FROM "{os.environ['TIMESTREAM_DB']}"."{os.environ['TIMESTREAM_TABLE']}"
            WHERE assetId = '{asset_id}'
            AND time BETWEEN from_iso8601_timestamp('{start}') AND from_iso8601_timestamp('{end}')
            ORDER BY time ASC
            """
            print("🧪 Query Timestream:", query)

            result = timestream.query(QueryString=query)
            print("📊 Resultado Timestream:", json.dumps(result))

            metrics = []
            for row in result['Rows']:
                data = row['Data']
                metrics.append({
                    "timestamp": data[0]['ScalarValue'],
                    "metric": data[1]['ScalarValue'],
                    "value": float(data[2]['ScalarValue'])
                })

            print("📈 Métricas procesadas:", json.dumps(metrics))
            return metrics

        print("⚠️ Campo no reconocido")
        return None

    except ClientError as e:
        print("❌ Error de cliente AWS:", e.response['Error']['Message'])
        raise e
    except Exception as e:
        print("❌ Error general:", str(e))
        raise e
