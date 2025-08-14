# Microservicio ingesta

## Hacer push desde EC2

1. Crear una clave SSH
    ```
    ssh-keygen -t ed25519 -C "eficiencia.desarrollo@copower.com.co"
    ```
2. Copiar clave generada `cat ~/.ssh/id_ed25519.pub`

3. En github agregar la clave `→ Settings → SSH and GPG keys`

4. Cambiar la configuracion del remote
    ```
    git remote set-url origin git@github.com:CathaleIA/microservices-catha.git
    ```
5. Tener permisos de GIT `sudo chown -R ec2-user:ec2-user .`


## Desplegar en AWS
1. Clone repositorio en EC2
1. Corrila la imagen que estaba en el EC2 `desploy-merge` (No tengo claro esta imagen).
1. Estrcutura de carpetas:
    ```
    ingestadata/
    ├── IngestaService/
    │   ├── lambda_ingesta.py
    │   └── requirements.txt  # Contiene: boto3 y requests
    ├── template.yaml
    ```
1. Comando para desplegar:  
    ```
    sam build
    sam deploy
    ``` 

    ![recursos](img/resources-deployed.png)

## Conexion con AWS. Mediante Librerias graphql (NO AMPLIFY).

1. Instalar dependencias 
    ```
    npm install aws-amplify
    npm install --save-dev @types/aws-amplify
    ```

1. Agregar varibales de entorno `.env`
    ```
    NEXT_PUBLIC_AWS_REGION=us-east-1
    NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-east-1_hWdkRwqlP
    NEXT_PUBLIC_COGNITO_APP_CLIENT_ID=2s9e6hdscshv3a7si9k3asul5o
    NEXT_PUBLIC_APPSYNC_HTTP_URL=https://ebvdnffnqbe3bfylubwf4mcfy4.appsync-api.us-east-1.amazonaws.com/graphql
    # opcional (Amplify detecta WebSocket internamente)
    NEXT_PUBLIC_APPSYNC_WS_URL=wss://ebvdnffnqbe3bfylubwf4mcfy4.appsync-realtime-api.us-east-1.amazonaws.com/graphql
    ```



