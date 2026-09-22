# Ambigüedades

Casos en que el resultado no está determinado por un texto único. Para cada uno:
- qué dice la norma;
- por qué no determina un comportamiento único;
- qué hace esta implementación;
- cómo se señala en la salida;
- a qué régimen afecta.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las decisiones se citan como en su documento: **D-n** en [`especificacion-calculo.md`](especificacion-calculo.md) y **V-n** en el §9.2 de [`modelo-datos.md`](modelo-datos.md). Los identificadores S-n son estables: no se renumeran ni se reutilizan. Por eso S-3 aparece en la segunda sección y no en la primera.

Hay tres secciones:

- [**Casos que la norma no resuelve**](#1-casos-que-la-norma-no-resuelve) (S-1, S-2 y S-4 a S-16): el texto calla, se contradice o no dice cuál de dos normas rige. S-14 a S-16 aparecieron al implementar la transición.
- [**Casos que vienen del borrador de la AMLA**](#2-casos-que-vienen-del-borrador-de-la-amla) (S-3, y los apoyos del borrador en otros casos). **El borrador no tiene efecto normativo** y las directrices finales se esperan en el cuarto trimestre de 2026. Todo lo de esta sección puede cambiar cuando se publiquen.
- [**Casos que vienen del modelo de datos**](#3-casos-que-vienen-del-modelo-de-datos) (S-17): la norma sí da una respuesta, pero a la entrada le falta el dato que haría falta para aplicarla.

**Cómo se señala en la salida.** La salida (especificación, §10) tiene cinco mecanismos, y cada caso dice cuáles usa:

- **decisiones**: una dimensión de lectura (por ejemplo `RA`, con las lecturas `RA-1` a `RA-3`). Si sus lecturas dan estados distintos, el régimen es `indeterminado`. La salida presenta la dimensión como una pregunta: el estado y las fechas de cada respuesta, si con ella el estado queda resuelto y los datos que la ponen en juego (D-30, D-36);
- **regímenes de transición**: T-1 a T-4 junto a `ley_rd` y `amlr`, con la comparación que señala si no coinciden (D-28, D-40);
- **estados propios**: `revision_pendiente_sin_plazo` y `sin_plazo`, que dicen que falta un plazo en lugar de inventarlo;
- **avisos**: incidencias que no cambian el estado, citadas por su D-n;
- **no se señala**: la implementación aplica una decisión, y la salida no dice que otra lectura cambiaría el resultado.

**Regímenes.** `ley_rd` es la Ley 10/2010 con el RD 304/2014; `amlr`, el AMLR; T-1 a T-4, las lecturas de la transición del 10 de julio de 2027 (especificación, §5). Antes de esa fecha, T-1 a T-4 dan lo mismo que `ley_rd`. Cuando un caso afecta a `ley_rd`, también afecta a los T-n que la aplican.

---

## 1. Casos que la norma no resuelve

<a id="s-1"></a>
### S-1. Fecha de inicio del primer periodo

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.**
- RD, art. 11.2: fija la «periodicidad» de los procesos de revisión, pero no dice desde cuándo cuenta.
- AMLR, art. 26.2: «El período entre las actualizaciones dela información del cliente». Cuenta entre actualizaciones, y no dice qué ocurre antes de la primera.
- Ni la Ley ni el RD ni el AMLR dicen si la diligencia debida inicial cuenta como la primera actualización.

**Por qué no determina un comportamiento único.** Hay al menos tres fechas candidatas, y pueden ser distintas:
- el establecimiento de la relación;
- la conclusión de la diligencia debida inicial. Puede ser posterior al establecimiento: el AMLR, art. 33.1.a, permite comprobar la identidad «después del establecimiento de la relación de negocios [...] pero en ningún caso más de sesenta días después», y el RD, art. 17.1.a, cuando se supere un umbral;
- la primera clasificación de riesgo.

**Qué hace la implementación.** Tres lecturas:
- **IP-1:** `fecha_inicio_relacion`;
- **IP-2:** la primera revisión `inicial` que cuenta. No existe si no hay ninguna (D-11);
- **IP-3:** la primera clasificación.

Solo se usan cuando ninguna revisión marca el calendario. Con RA-1 la revisión inicial ya es el ancla, así que IP solo importa con RA-2 o RA-3 (especificación, §2.1).

**Cómo se señala en la salida.** Decisión `IP` («¿Desde qué fecha cuenta el primer periodo de revisión?»). A menudo cambia el estado solo junto con RA; la salida lo dice («aún depende de RA»). Especificación, ejemplo 6, y el ejemplo de D-30.

<a id="s-2"></a>
### S-2. Clientes existentes el 10 de julio de 2027

**Régimen.** T-1 a T-4, para clientes con la relación viva el día A. También `amlr`, cuando el cliente no está calificado con el AMLR.

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027» (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)).
- El AMLR no tiene ninguna disposición transitoria sobre el seguimiento continuo. Su considerando 76 habla de los clientes existentes solo para justificar la supervisión periódica de «algunas categorías claramente especificadas de clientes ya existentes».
- La Ley consolidada a 21 de marzo de 2026 no contiene ninguna adaptación al AMLR.
- Precedente: cuando entró en vigor, la Ley sí fijó un régimen para los clientes existentes. Disposición transitoria séptima: «los sujetos obligados aplicarán a todos sus clientes existentes las medidas de diligencia debida establecidas en el Capítulo II en un plazo máximo de cinco años, contados a partir de la entrada en vigor de la presente Ley». El AMLR no tiene nada equivalente.

**Por qué no determina un comportamiento único.** Para un cliente con la relación viva el 10 de julio de 2027, ningún texto dice:
- si el periodo en curso termina con el plazo del RD o pasa al del AMLR;
- si el primer periodo del AMLR cuenta desde la última revisión o desde el 10 de julio de 2027;
- si la periodicidad del manual sigue obligando como Derecho nacional;
- qué plazo del AMLR se aplica si la entidad todavía no ha calificado al cliente con él.

**Qué hace la implementación.** Calcula cuatro lecturas como regímenes propios (especificación, §5.2):
- **T-1:** el periodo en curso termina con el RD;
- **T-2:** el AMLR se aplica desde A, contado desde la última revisión;
- **T-3:** el AMLR se aplica desde A, sin superar el vencimiento del RD (D-26);
- **T-4:** coexistencia; rige la fecha más temprana de las dos normas.

Con T-1 y T-3, desde la primera revisión que cuenta con fecha ≥ A se aplica el AMLR (D-27). Si el cliente no está calificado con el AMLR, hay dos lecturas: NC-1, cinco años como «todos los demás clientes», y NC-2, la calificación del RD como sustituta (§4.2).

**Cómo se señala en la salida.** Regímenes de transición: el informe dice «T-1 a T-4 no coinciden: el resultado depende de cómo se resuelva la transición». Además, la decisión `NC` en `amlr` y en los T-n que la usan. Corpus: casos 03 (las cuatro lecturas se separan) y 07. Especificación, ejemplos 8 y 9.

<a id="s-4"></a>
### S-4. Riesgo superior al promedio frente a riesgo elevado con medidas de la sección 4

**Régimen.** `amlr` y los T-n que lo aplican. `ley_rd` no tiene el problema: usa un solo criterio.

**Qué dice la norma.**
- RD, art. 11.2: la periodicidad «para los clientes de riesgo superior al promedio será, como mínimo, anual».
- AMLR, art. 26.2.a: «un año, en el caso de los clientes de riesgo elevado a los que se aplican las medidas de la sección 4 del presente capítulo».
- AMLR, art. 34.1: las medidas reforzadas se aplican «En los casos a que se refieren los artículos 29, 30, 31 y 36 a 46, y en otros casos de mayor riesgo que determinen las entidades obligadas».

**Por qué no determina un comportamiento único.**
- El relativo del art. 26.2.a puede restringir («solo los de riesgo elevado a los que se aplican») o describir («los de riesgo elevado, que son a los que se aplican»).
- Hay clientes con medidas de la sección 4 por disposición y no por valoración de la entidad. Por ejemplo, una persona del medio político (arts. 42 y siguientes) que la entidad no considera de riesgo elevado. El art. 34.1 sugiere que todos esos casos son de mayor riesgo, pero el art. 26.2.a no lo dice.
- Las dos poblaciones, la del RD y la del AMLR, no coinciden.

**Qué hace la implementación.** Recoge las calificaciones por separado (modelo, §4.2) y da dos lecturas del art. 26.2.a:
- **PB-1:** hacen falta los dos elementos;
- **PB-2:** basta uno.

Solo difieren cuando los dos datos no coinciden. **[Decisión propia]** (modelo, §4.2): `medidas_seccion_4_amlr` recoge si las medidas se aplican a la relación, no a una operación aislada examinada por el art. 34.2.

**Cómo se señala en la salida.** Decisión `PB`. Corpus: caso 04; especificación, ejemplo 2.

<a id="s-5"></a>
### S-5. Reclasificación a mitad de un periodo

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.** Ni el RD, art. 11.2, ni el AMLR, art. 26.2, dicen qué ocurre cuando el cliente cambia de clasificación entre dos revisiones.

**Por qué no determina un comportamiento único.** Un cliente revisado hace 18 meses pasa hoy a riesgo superior al promedio. El plazo de un año puede contarse desde la última revisión, y entonces está vencido desde hace seis meses. También puede contarse desde la reclasificación, y entonces vence dentro de un año. Al bajar de clasificación, la duda es la contraria.

**Qué hace la implementación.** Tres lecturas, las mismas que para S-13 (D-12):
- **FR-1:** la clasificación del inicio del periodo;
- **FR-2:** la vigente en la fecha de referencia, contada desde el inicio del periodo;
- **FR-3:** la vigente en la fecha de referencia, contada desde el cambio.

**Cómo se señala en la salida.** Decisión `FR`. Especificación, ejemplo 7.

<a id="s-6"></a>
### S-6. Revisión sin cambios o no completada: revisión frente a actualización

**Régimen.** `amlr` y los T-n que lo aplican, con la revisión sin cambios. Los dos regímenes, con la revisión no completada.

**Qué dice la norma.**
- RD, art. 11.2: la periodicidad es la «de los procesos de revisión documental». Cuenta la revisión.
- AMLR, art. 26.2: «El período entre las actualizaciones». Cuenta la actualización. El art. 26.3 distingue «revisarán y, cuando proceda, actualizarán».
- AMLR, considerando 70: para clientes recurrentes, la diligencia debida puede cumplirse «obteniendo una confirmación del cliente de que la información y los documentos conservados en los registros no han cambiado».

**Por qué no determina un comportamiento único.** Con el AMLR, no está claro si una revisión que confirma que nada ha cambiado es una «actualización». El considerando 70 apunta a que sí, pero habla de la diligencia debida en clientes recurrentes, no del art. 26.2. Tampoco está claro, con ninguno de los dos regímenes, si cuenta una revisión que no se pudo completar.

**Qué hace la implementación.**
- **Revisión sin cambios:** con el RD cuenta. Con el AMLR hay dos lecturas: **AC-1**, cuenta; **AC-2**, no cuenta. Con AC-2, un cliente cuya información no cambia sale vencido aunque se revise a tiempo.
- **Revisión no completada:** no cuenta en ningún régimen (D-8).
- **Revisión sin cambios que atiende un evento:** lo atiende en las dos lecturas, porque el art. 26.3 exige actualizar solo «cuando proceda» (D-19).

**Cómo se señala en la salida.** Decisión `AC`. La revisión no completada **no se señala**: D-8 se aplica sin lectura alternativa. Corpus: casos 02 y 07; especificación, ejemplo 3.

<a id="s-7"></a>
### S-7. Plazo para hacer la revisión por evento

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.**
- RD, art. 33.1.b: la actualización «será, en todo caso, preceptiva». No da plazo.
- AMLR, art. 26.3: «revisarán y, cuando proceda, actualizarán». No da plazo.

**Por qué no determina un comportamiento único.** Sin plazo, la «fecha de la próxima revisión obligatoria» tras un evento puede ser la del evento, la que fije el manual o no existir.

**Qué hace la implementación.** Usa el plazo del manual si lo fija. En las obligaciones de contacto, el límite es el 31 de diciembre del año. Si no hay ninguno de los dos, no inventa un plazo: el evento queda en `revision_pendiente_sin_plazo` (D-20). El «without delay» del borrador de la AMLA no se convierte en plazo (§2 de este documento).

**Cómo se señala en la salida.** Estado propio `revision_pendiente_sin_plazo`, con la fecha desde la que la revisión es exigible. Especificación, ejemplo 5, en su última variante, sin plazo en el manual.

<a id="s-8"></a>
### S-8. Fecha en que el evento activa la revisión

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.** AMLR, art. 26.3.a: «se produzca un cambio». Art. 26.3.c: «entren en conocimiento de un hecho». RD, art. 33.1.b: «cuando se verifique un cambio relevante».

**Por qué no determina un comportamiento único.**
- En la letra a) del AMLR, la obligación nace cuando se produce el cambio, aunque la entidad no lo sepa.
- En el RD, «verificarse» admite los dos sentidos: producirse y comprobarse.
- Cuando un mismo hecho encaja en la letra a) y en la c), las dos fechas compiten.

**Qué hace la implementación.**
- Con el AMLR, la letra decide la fecha: a) la del hecho, b) la de la obligación y c) la del conocimiento (§6.3).
- Con el RD 33.1.b hay dos lecturas: **FV-1**, el hecho; **FV-2**, el conocimiento.
- Si con la letra a) la revisión vence antes de que la entidad conozca el hecho, sale un aviso.

**Cómo se señala en la salida.** Decisión `FV`, y el aviso de la letra a). Especificación, ejemplo 5 (variantes a, b y d).

<a id="s-9"></a>
### S-9. Eventos sin supuesto claro

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.** El RD 33.1.b solo menciona el cambio en la actividad. El AMLR, art. 26.3, distingue el «cambio en las circunstancias pertinentes» (letra a) del «hecho relevante» (letra c). El considerando 69 da ejemplos de lo que la entidad «debe considerar».

**Por qué no determina un comportamiento único.** Un nuevo producto, una operación significativa, una anomalía o un hecho sin tipo pueden ser una circunstancia pertinente, un hecho relevante o ninguna de las dos cosas. Con la Ley 7.2, no está claro si una información de riesgo es un cambio de «las circunstancias del cliente».

**Qué hace la implementación.** Con el AMLR, lecturas **EV-A** (letra a), **EV-C** (letra c) y **EV-N** (ninguna), por tipo de evento (D-7). Con la Ley 7.2, lecturas **LC-1** (no es un cambio de circunstancias) y **LC-2** (sí lo es), para la información de riesgo y el tipo `otro`.

**Cómo se señala en la salida.** Decisiones `EV (tipo)` y `LC (tipo)`. Corpus: caso 06 (LC); especificación, ejemplo 5 (variante c).

<a id="s-10"></a>
### S-10. Alcance del art. 7.2 de la Ley

**Régimen.** `ley_rd`, y los T-n para los eventos anteriores a A.

**Qué dice la norma.** Ley, art. 7.2: la diligencia debida se aplica «no solo [...] a todos los nuevos clientes sino, asimismo, a los clientes existentes». El párrafo segundo enumera los supuestos: nuevos productos, cambio de circunstancias, operación significativa, obligación de contacto sobre titulares reales. La disposición transitoria séptima habla de «todos sus clientes existentes» desde la entrada en vigor de la Ley.

**Por qué no determina un comportamiento único.** «Clientes existentes» puede significar los que ya lo eran en 2010 o cualquier cliente con una relación en curso. Con la primera lectura, la revisión por evento del régimen español se limita al art. 33.1.b del RD.

**Qué hace la implementación.** Dos lecturas:
- **L72-1:** solo los clientes anteriores al 2010-04-30, fecha de entrada en vigor de la Ley;
- **L72-2:** cualquier cliente.

Con clientes anteriores a esa fecha no se consulta: las dos dan lo mismo.

**Cómo se señala en la salida.** Decisión `L72`. Corpus: caso 06; especificación, ejemplo 5.

<a id="s-11"></a>
### S-11. Periodicidad del manual frente a los límites legales

**Régimen.** `ley_rd` y `amlr`.

**Qué dice la norma.**
- RD, art. 11.2: con riesgo superior al promedio, la periodicidad «será, como mínimo, anual». Para el resto, la del manual.
- AMLR, art. 26.2: el período «no será en ningún caso superior» a uno o cinco años.
- AMLR, art. 33.1.b: entre las medidas simplificadas, «reducir la frecuencia de las actualizaciones de la identificación del cliente».

**Por qué no determina un comportamiento único.**
- **Manual más corto que el máximo del AMLR:** no está claro si la revisión «obligatoria» es la del manual o la del máximo legal.
- **Manual más largo:** cabe aplicar el límite o señalar el incumplimiento.
- **Medidas simplificadas:** pueden leerse como una excepción al límite de cinco años o dentro de él.
- **«Como mínimo, anual»:** admite dos lecturas.

**Qué hace la implementación.**
- **Manual más corto que el máximo del AMLR:** dos lecturas. **PM-1**, el máximo legal; **PM-2**, el del manual.
- **Manual más largo que el límite:** se aplica el límite, con aviso. Es D-14 con el RD y D-17 con el AMLR.
- **Medidas simplificadas:** se leen dentro del límite de cinco años (D-17), sin lectura alternativa.
- **«Como mínimo, anual»:** se lee como «al menos una vez al año» (modelo, §3.1; D-14).

**Cómo se señala en la salida.**
- Decisión `PM`.
- Avisos D-14 y D-17.
- La lectura del art. 33.1.b como excepción **no se señala**.

Corpus: casos 03 (D-17), 04 (D-14 y D-17), 07 (PM) y 08 (D-14).

<a id="s-12"></a>
### S-12. Fecha de referencia anterior a la aplicación del AMLR, y clubes de fútbol

**Régimen.** `amlr`.

**Qué dice la norma.** AMLR, art. 90: aplicable desde el 10 de julio de 2027, o desde el 10 de julio de 2029 para agentes de fútbol y clubes de fútbol profesional. El art. 3, punto 3, letra o), limita la condición de entidad obligada de los clubes a ciertas operaciones.

**Por qué no determina un comportamiento único.** Con una fecha de referencia anterior a la aplicación, calcular con el AMLR puede ser un error, una simulación o el cálculo de la primera fecha obligatoria. En los clubes, no está claro si el seguimiento continuo alcanza a relaciones que solo en parte tienen que ver con esas operaciones.

**Qué hace la implementación.**
- **Fecha anterior a la aplicación:** calcula el AMLR sobre toda la historia del cliente, como comparación, con aviso (D-24).
- **Clubes de fútbol:** aplica la fecha de 2029 a todo el cliente, sin distinguir operaciones. El modelo no recoge cuáles están en el ámbito de la letra o) (modelo, §2.1).

**Cómo se señala en la salida.** Aviso D-24. El ámbito de los clubes **no se señala**. Corpus: caso 08 (D-24).

<a id="s-13"></a>
### S-13. Versión del manual aplicable

**Régimen.** `ley_rd`; con el AMLR, solo cuando se aplica la lectura PM-2 (S-11).

**Qué dice la norma.** RD, art. 33.2: el manual se actualiza periódicamente. Ningún texto dice qué versión rige un periodo que empezó con otra.

**Por qué no determina un comportamiento único.** Si el manual pasa de 36 a 24 meses, un cliente revisado antes del cambio puede tener la próxima revisión a los 36 o a los 24 meses. Con la segunda lectura, puede estar vencido el mismo día del cambio.

**Qué hace la implementación.** Las lecturas FR-1 a FR-3 de S-5, que tratan juntos el cambio de clasificación y el de manual (D-12). Si no hay versión vigente en una fecha, se usa la primera (D-13).

**Cómo se señala en la salida.** Decisión `FR`.

<a id="s-14"></a>
### S-14. Evento que ninguna norma activa en su propio periodo

**Régimen.** T-1, T-2 y T-3.

**Qué dice la norma.** Ninguna regla de transición. D-25 juzga cada evento con la norma aplicable en su fecha de activación.

**Por qué no determina un comportamiento único.** Un cambio de actividad ocurrido antes de A y conocido después: con el RD, leído como FV-2, se activa después de A, cuando el RD ya no rige. Con el AMLR, por la letra a), se activa antes de A, cuando el AMLR aún no rige. Ninguna norma lo activa en su propio periodo.

**Qué hace la implementación.** Tres lecturas (D-31):
- **TE-1:** el RD, en su fecha;
- **TE-2:** el AMLR, con la activación en A;
- **TE-3:** ninguna norma.

La primera versión del cálculo aplicaba TE-3 sin decirlo.

**Cómo se señala en la salida.** Decisión `TE`, con aviso D-31. Test: `test_evento_que_ninguna_norma_activa_en_su_periodo`.

<a id="s-15"></a>
### S-15. Evento que las dos normas activan en su propio periodo

**Régimen.** T-1, T-2 y T-3.

**Qué dice la norma.** Ninguna regla de transición. D-25 no dice qué norma prevalece si las dos se cumplen.

**Por qué no determina un comportamiento único.** Una información de riesgo ocurrida antes de A y conocida después: la Ley 7.2 la activa en la fecha del hecho (antes de A), y la letra c) del AMLR en la del conocimiento (después). Cada norma la activa dentro de su periodo, con fechas límite distintas.

**Qué hace la implementación.** Dos lecturas (D-32):
- **TD-1:** el RD;
- **TD-2:** el AMLR.

La primera versión del cálculo aplicaba TD-1 sin decirlo, porque comprobaba primero el RD.

**Cómo se señala en la salida.** Decisión `TD`, con aviso D-32. Corpus: caso 06.

<a id="s-16"></a>
### S-16. Qué norma decide si una revisión posterior a A cierra el periodo del RD

**Régimen.** T-1 y T-3.

**Qué dice la norma.** Ninguna regla de transición. D-27 pasa al AMLR con «la primera revisión que cuenta con fecha ≥ A», sin decir con qué norma se decide si cuenta. Y las dos normas no cuentan las mismas revisiones (S-6).

**Por qué no determina un comportamiento único.** Una revisión sin cambios posterior a A, con la lectura AC-2: el AMLR no la cuenta y el RD sí. Si la juzga el AMLR, no cuenta para nadie: el cliente sigue en el periodo del RD anterior, que puede estar vencido. Si la juzga el RD, cierra ese periodo.

**Qué hace la implementación.** Dos lecturas (D-33):
- **TR-1:** decide el AMLR;
- **TR-2:** decide el RD, mientras dura su periodo.

La primera versión del cálculo aplicaba TR-1 sin decirlo.

**Cómo se señala en la salida.** Decisión `TR`, con aviso D-33. Corpus: caso 07.

---

## 2. Casos que vienen del borrador de la AMLA

> **Borrador sin efecto normativo.** «Consultation Paper. Draft Guidelines on ongoing monitoring of a business relationship under Article 26(5) of Regulation (EU) 2024/1624», de 3 de junio de 2026. La consulta se cerró el 3 de septiembre de 2026, y la AMLA anuncia las directrices finales para el cuarto trimestre de 2026. Lo que sigue depende de su redacción y puede cambiar. Cuando se publiquen, hay que revisar esta sección, la especificación y el corpus ([ADR 0001](adr/0001-calcular-seis-regimenes-y-atribuir.md)).

<a id="s-3"></a>
### S-3. Revisión anticipada: «can reset»

**Régimen.** `ley_rd` y `amlr`. El borrador interpreta el AMLR; con el RD la pregunta es la misma y tampoco hay texto.

**Qué dice la norma.**
- AMLR, art. 26.2: fija el período máximo «entre las actualizaciones». No dice si una actualización hecha antes de tiempo inicia un período nuevo.
- Borrador AMLA, ap. 2: «If a review is carried out earlier than scheduled, this can reset the timeline for the next required update» [si una revisión se hace antes de lo previsto, puede reiniciar el plazo de la siguiente actualización].
- RD: nada.

**Por qué no determina un comportamiento único.** El borrador dice «puede», no «reinicia». Admite tres lecturas: siempre reinicia, nunca reinicia o lo decide la entidad. Además, no tiene efecto normativo.

**Qué hace la implementación.** Tres lecturas (especificación, §2.2):
- **RA-1:** siempre reinicia;
- **RA-2:** nunca; solo las revisiones periódicas marcan el calendario (D-9);
- **RA-3:** lo decide el manual, según `revision_anticipada_reinicia_plazo`. Con el manual a `null`, cada revisión se calcula de las dos maneras (D-10).

Que el manual se pronuncie no elimina RA-1 ni RA-2, porque el manual no decide si la norma lo permite.

**Cómo se señala en la salida.** Decisión `RA` («¿Una revisión hecha antes de tiempo reinicia el plazo de la siguiente?»). Corpus: caso 05; especificación, ejemplo 4.

**Qué cambiaría con las directrices finales.**
- Si dicen «reinicia», o «no reinicia», sin margen: RA-1 o RA-2 pasaría a ser la regla y RA desaparecería como dimensión.
- Si mantienen «can»: las tres lecturas siguen.

### Otros casos en que se cita el borrador

En estos casos el problema está en la norma, y el borrador solo aporta un argumento o un ejemplo. Ninguna lectura existe solo por él, y ninguna se descarta por él.

| Caso | Qué cita del borrador | Qué cambiaría con las directrices finales |
|---|---|---|
| [S-1](#s-1) | Ap. 21: la información recogida «at customer onboarding and during the most recent customer review». | Si fijan desde cuándo cuenta el primer periodo, IP se reduciría a una lectura. |
| [S-5](#s-5) | Ap. 3: al revisar se valora si hay que actualizar «the customer risk classification». | Si dicen qué pasa con el plazo en curso al reclasificar, FR se reduciría. |
| [S-6](#s-6) | Aps. 30 a 32: suspensión de operaciones si el cliente no responde; apoya D-8. | Si dicen que una revisión sin cambios cuenta como actualización, AC-2 desaparecería. |
| [S-7](#s-7) | Ap. 20.d, «without delay»; ap. 25, «without undue delay». No se convierten en plazo (D-20). | Si fijan un plazo en días, sería el plazo de la revisión por evento en lugar de `revision_pendiente_sin_plazo`. |
| [S-9](#s-9) | Ap. 27: lista de eventos que «may trigger a review», sin letra del art. 26.3. | Si asignan una letra a cada tipo, EV desaparecería para esos tipos. |
| [S-11](#s-11) | Ap. 2: las entidades deciden «whether more frequent updates are needed»; apoya PM-2. | Si dicen que el plazo del manual es el obligatorio, o que no lo es, PM se reduciría a una lectura. |

---

## 3. Casos que vienen del modelo de datos

<a id="s-17"></a>
### S-17. Calificación de riesgo sin un dato

**Régimen.** `ley_rd` si falta `superior_al_promedio`; `amlr` si falta `riesgo_elevado_amlr` o `medidas_seccion_4_amlr`.

**Qué dice la norma.** La norma sí responde: el plazo depende de la calificación (RD, art. 11.2; AMLR, art. 26.2). Pero la entrada admite `null` en esas calificaciones, que significa que la entidad no la hizo (modelo, §4.2), y el cálculo no la deduce de otros datos (modelo, §0, principio 4).

**Por qué no determina un comportamiento único.** Sin el dato, la regla no se puede aplicar. No es una pregunta de interpretación: se resuelve completando la entrada.

**Qué hace la implementación.** Evalúa las dos posibilidades (D-15):
- `SP (fecha)` con el RD;
- `riesgo_elevado_amlr desconocido (fecha)` o `medidas_seccion_4_amlr desconocido (fecha)` con el AMLR.

Si faltan los dos datos del AMLR, se aplican las lecturas NC de S-2.

**Cómo se señala en la salida.** Decisión con una pregunta sobre el dato, no sobre la norma: «La clasificación del 2020-01-10 no dice si el riesgo es superior al promedio: ¿lo es?» (D-36). Corpus: caso 08.
