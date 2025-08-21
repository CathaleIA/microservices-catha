# SnowflakeQueryLambda/app.py
import json
import logging
import boto3
import snowflake.connector
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente de Secrets Manager
secrets_client = boto3.client('secretsmanager')

def get_secret():
    secret_name = "SnowflakeCredentials"
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Error obteniendo el secreto: {e}")
        raise e

def lambda_handler(event, context):
    logger.info(f"Evento recibido: {event}")

    # Obtener credenciales
    try:
        creds = get_secret()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'No se pudo obtener las credenciales de Snowflake'})
        }

    # Conectar a Snowflake
    try:
        conn = snowflake.connector.connect(
            user=creds['user'],
            password=creds['password'],
            account=creds['account'],
            warehouse=creds['warehouse'],
            database=creds['database'],
            schema=creds['schema'],
            autocommit=True
        )

        cursor = conn.cursor()

        # cursor.execute(f"USE WAREHOUSE {creds['warehouse']}")   

        # Extraer variables del evento (AppSync las pasa en event['arguments'])
        # asset_id = event.get('arguments', {}).get('assetId', 'A1')
        start = event.get('arguments', {}).get('start', '2025-08-01')
        end = event.get('arguments', {}).get('end', '2025-08-21')

        # Consulta SQL
        query = f"""
        SELECT 
            MEASURE_TS,
            PROCESSVARIABLES_GENERATOR_RX_600_CLOCK_PULSE AS value
        FROM CPW_AWS_DB.NB_COPOWER_LA_CIRA_INFANTAS.DIA_NE_XT4_MODEL_ASOF_24HR_VW
        WHERE PROCESSVARIABLES_GENERATOR_RX_600_CLOCK_PULSE IS NOT NULL
        ORDER BY MEASURE_TS
        LIMIT 1000
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Formatear resultado
        result = [
            {
                "timestamp": str(row[0]),
                "value": float(row[1]) if row[1] is not None else None
            }
            for row in rows
        ]

        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Error ejecutando query en Snowflake: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }