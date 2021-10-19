# Concurso con datos abiertos de la CDMX
============================

### Estructura del repositorio:
    .
    ├── ...
    ├── scripts                         # Directorio con el código necesario para analizar y modelar ILE y LM
    │   ├── mariachis                   # Directorio para ocupar clases y métodos
    │   │   ├── __init__.py             # El folder "mariachis" se puede trabajar de forma mdoular
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


============================

## Proyecto: Mujeres - Merecemos ser más que una estadística

### ¿De qué debemos hablar?

Desafortunadamente, no sorprende que los problemas de desigualdad y violencia de género sean una constante en nuestra sociedad y como consecuencia de la pandemia provocada por el COVID-19 [más mujeres se hayan visto afectadas](https://www.bancomundial.org/es/news/feature/2020/05/15/covid-19-could-worsen-gender-inequality-in-latin-america-and-the-caribbean). Todas merecemos ser más que una estadística, merecemos ser más que un número que se suma a la cantidad alarmante de casos diarios, somos personas con un nombre y rostro, somos mujeres con historias de vida, con logros, sueños por cumplir, esperanza y valentía por hacer las cosas diferente.

Por ello, enfocaremos este proyecto en dos problemas sociales con alta urgencia de resolver:
Administración de recursos dada la demanda futura de llamadas a la [Línea Mujeres](https://wradio.com.mx/radio/2019/04/05/sociedad/1554495895_112626.html) (LM)
Personalización de campañas para prevenir los embarazos no deseados, ocupando información de las personas gestantes que acuden a la [Interrupción Legal del Embarazo](https://www.milenio.com/politica/comunidad/aborto-cdmx-273-mil-mujeres-interrumpido-embarazo-2007) (ILE)

En esta época de resiliencia y cambio, queremos dejar huella con nuestras propuestas para que las futuras generaciones no vivan con lo que hasta ahora hemos adoptado como “normal”. Este es el momento indicado para cuestionar y reformular las reglas preestablecidas, porque somos nosotros quienes le ponemos el color al mundo, somos quienes construimos el mañana.

### ¿Qué vamos a lograr?

Los beneficios que la Inteligencia Artificial nos brinda deben ser utilizados a nuestro favor y en este trabajo usaremos diferentes herramientas para cumplir con los siguientes objetivos:

Por un lado, tomando en cuenta los datos de la LM:
- Analizar el comportamiento histórico de cada uno de los servicios que proporciona la línea: jurídico, médico y psicológico.
- Generar un modelo de series de tiempo para cada servicio y <ins>pronosticar la cantidad de llamadas semanales</ins> que se recibirán el siguiente año.

Por otro lado, respecto a la ILE:
- <ins>Agrupar estadísticamente</ins> a las personas gestantes que deciden interrumpir su embarazo.
- Empatizar con la vulnerabilidad de cada grupo para priorizar a través de un semáforo.
- Abrir la posibilidad de generar campañas personalizadas e innovadoras enfocadas en las características que hacen diferente a cada grupo y sobre todo, considerando también a la pareja.

### ¿Por qué es urgente solucionarlo?

Si bien, de primera instancia los dos temas parecen tener un enfoque diferente, ambos se centran en la desigualdad que una persona padece simplemente por haber nacido mujer. Es inaceptable concebir los [altos grados de violencia](https://www.jornada.com.mx/notas/2021/09/25/capital/diariamente-detectan-dos-casos-de-violencia-feminicida-en-cdmx/) que suceden diariamente. 

Existen oficinas especializadas en la atención a las mujeres como [SEMUJERES](https://www.semujeres.cdmx.gob.mx/) con múltiples campañas para frenar a esta [pandemia tan peligrosa](https://www.televisa.com/noticias/unam-violencia-contra-las-mujeres-se-disparo-durante-pandemia-de-covid-19/) que la vivida en los últimos años. Dicha institución lanzó en el 2019 su campaña [#YoDecidoMiFuturo](https://www.semujeres.cdmx.gob.mx/comunicacion/nota/estrategia-para-prevencion-del-embarazo-en-adolescentes-yodecidomifuturo) con el objetivo de evitar el embarazo antes de los 19 años. Adicionalmente, el gobierno federal retomó en 2020, la [Estrategia Nacional para la Prevención del Embarazo en Adolescentes](https://www.jornada.com.mx/ultimas/sociedad/2020/08/14/gobierno-relanza-campana-para-reducir-embarazos-adolescentes-863.html) (ENAPEA) buscando erradicar los embarazos de niñas de 14 años o menos. Incluso en este año, durante septiembre se presentaron las campañas: [¡Yo decido! y ¡Yo exijo respeto!](https://mexico.unfpa.org/es/news/presentan-campa%C3%B1a-para-prevenci%C3%B3n-y-erradicaci%C3%B3n-de-embarazo-en-ni%C3%B1ez-adolescencias-y), que se enfoca principalmente a la población en entornos rurales e indígenas. 

Sin embargo, no podemos quitar el dedo del renglón, el problema de la violencia de género debe ser atacado desde nuevas perspectivas, apoyados de los avances estadísticos de última tecnología para desarrollar soluciones que presenten empatía y ataquen de raíz la problemática de origen.

### ¡Este es nuestro proyecto!
#### ¿Cómo obtenemos valor de la información?

La información es importada desde archivos en formato .csv* y se emplea el lenguaje de programación Python para la limpieza, estructuración y modelado estadístico. El tratamiento consta de lo siguiente:

[Llamadas realizadas a la Línea Mujeres](https://datos.cdmx.gob.mx/dataset/linea-mujeres), cabe señalar que para la correcta generación del pronóstico los siguientes pasos se realizaron para cada uno de los tres servicios proporcionados: médico, jurídico y psicológico.

1. **Agrupación semanal** del número de llamadas recibidas.
2. **Tratamiento de datos atípicos** mediante el método [Hampel Filter](https://medium.com/wwblog/clean-up-your-time-series-data-with-a-hampel-filter-58b0bb3ebb04#:~:text=A%20Hampel%20filter%20is%20a,them%20with%20more%20representative%20values.&text=For%20any%20point%20in%20the,it%20with%20the%20window's%20median.). El cual considera la mediana de las observaciones tomando una ventana de tiempo. Si una muestra difiere de la mediana en más de k desviaciones estándar, se considera un dato atípico y se reemplaza por la mediana. Para el presente trabajo consideraremos k=3 y una ventana de tiempo de 10 periodos.

*Gráfica 1. Aplicación de Hampel Filter para la serie de tiempo de llamadas con servicio Psicológico (atípicos: azul)*
![Alt text](media/Hampel_Filter.png?raw=true "Hampel Filter")
*Fuente: Elaboración propia con imputación de valores atípicos*

3. **Entrenamiento del modelo** de series de tiempo para la etapa de evaluación, se utiliza el modelo de Prophet, el fue desarrollado por la comunidad de Facebook. Las últimas 52 semanas de las ya sucedidas no serán consideradas al momento de entrenar para poder evaluar el ajuste que tiene el modelo ante la historia, obteniendo el porcentaje de error (MAPE) y disminuirlo.
4. **Re-entrenamiento del modelo** con todas las observaciones disponibles, esto después de haber obtenido un porcentaje de error aceptable.
5. **Generación del pronóstico** y bandas de confianza, con una probabilidad del 80%, de las siguientes 52 semanas.



> Se presenta el documento en este [link](https://docs.google.com/document/d/1mNU70JAsVT5-yrPMIfRxTJuGtVDPpv96FVTullAEqpc/edit?usp=sharing)