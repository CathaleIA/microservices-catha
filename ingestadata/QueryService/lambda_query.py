import boto3
import os

# Inicializamos los clientes
dynamodb = boto3.resource('dynamodb')
timestream = boto3.client('timestream-query')

# Obtenemos la tabla DynamoDB desde variable de entorno
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    field = event['info']['fieldName']  # Qué operación se está ejecutando

    # 🔍 Consulta el estado actual desde DynamoDB
    if field == 'getStatus':
        asset_id = event['arguments']['assetId']
        response = table.get_item(Key={'assetId': asset_id})
        return response.get('Item', {})  # Devuelve el estado actual

    # 📈 Consulta histórico desde Timestream
    elif field == 'getMetrics':
        asset_id = event['arguments']['assetId']
        start = event['arguments']['start']
        end = event['arguments']['end']

        # Construimos la query SQL para Timestream
        query = f"""
        SELECT time, measure_name, measure_value::double
        FROM "{os.environ['TIMESTREAM_DB']}"."{os.environ['TIMESTREAM_TABLE']}"
        WHERE assetId = '{asset_id}'
        AND time BETWEEN from_iso8601_timestamp('{start}') AND from_iso8601_timestamp('{end}')
        ORDER BY time ASC
        """

        # Ejecutamos la query
        result = timestream.query(QueryString=query)

        # Procesamos los resultados
        metrics = []
        for row in result['Rows']:
            data = row['Data']
            metrics.append({
                "timestamp": data[0]['ScalarValue'],
                "metric": data[1]['ScalarValue'],
                "value": float(data[2]['ScalarValue'])
            })

        return metrics

    # Si no se reconoce el campo, devolvemos vacío
    return {}