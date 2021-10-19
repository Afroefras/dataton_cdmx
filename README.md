# Concurso con datos abiertos de la CDMX:
## Se modelan datos de Interrupción Legal del Embarazo y llamadas a la Línea Mujeres, tanto clustering como pronóstico 💜

Colaboración con: @bcisnerose

### Estructura del repositorio:
    .
    ├── ...
    ├── media                           # Directorio con imágenes para README
    │   └── ...
    ├── scripts                         # Directorio con el código necesario para analizar y modelar ILE y LM
    │   ├── mariachis                   # Directorio para ocupar clases y métodos
    │   │   ├── __init__.py             # El folder "mariachis" se puede trabajar de forma modular
    │   │   ├── _base.py                # Clase base, con métodos como extraer los datos vía API, exportarlos, entrenar modelación supervisada y no supervisada, etc
    │   │   ├── ile.py                  # Clase hija de BaseClass, con métodos adicionales específicos para tratar los datos ILE
    │   │   └── localidades.py          # Clase hija de BaseClass, con métodos adicionales específicos para extraer datos de localidades y crear variables de geolocalización
    │   │
    │   ├── ILE_00_Extracción.ipynb     # Se pretende importar vía API para mantener un flujo continuo en el análisis y modelado con nuevos datos
    │   ├── ILE_01_Limpieza.ipynb       # Variables numéricas a rangos, categóricas se normalizan y valores nulos se imputan con la etiqueta "DESCONOCIDO"
    │   ├── ILE_02_Clustering.ipynb     # Agrupación de personas gestantes con decisión de ILE e interpretación de cada grupo
    │   ├── ILE_03_Pronóstico.ipynb     # Primer acercamiento al siguiente paso, pronosticar la cantidad de ILE por clúster obtenido en notebook anterior
    │   ├── ILE_04_Geoloc.ipynb         # Unión con localidades para conocer la distribución de cada clúster
    │   └── Línea_Mujeres.ipynb         # Modelo de pronóstico para llamadas a la LM
    └── requirements.txt                # Instalar las librerías necesarias con el comando: `pip install -r requirements.txt`

<br><br>

## Mujeres - Merecemos ser más que una estadística

### ¿De qué debemos hablar?

Desafortunadamente, no sorprende que los problemas de desigualdad y violencia de género sean una constante en nuestra sociedad y como consecuencia de la pandemia provocada por el COVID-19 [más mujeres se hayan visto afectadas](https://www.bancomundial.org/es/news/feature/2020/05/15/covid-19-could-worsen-gender-inequality-in-latin-america-and-the-caribbean). Todas merecemos ser más que una estadística, merecemos ser más que un número que se suma a la cantidad alarmante de casos diarios, somos personas con un nombre y rostro, somos mujeres con historias de vida, con logros, sueños por cumplir, esperanza y valentía por hacer las cosas diferente.

Por ello, enfocaremos este proyecto en dos problemas sociales con alta urgencia de resolver:
Administración de recursos dada la demanda futura de llamadas a la [Línea Mujeres](https://wradio.com.mx/radio/2019/04/05/sociedad/1554495895_112626.html) (LM)
Personalización de campañas para prevenir los embarazos no deseados, ocupando información de las personas gestantes que acuden a la [Interrupción Legal del Embarazo](https://www.milenio.com/politica/comunidad/aborto-cdmx-273-mil-mujeres-interrumpido-embarazo-2007) (ILE)

En esta época de resiliencia y cambio, queremos dejar huella con nuestras propuestas para que las futuras generaciones no vivan con lo que hasta ahora hemos adoptado como “normal”. Este es el momento indicado para cuestionar y reformular las reglas preestablecidas, porque somos nosotros quienes le ponemos el color al mundo, somos quienes construimos el mañana.


<br><br>

### ¿Qué vamos a lograr?

Los beneficios que la Inteligencia Artificial nos brinda deben ser utilizados a nuestro favor y en este trabajo usaremos diferentes herramientas para cumplir con los siguientes objetivos:

Por un lado, tomando en cuenta los datos de la LM:
- Analizar el comportamiento histórico de cada uno de los servicios que proporciona la línea: jurídico, médico y psicológico.
- Generar un modelo de series de tiempo para cada servicio y <ins>pronosticar la cantidad de llamadas semanales</ins> que se recibirán el siguiente año.

Por otro lado, respecto a la ILE:
- <ins>Agrupar estadísticamente</ins> a las personas gestantes que deciden interrumpir su embarazo.
- Empatizar con la vulnerabilidad de cada grupo para priorizar a través de un semáforo.
- Abrir la posibilidad de generar campañas personalizadas e innovadoras enfocadas en las características que hacen diferente a cada grupo y sobre todo, considerando también a la pareja.


<br><br>

### ¿Por qué es urgente solucionarlo?

Si bien, de primera instancia los dos temas parecen tener un enfoque diferente, ambos se centran en la desigualdad que una persona padece simplemente por haber nacido mujer. Es inaceptable concebir los [altos grados de violencia](https://www.jornada.com.mx/notas/2021/09/25/capital/diariamente-detectan-dos-casos-de-violencia-feminicida-en-cdmx/) que suceden diariamente. 

Existen oficinas especializadas en la atención a las mujeres como [SEMUJERES](https://www.semujeres.cdmx.gob.mx/) con múltiples campañas para frenar a esta [pandemia tan peligrosa](https://www.televisa.com/noticias/unam-violencia-contra-las-mujeres-se-disparo-durante-pandemia-de-covid-19/) que la vivida en los últimos años. Dicha institución lanzó en el 2019 su campaña [#YoDecidoMiFuturo](https://www.semujeres.cdmx.gob.mx/comunicacion/nota/estrategia-para-prevencion-del-embarazo-en-adolescentes-yodecidomifuturo) con el objetivo de evitar el embarazo antes de los 19 años. Adicionalmente, el gobierno federal retomó en 2020, la [Estrategia Nacional para la Prevención del Embarazo en Adolescentes](https://www.jornada.com.mx/ultimas/sociedad/2020/08/14/gobierno-relanza-campana-para-reducir-embarazos-adolescentes-863.html) (ENAPEA) buscando erradicar los embarazos de niñas de 14 años o menos. Incluso en este año, durante septiembre se presentaron las campañas: [¡Yo decido! y ¡Yo exijo respeto!](https://mexico.unfpa.org/es/news/presentan-campa%C3%B1a-para-prevenci%C3%B3n-y-erradicaci%C3%B3n-de-embarazo-en-ni%C3%B1ez-adolescencias-y), que se enfoca principalmente a la población en entornos rurales e indígenas. 

Sin embargo, no podemos quitar el dedo del renglón, el problema de la violencia de género debe ser atacado desde nuevas perspectivas, apoyados de los avances estadísticos de última tecnología para desarrollar soluciones que presenten empatía y ataquen de raíz la problemática de origen.

<br><br>

### ¡Este es nuestro proyecto!
#### ¿Cómo obtenemos valor de la información?

La información es importada desde archivos en formato .csv* y se emplea el lenguaje de programación Python para la limpieza, estructuración y modelado estadístico. El tratamiento consta de lo siguiente:

[Llamadas realizadas a la Línea Mujeres](https://datos.cdmx.gob.mx/dataset/linea-mujeres), cabe señalar que para la correcta generación del pronóstico los siguientes pasos se realizaron para cada uno de los tres servicios proporcionados: médico, jurídico y psicológico.

1. **Agrupación semanal** del número de llamadas recibidas.
2. **Tratamiento de datos atípicos** mediante el método [Hampel Filter](https://medium.com/wwblog/clean-up-your-time-series-data-with-a-hampel-filter-58b0bb3ebb04#:~:text=A%20Hampel%20filter%20is%20a,them%20with%20more%20representative%20values.&text=For%20any%20point%20in%20the,it%20with%20the%20window's%20median.). El cual considera la mediana de las observaciones tomando una ventana de tiempo. Si una muestra difiere de la mediana en más de k desviaciones estándar, se considera un dato atípico y se reemplaza por la mediana. Para el presente trabajo consideraremos k=3 y una ventana de tiempo de 10 periodos.

<div align="center"><i>Gráfica 1. Aplicación de Hampel Filter para la serie de tiempo de llamadas con servicio Psicológico (atípicos: azul)</i></div>

![Alt text](media/LM_Hampel_Filter.png?raw=true "Hampel Filter")
<div align="center"><i>Fuente: Elaboración propia con imputación de valores atípicos</i></div>
<br>


3. **Entrenamiento del modelo** de series de tiempo para la etapa de evaluación, se utiliza el modelo de Prophet, el fue desarrollado por la comunidad de Facebook. Las últimas 52 semanas de las ya sucedidas no serán consideradas al momento de entrenar para poder evaluar el ajuste que tiene el modelo ante la historia, obteniendo el porcentaje de error (MAPE) y disminuirlo.
4. **Re-entrenamiento del modelo** con todas las observaciones disponibles, esto después de haber obtenido un porcentaje de error aceptable.
5. **Generación del pronóstico** y bandas de confianza, con una probabilidad del 80%, de las siguientes 52 semanas.

<br>

[Interrupción Legal del Embarazo](https://datos.cdmx.gob.mx/dataset/interrupcion-legal-del-embarazo)

1. Limpieza de datos. Se cuenta con 47 columnas de diferentes tipos, sin embargo al encontrar valores nulos en al menos un valor para todas ellas, se decide aplicar una transformación categórica y así, <ins>con todo el respeto que cada registro merece</ins>, no omitir ni imputar información:
    - Variables numéricas serán representadas en rangos. Ej: edad en años=23 → “22 a 25 años”.
    - Variables categóricas serán normalizadas, es decir, agrupamos sus opciones.
    - Los registros que tengan valores nulos, es decir, que cierta pregunta no fue contestada, se le asignará la etiqueta “DESCONOCIDO” así todas las variables ahora son categóricas y <ins>no se omite ni imputa ningún valor</ins>.
2. Agrupación de personas gestantes con decisión de ILE en 10 clústers con algoritmo [KModes](https://www.analyticsvidhya.com/blog/2021/06/kmodes-clustering-algorithm-for-categorical-data/) al tratarse de variables categóricas. Después de interpretar las diferencias entre cada grupo, se propone un semáforo de vulnerabilidad: rojo, naranja y amarillo. El color verde no se utilizará porque ninguna persona gestante tendría que pasar por una ILE: la maternidad debería ser deseada.
3. Frecuencia por localidad, se contesta la pregunta: ¿Cómo se distribuye cada uno de los 10 grupos en esta alcaldía o municipio? Con el objetivo de agrupar alcaldías con frecuencias similares.
4. Personalización de campañas. Con la información limpia, organizada y segmentada en grupos, tanto de ILE como de alcaldías, tenemos la oportunidad de dirigir diferentes campañas a donde más lo necesita y a quien más lo necesita.
<br>

*Nota: Se intenta importar la información vía API pero la cantidad de registros para cada tabla, supera el límite de 32 mil registros permitidos*

<br><br>

### ¿Qué descubrimos?


Sin duda los hallazgos generaron un impacto, no siempre son agradables pero se tiene la responsabilidad de difundirlos y proponer estrategias para mitigar la desigualdad que puedan presentar, directa o indirectamente.

Por parte de la LM, se notó que la cantidad de llamadas para atender temas relacionados con la psicología van en aumento con el paso de los años, además se pronostica que para el 2022 se continúe con una tendencia positiva. Esto puede ser interpretado desde dos perspectivas: existe mayor conciencia respecto a las emociones y que los servicios psicológicos sean más requeridos por el [aumento en casos de depresión y ansiedad](https://cnnespanol.cnn.com/2021/10/11/cuarta-parte-poblacion-mundial-ansiedad-depresion-covid-19-trax/) en los últimos años, debido al confinamiento y otros problemas sociales que nos rodean.

<div align="center"><i>Gráfica 2. Distribución de llamadas por tipo de servicio</i></div>

![Alt text](media/LM_Dist_Servicios_anual.png?raw=true "Distribución de Servicios por año")
<div align="center"><i>Fuente: Elaboración propia con datos de LM</i></div>
<br>

Partiendo del hecho de que el servicio de asesorías está disponible los 365 días del año y las 24 horas, los días con mayor cantidad de llamadas son de lunes a jueves, mientras que durante el fin de semana, la tendencia disminuye de forma gradual, siendo el domingo el día con menor llamadas. El comportamiento por día de la semana nos da visibilidad para asignar de forma correcta los recursos de atención en la línea.


<div align="center"><i>Gráfica 3. Distribución de llamadas por día de la semana y año</i></div>

![Alt text](media/LM_Dist_Servicios_semanal.png?raw=true "Distribución de Servicios por día de la semana")
<div align="center"><i>Fuente: Elaboración propia con datos de LM</i></div>
<br>

Para el modelo **Jurídico**, se percibe una tendencia a la baja para el siguiente año, adicionalmente se notó que existe una estacionalidad muy marcada, pues en el mes de enero se presenta el punto más bajo en la recepción de llamadas, mientras que marzo y junio son los meses con mayor cantidad. 

<div align="center"><i>Gráfica 4. Pronóstico y tendencias del modelo Jurídico</i></div>

![Alt text](media/LM_modelo_Juridico.png?raw=true "Modelo Jurídico")
<div align="center"><i>Fuente: Elaboración propia con resultado del modelo Jurídico</i></div>
<br>

El modelo **Médico** es diferente, se tiene una tendencia a la alza. Respecto a la tendencia por mes, para finales de octubre se presenta el periodo con menor llamadas recibidas y el punto más alto es a mediados de marzo. Al menos para el 2020, lo anterior puede ser una consecuencia del impacto de la pandemia ante el COVID-19.

<div align="center"><i>Gráfica 4. Pronóstico y tendencias del modelo Médico</i></div>

![Alt text](media/LM_modelo_Medico.png?raw=true "Modelo Médico")
<div align="center"><i>Fuente: Elaboración propia con resultado del modelo Médico</i></div>
<br>

Por último y no por ello menos importante, el modelo **Psicológico** también tiene una tendencia a la alta, siendo enero el mes con menos llamadas y mayo junto con junio los periodos en los que más mujeres se comunican para recibir apoyo con temas psicológicos.

<div align="center"><i>Gráfica 4. Pronóstico y tendencias del modelo Psicológico</i></div>

![Alt text](media/LM_modelo_Psicologico.png?raw=true "Modelo Psicológico")
<div align="center"><i>Fuente: Elaboración propia con resultado del modelo Psicológico</i></div>
<br>

La métrica utilizada para evaluar el comportamiento de cada modelo de series de tiempo fue el error porcentual absoluto medio (MAPE por sus siglás en inglés: Mean Absolute Percentage Error). Cabe señalar que los datos atípicos pueden afectar dicho error, es por ello que para el modelo Médico se excluyeron dichos registros atípicos debido al inicio de la pandemia en 2020.

*Tabla 1. MAPE por modelo, sin tomar en cuenta registros atípicos*
|Métrica|Jurídico|Médico|Psicológico|
|:---:|:---:|:---:|:---:|
|**MAPE**|17%|21%|16%|

*Fuente: Elaboración propia con resultados de modelación LM*
<br><br>

Ahora, respecto a los **hallazgos de la ILE**, descubrimos que parece haber una tendencia a la baja desde 2016, sin embargo a partir de 2019 se tiene un ascenso en la tendencia de la ILE. En definitiva a partir de abril 2020, la tendencia cambia radicalmente lo que nos hace preguntarnos: ¿Cuántos embarazos no deseados ocurrieron sin oportunidad de asistir a la ILE?

<div align="center"><i>Gráfica 7. Cantidad de personas gestantes (en miles) pre-pandemia</i></div>

![Alt text](media/ILE_tendencia_mensual.png?raw=true "ILE: tendencia mensual")
<div align="center"><i>Fuente: Elaboración propia con datos de ILE</i></div>
<br>

Adicionalmente, el 64% de las personas gestantes que acuden a la ILE provienen de la CDMX y el 31% del Estado de México. El 5% restante está centralizado geográficamente en el país, esto significa falta de difusión a los estados que están alejados de la capital, tal es el caso de Campeche: desde 2016 han asistido a la ILE solamente 5 personas.

<div align="center"><i>Imagen 1. Mapa de calor: frecuencia de ILE (sin contar CDMX ni Estado de México)</i></div>

![Alt text](media/ILE_Heatmap.png?raw=true "ILE: Mapa de calor MX")
<div align="center"><i>Fuente: Elaboración propia en sitio web: DanielPinero.com</i></div>
<br>

Es muy importante dejar claro que aplicar un algoritmo de clustering para encontrar grupos con características en común no significa solamente catalogar registros, si no que **se respeta la individualidad de cada persona gestante** y confiamos en las herramientas que la estadística nos ofrece para generar mejores soluciones. Dicho esto, las características de cada grupo son:

&#x203C; **Semáforo de vulnerabilidad ROJO**
1. Con alta incidencia en 2016, provenientes en su mayoría del Estado de México y Ciudad de México siendo empleadas, con edades entre 26 a 29 años y un hijo en promedio, son quienes usaban condón y no especifican Método de Planificación familiar (MPF) posterior, además se desconocen abortos, cesáreas, ILE previas, menarca e Inicio de Vida Sexual Activa (IVSA). Acudieron con siete Semanas De Gestación (SDG) y recibieron terapia dual, además se desconocen complicaciones en el procedimiento.
    - Ahora bien, hay mujeres que pertenecen a un grupo minoritario pero no representan a todo el clúster aún cuando tienen características similares con él, sin embargo es importante hacer mención de estas minorías que pueden interpretarse como un subconjunto del clúster. En este, la minoría de mujeres tienen una o más de las siguientes características:
        - Máximo primaria o incluso sin acceso a la educación
        - Mantienen el mismo método anticonceptivo antes y después del ILE
        - Tienen algún seguro (IMSS, ISSSTE, etc.)
        - Mujeres casadas
        - No firmaron o se desconoce si firmaron el consentimiento informado
        - IVSA menor a los 8 años
        - Hay quienes han tenido 2 o más gestas
        
2. Acudieron en su mayoría durante 2019, del total de este grupo, son estudiantes de preparatoria con 19 a 21 años y sin hijos. Primera menstruación (Menarca) a los 12 años, IVSA cinco años después por lo que es muy probable que el procedimiento de ILE sea de su primera gesta.
    - Es muy importante recalcar que del universo de mujeres que tuvieron complicaciones en la ILE, la mayoría está en este clúster

3. Trabajadoras del hogar no remuneradas con preparatoria, de 22 a 29 años en unión libre con 1 hijo. Mantienen el condón como MPF después del procedimiento. Acuden con diez semanas o más de gestación sin citas previas. Presencia de dolor después del procedimiento por lo que se prescriben analgésicos.
<br>

&#x1F536; **Semáforo de vulnerabilidad NARANJA**
1. Mujeres foráneas que acuden en 2018, o son estudiantes o no contestaron ocupación, con edades de 19 a 21 años y sin hijos. Recibieron dos citas previas, consejería, terapia dual y se prescribió analgésico.
2. Trabajadoras del hogar no remuneradas de 22 a 25 años con secundaria y sin hijos. Menarca ligeramente tardía respecto al promedio: a los 13 años. Recibieron terapia dual y se desconoce si hubo complicaciones.
3. Trabajadoras del hogar no remuneradas de 22 a 35 años con secundaria y dos hijos en promedio. No ocupan MPF y acuden con una cita previa y siete semanas de gestación, recibe terapia dual y sin dolor después del procedimiento.
4. Trabajadoras del hogar no remuneradas de 30 a 35 años con secundaria, en unión libre con uno o más hijos y acuden acompañadas por su pareja. Es referida de otra unidad  con tres o más citas previas, hubo dolor por lo que se prescribió analgésico.
5. Alta frecuencia en 2020, personas de diferentes niveles educativos (pocos sin acceso a la educación) con edades entre 22 a 25 sin hijos ni MPF previo. Recibieron consejería y no se complica el procedimiento ni tuvieron dolor después de él.
    - La minoría de mujeres separadas y/o desempleadas están en este grupo.
<br>

&#x26A0; **Semáforo de vulnerabilidad AMARILLO**
1. No se conoce la fecha de la ILE, estudiantes o empleadas entre 19 y 29 años sin hijos. Acude acompañada de alguien de confianza, directamente a ser atendida por especialidad de gineco-obstetricia con seis a ocho semanas de gestación, no hay dolor después del procedimiento.
2. Mujeres mexiquenses que acuden en 2017 de 22 a 25 años de edad, empleadas y sin hijos. Sin MPF previo y después se deciden por implante. Recibieron consejería y terapia dual, no se complica el procedimiento.
<br>

Aún cuando no se utilizó la variable fecha (ni en ninguna división como año, trimestre, mes) para generar los clústers, es muy interesante cómo los 10 grupos obtenidos (y a su vez agrupados por semáforo de vulnerabilidad) tienen tendencias notables a lo largo del tiempo.

<div align="center"><i>Gráfica 8. Personas gestantes (en miles) por año-trimestre y semáforo de vulnerabilidad</i></div>

![Alt text](media/ILE_tendencia_trimestral.png?raw=true "ILE: Tendencia trimestral por semáforo")
<div align="center"><i>Fuente: Elaboración propia con resultado del modelo ILE</i></div>
<br><br>

## Propuestas y conclusiones

Por un lado, tomando en cuenta el modelo de series de tiempo sobre la recepción de llamadas en la Linea Mujeres para las siguientes 52 semanas se propone el uso de datos en dos perspectivas: 

1. Administración de los recursos: Al conocer las futuras necesidades de las usuarias, tenemos visibilidad en cuanto a la cantidad de profesionales que deberán atender dicha demanda. Ayuda ante la toma de decisiones para futuras contrataciones o redistribución de los actuales. 
2. Visibilidad para las instituciones: Dado que la Línea Mujeres también ayuda a canalizar los casos con instituciones que ayuden a darle seguimiento, el modelo de series de tiempo podría ser una indicador para dichas instituciones sobre los futuros casos que podrían recibir.

Por otro lado para el modelo ILE, la agrupación de personas gestantes con decisión de ILE y a su vez, la distribución en las diferentes alcaldías y municipios, facilita una personalización de campañas con un enfoque directo: planificación familiar en jóvenes, seguridad para menores de edad, medicina preventiva para evitar complicaciones, propuesta de MPF según la edad y otras características que el modelo ya captura en su generalidad. Además, conocer dónde se ubican las minorías con problemas sociales importantes nos permite atacarlos de raíz, evitando los embarazos no deseados ocupando las herramientas estadísticas que hoy en día la tecnología pone al alcance de todos, tanto en este modelo ILE como en el modelo de la Línea Mujeres, para brindar la atención que cada mujer merece, para lograr lo que merecemos: ser más que una estadística.

<div align="center"><i>Gráfica 9. Distribución porcentual de semáforo por clusters de localidades ILE</i></div>

![Alt text](media/ILE_semaforo_localidad.png?raw=true "ILE: Distribución de semáforo por localidades")
<div align="center"><i>Fuente: Elaboración propia con resultado de clustering por localidad según distribución de grupos ILE</i></div>
<br>

Los siguientes pasos para incrementar aún más el valor de los datos públicos, se propone:
- Para LM, generar clusters de las llamadas recibidas con el objetivo de crear campañas para la prevención de los casos, es decir, buscar reducir la cantidad de llamadas como consecuencia de campañas efectivas y no por desconocimiento de la existencia de la línea. Dicha segmentación deberá realizarse dentro de cada uno de los tres servicios para obtener una distribución de grupos mucho más efectiva.
- Para ILE, modelar el pronóstico para cada grupo obtenido y así como con los servicios de LM, se podrían distribuir los recursos y difusión oportunamente, anticipando la demanda y necesidad de cada persona gestante que decide interrumpir su embarazo.

<br><br>

<div align="center"><strong>¡¡¡GRACIAS!!!!</strong></div>
<br><br>

> El documento presentado se ubica en este [link](https://docs.google.com/document/d/1mNU70JAsVT5-yrPMIfRxTJuGtVDPpv96FVTullAEqpc/edit?usp=sharing)