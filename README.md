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
1. Libreria para firmar solicitudes a appsync con IAM, se instalo desde EC2 en la raiz del proyecto, cuando se hace sam build el lee los archivos.
    ```
    pip install requests requests-aws4auth -t IngestaService/
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
    npm install @apollo/client aws-appsync-auth-link aws-appsync-subscription-link graphql
    ```

1. Agregar varibales de entorno `.env`
    ```
    NEXT_PUBLIC_APPSYNC_API_URL=https://ebvdnffnqbe3bfylubwf4mcfy4.appsync-api.us-east-1.amazonaws.com/graphql
    NEXT_PUBLIC_APPSYNC_WS_URL=wss://ebvdnffnqbe3bfylubwf4mcfy4.appsync-realtime-api.us-east-1.amazonaws.com/graphql
    ```

1. Documentacion oficial
    1. [Building a real-time WebSocket client in AWS AppSync](https://docs.aws.amazon.com/appsync/latest/devguide/real-time-websocket-client.html)

    1. [Opciones para conectar Nextj con Appsync, libreria final actualizada](https://docs.amplify.aws/gen1/nextjs/prev/build-a-backend/graphqlapi/upgrade-guide/)

    

## Halar data de APIFAKE



## Conexion de snowflake con AWS

1. Link: https://docs.snowflake.com/en/user-guide/python-connector-install.html

1. Se guardaron las credenciales de acceso a AWS en Secrets Manager de AWS.



Prop para querys inteligentes a snowflake.
```
habalme mas sobre la opcion donde plotly inicia en 7d por ejemplo, y cuando cambie realiza otra consulta, lo quiero asi porque un mes tendra menos puntos que un dia por ejemplo, como soy capaz de leer cuando acciono un boton de rangeselector? , esto hay sobre evento en la libreria de plotly: export interface PlotMouseEvent {
    points: PlotDatum[];
    event: MouseEvent;
}

export interface PlotHoverEvent extends PlotMouseEvent {
    xvals: Datum[];
    yvals: Datum[];
}

export interface PlotCoordinate {
    x: number;
    y: number;
    pointNumber: number;
}

export interface SelectionRange {
    x: number[];
    y: number[];
}

export type PlotSelectedData = Partial<PlotDatum>;

export interface PlotSelectionEvent {
    points: PlotDatum[];
    range?: SelectionRange | undefined;
    lassoPoints?: SelectionRange | undefined;
}

export interface PlotRestyleEventUpdate {
    [key: string]: any;
}

export type PlotRestyleEvent = [PlotRestyleEventUpdate, number[]];

export interface PlotScene {
    center: Point;
    eye: Point;
    up: Point;
}

export interface PlotRelayoutEvent extends Partial<Layout> {
    "xaxis.range[0]"?: number;
    "xaxis.range[1]"?: number;
    "yaxis.range[0]"?: number;
    "yaxis.range[1]"?: number;
    "xaxis.autorange"?: boolean;
    "yaxis.autorange"?: boolean;
}

export interface ClickAnnotationEvent {
    index: number;
    annotation: Annotations;
    fullAnnotation: Annotations;
    event: MouseEvent;
}

export interface FrameAnimationEvent {
    name: string;
    frame: Frame;
    animation: {
        frame: AnimationFrameOpts;
        transition: Transition;
    };
}

export interface LegendClickEvent {
    event: MouseEvent;
    node: PlotlyHTMLElement;
    curveNumber: number;
    expandedIndex: number;
    data: Data[];
    layout: Partial<Layout>;
    frames: Frame[];
    config: Partial<Config>;
    fullData: Data[];
    fullLayout: Partial<Layout>;
}
export interface SliderChangeEvent {
    slider: Slider;
    step: SliderStep;
    interaction: boolean;
    previousActive: number;
}

export interface SliderStartEvent {
    slider: Slider;
}

export interface SliderEndEvent {
    slider: Slider;
    step: SliderStep;
}

export interface SunburstClickEvent {
    event: MouseEvent;
    nextLevel: string;
    points: SunburstPlotDatum[];
}

export interface SunburstPlotDatum {
    color: number;
    curveNumber: number;
    data: Data;
    entry: string;
    fullData: Data;
    hovertext: string;
    id: string;
    label: string;
    parent: string;
    percentEntry: number;
    percentParent: number;
    percentRoot: number;
    pointNumber: number;
    root: string;
    value: number;
}

export interface BeforePlotEvent {
    data: Data[];
    layout: Partial<Layout>;
    config: Partial<Config>;
}

export interface PlotlyHTMLElement extends HTMLElement {
    on(event: "plotly_click" | "plotly_unhover", callback: (event: PlotMouseEvent) => void): void;
    on(event: "plotly_hover", callback: (event: PlotHoverEvent) => void): void;
    on(event: "plotly_selecting" | "plotly_selected", callback: (event: PlotSelectionEvent) => void): void;
    on(event: "plotly_restyle", callback: (data: PlotRestyleEvent) => void): void;
    on(event: "plotly_relayout" | "plotly_relayouting", callback: (event: PlotRelayoutEvent) => void): void;
    on(event: "plotly_clickannotation", callback: (event: ClickAnnotationEvent) => void): void;
    on(event: "plotly_animatingframe", callback: (event: FrameAnimationEvent) => void): void;
    on(event: "plotly_legendclick" | "plotly_legenddoubleclick", callback: (event: LegendClickEvent) => boolean): void;
    on(event: "plotly_sliderchange", callback: (event: SliderChangeEvent) => void): void;
    on(event: "plotly_sliderend", callback: (event: SliderEndEvent) => void): void;
    on(event: "plotly_sliderstart", callback: (event: SliderStartEvent) => void): void;
    on(event: "plotly_sunburstclick", callback: (event: SunburstClickEvent) => void): void;
    on(event: "plotly_event", callback: (data: any) => void): void;
    on(event: "plotly_beforeplot", callback: (event: BeforePlotEvent) => boolean): void;
    on(
        event:
            | "plotly_afterexport"
            | "plotly_afterplot"
            | "plotly_animated"
            | "plotly_animationinterrupted"
            | "plotly_autosize"
            | "plotly_beforeexport"
            | "plotly_deselect"
            | "plotly_doubleclick"
            | "plotly_framework"
            | "plotly_redraw"
            | "plotly_transitioning"
            | "plotly_transitioninterrupted",
        callback: () => void,
    ): void;
    removeAllListeners: (handler: string) => void;
    data: Data[];
    layout: Layout;
} 
```

