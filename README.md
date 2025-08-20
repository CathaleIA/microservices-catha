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
1. Cree un contenedor con la imagen que estaba en el EC2 `desploy-merge` (No tengo claro esta imagen).
    ```
    [ec2-user@ip-172-31-84-48 microservices-catha]$ docker run -it --rm --privileged -v ~/.aws:/home/ec2-user/.aws:ro -v $(pwd):/home/ec2-user/app -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /etc/docker:/etc/docker --group-add $(stat -c '%g' /var/run/docker.sock) -u root deploy-merge
    ```

1. Estrcutura de carpetas:
    ```
    ingestadata/
    ├── IngestaService/
    │   ├── lambda_ingesta.py
    │   └── requirements.txt
    ├── QueryService/
    │   ├── lambda_query.py
    │   └── requirements.txt
    ├── template.yaml
    ```
1. Comando para desplegar:  
    ```
    sam build
    sam deploy
    ``` 
    ![recursos](img/resources-deployed.png)

## Conexion con AWS. Mediante Apollo.

1. Instalar dependencias 
    ```
    npm install graphql graphql-ws @apollo/client
    npm install subscriptions-transport-ws
    ```

1. Agregar varibales de entorno `.env`
    ```
    NEXT_PUBLIC_APPSYNC_API_URL=https://ebvdnffnqbe3bfylubwf4mcfy4.appsync-api.us-east-1.amazonaws.com/graphql
    NEXT_PUBLIC_APPSYNC_WS_URL=wss://ebvdnffnqbe3bfylubwf4mcfy4.appsync-realtime-api.us-east-1.amazonaws.com/graphql
    ```

## Halar data de APIFAKE



## Conexion de snowflake con AWS

1. Link: https://docs.snowflake.com/en/user-guide/python-connector-install.html

