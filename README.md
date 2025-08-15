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



¡Gracias por explicarlo tan claramente! Como ya eliminaste el backend de Amplify y estás gestionando tus recursos (incluyendo AppSync) con AWS SAM, entonces no necesitas usar generateClient() ni depender del backend de Amplify Gen 2. Lo que necesitas es una forma directa de conectarte a AppSync desde tu frontend, usando el endpoint y las credenciales que tú controlas.
Aquí te muestro cómo hacerlo paso a paso:

🔌 Conectarte a AppSync desde Next.js (sin Amplify backend)
✅ 1. Usa Apollo Client para GraphQL + suscripciones
AppSync es compatible con GraphQL estándar, así que puedes usar Apollo Client para manejar queries, mutations y suscripciones.

🧱 2. Configura Apollo con WebSocket para suscripciones
// lib/apolloClient.ts
import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';

const httpLink = new HttpLink({
  uri: 'https://<tu-appsync-id>.appsync-api.<region>.amazonaws.com/graphql',
  headers: {
    Authorization: '<tu-token-jwt>', // Puedes obtenerlo desde Cognito o IAM
  },
});

const wsLink = new GraphQLWsLink(
  createClient({
    url: 'wss://<tu-appsync-id>.appsync-realtime-api.<region>.amazonaws.com/graphql',
    connectionParams: {
      Authorization: '<tu-token-jwt>',
    },
  })
);

const splitLink = split(
  ({ query }) => {
    const def = getMainDefinition(query);
    return def.kind === 'OperationDefinition' && def.operation === 'subscription';
  },
  wsLink,
  httpLink
);

export const apolloClient = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});



📡 3. Usa la suscripción en tu componente
import { gql, useSubscription } from '@apollo/client';
import { apolloClient } from '@/lib/apolloClient';
import { ApolloProvider } from '@apollo/client';

const ON_UPDATE = gql`
  subscription OnUpdateStatus {
    onUpdateStatus {
      assetId
      status
      timestamp
    }
  }
`;

const StatusListener = () => {
  const { data, loading } = useSubscription(ON_UPDATE);

  if (loading) return <p>Conectando...</p>;
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
};

export default function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <StatusListener />
    </ApolloProvider>
  );
}



🔐 ¿Y el token JWT?
Si estás usando Cognito para autenticar usuarios, puedes obtener el token así:
import { Auth } from 'aws-amplify';

const jwt = await Auth.currentSession().then(session =>
  session.getIdToken().getJwtToken()
);


Y lo pasas como Authorization en los headers.

🧠 En resumen
Ya que usas SAM para crear AppSync, tu frontend debe conectarse directamente usando:
| Elemento | Solución recomendada | 
| Queries/Mutations | Apollo Client | 
| Suscripciones | Apollo + graphql-ws | 
| Autenticación | Cognito (JWT) o IAM | 



¿Quieres que te ayude a configurar la autenticación con Cognito o a probar una suscripción en tiempo real? Podemos armarlo juntos.

```
// lib/apolloClient.ts
import { ApolloClient, InMemoryCache, HttpLink, split } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';

const httpLink = new HttpLink({
  uri: 'https://<tu-appsync-id>.appsync-api.<region>.amazonaws.com/graphql',
  headers: {
    Authorization: '<tu-token-jwt>', // Puedes obtenerlo desde Cognito o IAM
  },
});

const wsLink = new GraphQLWsLink(
  createClient({
    url: 'wss://<tu-appsync-id>.appsync-realtime-api.<region>.amazonaws.com/graphql',
    connectionParams: {
      Authorization: '<tu-token-jwt>',
    },
  })
);

const splitLink = split(
  ({ query }) => {
    const def = getMainDefinition(query);
    return def.kind === 'OperationDefinition' && def.operation === 'subscription';
  },
  wsLink,
  httpLink
);

export const apolloClient = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});
```
3. Usa la suscripción en tu component
```
import { gql, useSubscription } from '@apollo/client';
import { apolloClient } from '@/lib/apolloClient';
import { ApolloProvider } from '@apollo/client';

const ON_UPDATE = gql`
  subscription OnUpdateStatus {
    onUpdateStatus {
      assetId
      status
      timestamp
    }
  }
`;

const StatusListener = () => {
  const { data, loading } = useSubscription(ON_UPDATE);

  if (loading) return <p>Conectando...</p>;
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
};

export default function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <StatusListener />
    </ApolloProvider>
  );
}
```

