# 0001. Calcular seis regímenes y atribuir cada indeterminado en lugar de devolver una fecha

- Estado: aceptada
- Fecha: 22/09/2026

## Contexto

Los sujetos obligados por la normativa de prevención del blanqueo de capitales (PBC) tienen que mantener actualizada la información de sus clientes durante toda la relación de negocios. La obligación se cumple con revisiones periódicas y con revisiones que provocan ciertos hechos:

- **Ley 10/2010, art. 6:** seguimiento continuo para «garantizar que los documentos, datos e información de que se disponga estén actualizados».
- **RD 304/2014, art. 11.2:** «procesos de revisión» periódicos. Art. 33.1.b: una actualización «preceptiva cuando se verifique un cambio relevante en la actividad del cliente».
- **AMLR, art. 26.2 y 26.3:** actualización periódica y revisión cuando cambian las circunstancias del cliente, cuando hay que contactarle por sus titulares reales o por la Directiva 2011/16/UE, o cuando la entidad conoce un hecho relevante.

La pregunta práctica es cuándo hay que revisar a cada cliente y si, en una fecha dada, la revisión está en plazo o vencida. Revisar tarde es un incumplimiento. Revisar antes de lo necesario no lo es, pero cuesta, y en una cartera grande el calendario de revisiones es trabajo planificado.

El plazo cambia de naturaleza con el AMLR:

- **Con el RD, el plazo lo decide el manual.** Art. 11.2: «El manual [...] determinará, en función del riesgo, la periodicidad de los procesos de revisión documental que para los clientes de riesgo superior al promedio será, como mínimo, anual». Para el resto no hay plazo legal: cada entidad fija el suyo.
- **Con el AMLR, hay un máximo.** Art. 26.2: el período entre actualizaciones «no será en ningún caso superior a» un año para los clientes de riesgo elevado a los que se aplican las medidas de la sección 4, y cinco años para todos los demás. Es aplicable desde el 10 de julio de 2027 (art. 90).

Ningún texto regula a los clientes que ya lo son el 10 de julio de 2027. El AMLR no tiene disposición transitoria sobre el seguimiento continuo, y la Ley consolidada a 21 de marzo de 2026 no tiene ninguna adaptación. Para un cliente de riesgo bajo con un manual de diez años, revisado en enero de 2024, la próxima revisión puede ser en 2034 (sigue el RD), en 2029 (el AMLR desde la última revisión) o en 2032 (el AMLR desde el 10 de julio de 2027). Es el caso 03 del corpus.

Además, el art. 26.5 del AMLR encarga a la AMLA directrices sobre el seguimiento continuo. En la fecha de esta decisión solo hay un borrador sometido a consulta, sin efecto normativo, y las directrices finales se esperan en el cuarto trimestre de 2026. El borrador toma posición en al menos un punto que cambia fechas: una revisión anticipada «can reset» el plazo de la siguiente (ap. 2).

## Decisión

**1. La herramienta calcula seis regímenes y atribuye cada `indeterminado` a las dimensiones que lo causan. No devuelve una fecha.**

Los seis son el RD aplicado solo (`ley_rd`), el AMLR aplicado solo (`amlr`) y cuatro lecturas de la transición (T-1 a T-4). Se calculan siempre los seis y ninguno es el principal ([especificación](../especificacion-calculo.md), §1.1 y §5; D-4). Dentro de cada régimen, cada pregunta que la norma no resuelve es una **dimensión de lectura** con sus respuestas posibles. El régimen es `indeterminado` si las respuestas dan estados distintos.

A cada `indeterminado` se le atribuyen las dimensiones que lo causan: las que, en alguna combinación de las demás, cambian el estado al cambiar solo ellas (D-30). No hay una combinación de referencia, porque la herramienta no elige lecturas. Así se atribuyen también las dimensiones que solo cambian el estado junto con otra.

Hay tres razones.

- **Diecisiete casos que la norma no resuelve** ([ambiguedades.md](../ambiguedades.md)), y varios cambian el estado en clientes corrientes:
  - si una revisión sin cambios cuenta como actualización para el AMLR (S-6): con la lectura que no la cuenta, un cliente revisado a tiempo sale vencido;
  - si el plazo de un año del AMLR exige riesgo elevado y medidas de la sección 4 o basta uno, lo que decide si una persona del medio político se revisa cada año o cada cinco (S-4);
  - la transición (S-2).

  Una fecha única resuelve cada uno en un sentido, sin decir cuál.
- **Cuarenta decisiones propias** en la especificación (D-1 a D-40) y veintitrés de validación en el modelo (V-1 a V-23), cada una con su motivo. Ninguna es la ley. Una fecha sin más las incorpora todas sin nombrar ninguna.
- **Quien recibe un `indeterminado` necesita saber qué decidir.** Un «indeterminado» sin más solo dice que la herramienta no sabe. Atribuido a dimensiones, dice qué pregunta hay que responder, qué pasa con cada respuesta y si con una basta. Por eso la atribución se decidió antes de implementar el cálculo y condicionó sus estructuras: cada combinación de lecturas guarda las dimensiones que consultó, y cada dato de la entrada tiene un identificador para poder citarlo.

**2. La herramienta se publica sobre el borrador de la AMLA, declarándolo, y se actualizará cuando salgan las directrices finales.**

Esperar a las directrices finales dejaría sin herramienta los meses en que las entidades preparan el 10 de julio de 2027. Ignorar el borrador dejaría fuera la única indicación de la AMLA sobre el reinicio del plazo. Se usa así:

- **Nunca como norma.** El borrador solo construye lecturas o apoya una lectura; nunca descarta otra. En la especificación y en [ambiguedades.md](../ambiguedades.md) se cita siempre como borrador.
- **Separado.** El único caso que existe por el borrador, S-3, tiene su propia sección en [ambiguedades.md](../ambiguedades.md). Una tabla lista qué cambiaría en los demás casos donde se cita.
- **Con versión.** [FUENTES.md](../fuentes/FUENTES.md) lo registra como borrador sometido a consulta, sin efecto normativo, con su fecha, su SHA-256 y la fecha esperada de las directrices finales.

## Consecuencias

**La salida es una lista de decisiones que alguien tiene que tomar.** Para cada `indeterminado`, el informe da las dimensiones que lo causan como preguntas, por ejemplo «¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente? (S-3, §2.2)». Para cada respuesta da el estado, las fechas y si con ella el estado queda resuelto o de qué otra dimensión sigue dependiendo (especificación, §10.2; D-36). Hay dos clases de pregunta, y la salida las distingue:

- **De interpretación** (RA, AC, PB, PM, L72…): las responde quien aplica la norma en la entidad, o un criterio del supervisor. La herramienta no elige.
- **De datos** (S-17): la clasificación del cliente no dice algo que la norma necesita. Se responden completando la entrada.

Quien solo quiere una fecha tiene que responder antes esas preguntas. Es el precio de no responderlas en silencio.

**`indeterminado` es frecuente.** En el corpus, siete de nueve casos dan código 1. No es un defecto del cálculo: es la cantidad de preguntas que la norma deja abiertas. El código de salida solo mira el estado (D-38), así que no avisa cuando dos regímenes dan el mismo estado con fechas distintas; eso lo dice el informe (D-40).

**Hay que mantener el repositorio cuando cambie el borrador.** Cuando se publiquen las directrices finales hará falta:

1. Añadirlas a [FUENTES.md](../fuentes/FUENTES.md) como documento distinto, con su versión y su huella, y decidir si el borrador se retira de las fuentes.
2. Revisar la sección 2 de [ambiguedades.md](../ambiguedades.md): S-3 y la tabla de los demás casos. Si las directrices resuelven una dimensión, esa dimensión pasa a ser regla y deja de ser lectura. Si no la resuelven, sigue, con la cita nueva.
3. Cambiar la especificación (§2.2 para RA, y las secciones de cada caso de la tabla), con decisiones nuevas o retiradas. Las decisiones retiradas conservan su número.
4. Cambiar el código: las lecturas en `calculo.py` y las preguntas en `salida.py`.
5. Reescribir a mano los resultados esperados del corpus afectados. Es seguro el caso 05, que existe para mostrar el «can reset». También puede afectar a los demás, si cambian las dimensiones que consultan.

El coste es proporcional a lo que cambie, y está acotado porque el borrador nunca se usó como norma: ninguna lectura existe solo por él salvo las de S-3.

**La frontera entre lo que la herramienta calcula y lo que exige decidir a quien aplica la norma.** La herramienta calcula fechas y estados bajo lecturas declaradas, de forma exacta y reproducible. No decide:
- qué lectura es la correcta;
- cómo clasificar a un cliente: usa la clasificación que hizo la entidad (modelo, §0, principio 4);
- si un hecho es relevante: usa la valoración de la entidad (D-18);
- si una revisión fue suficiente: usa su resultado tal como lo declara la entrada.

Donde uno de estos puntos cambia el estado, la salida lo muestra como decisión, como regímenes que no coinciden o como estado propio. No lo resuelve.

## Referencias

- Ley 10/2010, de 28 de abril, arts. 6 y 7.2 (texto consolidado, última modificación de 21 de marzo de 2026): <https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737>
- Real Decreto 304/2014, de 5 de mayo, arts. 11 y 33 (texto consolidado, última modificación de 24 de abril de 2024): <https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742>
- Reglamento (UE) 2024/1624 (AMLR), arts. 26 y 90 (DO L de 19.6.2024): <http://data.europa.eu/eli/reg/2024/1624/oj>
- AMLA, «Consultation Paper. Draft Guidelines on ongoing monitoring of a business relationship under Article 26(5) of Regulation (EU) 2024/1624», 3 de junio de 2026. **Borrador sometido a consulta, sin efecto normativo**: <https://www.amla.europa.eu/policy/public-consultations/consultation-draft-guidelines-ongoing-monitoring-business-relationship_en>
- Versiones y huellas de los documentos usados: [fuentes/FUENTES.md](../fuentes/FUENTES.md)
