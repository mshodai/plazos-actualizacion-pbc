# Especificación del cálculo

Este documento explica cómo se calcula, en una fecha de referencia, **la fecha de la próxima revisión obligatoria de la información de un cliente y su estado**. Se calcula con la Ley 10/2010 y su Reglamento, con el AMLR y con cada lectura de la transición entre ambos. La entrada es el JSON de [`modelo-datos.md`](modelo-datos.md), que solo recoge hechos y no lleva régimen. No contiene código.

Siglas y fuentes: las de [`modelo-datos.md`](modelo-datos.md) (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)). Las referencias «S-n» remiten a los casos que la norma no resuelve, al final de [`modelo-datos.md`](modelo-datos.md#casos-que-la-norma-no-resuelve). «Modelo, §n» remite a una sección de ese documento.

Convenciones:

- Las citas van entre comillas «» y son literales. Las del borrador AMLA están en inglés, el único idioma en que se publicó, y llevan traducción propia entre corchetes.
- **[D-n]** marca una decisión de este proyecto que no sale de los textos. Todas están numeradas y reunidas en el [§11](#11-índice-de-decisiones). Los números son estables: una decisión retirada conserva su número y no se reutiliza.
- **Lectura** es una interpretación posible de un texto que no se resuelve. Cada lectura tiene un identificador (por ejemplo `RA-2`). Cuando hay varias, el cálculo las devuelve todas con su resultado (§1.5) y no elige. Si dan estados distintos, el estado es `indeterminado`.
- El borrador AMLA **no tiene efecto normativo**. Aquí solo sirve para construir lecturas del AMLR, nunca para descartar otras.

---

## 1. Marco común

### 1.1. El régimen es un parámetro del cálculo

**[D-4]** El cálculo recibe la entrada y un **régimen**. Una ejecución completa calcula siempre los seis regímenes sobre la misma entrada y los devuelve juntos. Ninguno es el principal ni el resultado por defecto. Es la misma decisión que D-14 en `plazos-conservacion-pbc`.

| Régimen | Qué calcula | Sección |
|---|---|---|
| `ley_rd` | La Ley y el RD, aplicados solos, en cualquier fecha. | §3 |
| `amlr` | El AMLR, aplicado solo, en cualquier fecha y a toda la historia del cliente. | §4 |
| `T-1` a `T-4` | Lo que se aplica en `fecha_referencia` según cada lectura de la transición del 10 de julio de 2027. | §5 |

Los dos primeros sirven para comparar las normas tal como están escritas. Los cuatro últimos sirven para saber qué se aplica en una fecha concreta según cómo se resuelva la transición, que ningún texto resuelve (S-2).

En todo el documento:

- **R** es `fecha_referencia`.
- **A** es la fecha de aplicación del AMLR (art. 90): 2027-07-10, o 2029-07-10 si `sujeto.actividad` es `agente_de_futbol` o `club_de_futbol_profesional`.

### 1.2. Qué se calcula

Para cada régimen y lectura, el cálculo obtiene dos **componentes**:

- **Periódico**: la fecha límite de la próxima revisión periódica (RD 11.2; AMLR 26.2).
- **Por evento**: por cada evento que activa una revisión y no está atendido, la fecha en que se activa y, si la hay, su fecha límite (RD 33.1.b; Ley 7.2; AMLR 26.3).

Con ellos se forman el estado de la lectura y la **fecha de la próxima revisión obligatoria** (§1.4).

### 1.3. Cómputo de fechas

Ninguna fuente dice cómo se cuentan los meses ni los días. Se usan estas reglas:

- **[D-1]** «N meses desde F» vence en la fecha V que tiene el mismo día que F, N meses después. Si ese día no existe en el mes de V, V es el último día de ese mes. Ejemplos: 2027-08-31 + 6 meses = 2028-02-29; 2024-02-29 + 12 meses = 2025-02-28. Los años del RD y del AMLR («anual», «un año», «cinco años») se cuentan como 12 y 60 meses.
- **[D-2]** El día V todavía está en plazo: una revisión hecha ese día es puntual. La revisión está `vencida` desde V + 1 día.
- **[D-3]** «N días desde F» (el plazo del manual para las revisiones por evento) vence en F + N días naturales, y ese día todavía está en plazo, igual que en [D-2]. Ejemplo: 2028-04-01 + 30 días = 2028-05-01.

### 1.4. Estados

| Estado | Significado |
|---|---|
| `en_plazo` | Hay una fecha límite y R no la ha pasado. |
| `vencida` | Alguna fecha límite es anterior a R y la revisión no se ha hecho. |
| `revision_pendiente_sin_plazo` | Un evento ha activado una revisión que no se ha hecho, y ni la norma ni el manual le ponen plazo (§6.4). No es `en_plazo`, porque no hay plazo que cumplir. Tampoco es `vencida`, porque no hay plazo que haya pasado. |
| `sin_plazo` | La norma del régimen no da ninguna periodicidad para el cliente. Solo puede ocurrir con la Ley y el RD, cuando el manual no fija periodicidad para el nivel del cliente ([D-16]). |
| `relacion_terminada` | La relación terminó en R o antes ([D-22]). |
| `indeterminado` | Las lecturas del régimen dan estados distintos ([D-6]). |

**[D-23]** Si en una lectura concurren varios componentes, el estado de la lectura se elige por este orden de prioridad: `relacion_terminada`, `vencida`, `revision_pendiente_sin_plazo`, `sin_plazo`, `en_plazo`. Por ejemplo, una revisión periódica en plazo con un evento vencido da `vencida`. El resultado conserva el estado de cada componente, así que el orden solo decide qué se muestra como estado de la lectura.

**[D-29]** La **fecha de la próxima revisión obligatoria** de una lectura es la más temprana de sus fechas límite sin cumplir: la periódica y las de los eventos pendientes que tienen plazo. Si esa fecha es anterior a R, la revisión está vencida. Los eventos pendientes sin plazo no tienen fecha límite: se dan aparte, con la fecha desde la que la revisión es exigible.

### 1.5. Forma del resultado y lecturas

**[D-5]** El resultado tiene una entrada por régimen. Cada entrada incluye:

- `estado`: uno de los de §1.4.
- `fecha_proxima_revision`: la de [D-29] si todas las lecturas coinciden, o la lista de fechas distintas con las lecturas que dan cada una.
- `componentes`: el periódico y los eventos, con sus fechas y su estado.
- `lecturas`: una entrada por combinación de lecturas que da un resultado distinto. Cada una lleva sus identificadores, sus fechas, su estado y las citas en que se basa.
- `avisos`: incidencias que no impiden el cálculo, como una periodicidad del manual recortada al límite legal o el AMLR calculado antes de A.

**[D-6]** Si todas las combinaciones de lecturas dan el mismo estado en R, `estado` toma ese valor, aunque las fechas sean distintas. Si difieren, `estado` es `indeterminado`. Las lecturas se devuelven siempre.

**[D-7]** Las lecturas de dimensiones distintas se combinan todas con todas. Solo se devuelven las combinaciones que dan un resultado distinto. En los eventos, una lectura se aplica por **tipo** de evento: todos los eventos del mismo tipo se leen igual dentro de una combinación. La alternativa, leer cada evento por separado, produciría combinaciones incoherentes. Por ejemplo, dos operaciones significativas tratadas una como letra a) y otra como letra c) del art. 26.3.

Las dimensiones de lectura son estas:

| Dimensión | Lecturas | Régimen | Sección |
|---|---|---|---|
| Inicio del primer periodo (S-1) | IP-1, IP-2, IP-3 | ambos | §2.1 |
| Revisión anticipada (S-3) | RA-1, RA-2, RA-3 | ambos | §2.2 |
| Revisión sin cambios (S-6) | AC-1, AC-2 | AMLR | §2.3 |
| Clasificación o manual que cambian a mitad de periodo (S-5, S-13) | FR-1, FR-2, FR-3 | ambos | §2.4 |
| Riesgo superior al promedio sin calificar | SP-1, SP-2 | Ley y RD | §3.2 |
| Elementos del art. 26.2.a (S-4) | PB-1, PB-2 | AMLR | §4.2 |
| Cliente sin calificación con el AMLR (S-2, S-4) | NC-1, NC-2 | AMLR | §4.2 |
| Manual más corto que el límite legal (S-11) | PM-1, PM-2 | AMLR | §4.2 |
| Fecha de «se verifique» en el RD 33.1.b (S-8) | FV-1, FV-2 | Ley y RD | §6.2 |
| Alcance de la Ley 7.2 (S-10) | L72-1, L72-2 | Ley y RD | §6.2 |
| Información de riesgo u `otro` como «cambio de circunstancias» en la Ley 7.2 (S-9) | LC-1, LC-2 | Ley y RD | §6.2 |
| Letra del art. 26.3 en los eventos sin supuesto claro (S-9) | EV-A, EV-C, EV-N | AMLR | §6.3 |
| Transición (S-2) | T-1 a T-4 | transición | §5 |

---

## 2. Piezas comunes a los dos regímenes

### 2.1. Inicio del primer periodo (S-1)

**Los textos.** RD, art. 11.2: el manual determina «la periodicidad de los procesos de revisión documental». AMLR, art. 26.2: «El período entre las actualizaciones dela información del cliente [...] no será en ningún caso superior a». Ninguno dice desde cuándo cuenta el primer periodo.

Se usa cuando no hay ninguna revisión que marque el calendario según la lectura de §2.2:

| Lectura | Inicio del primer periodo | Apoyo |
|---|---|---|
| **IP-1** | `fecha_inicio_relacion` | El seguimiento continuo es de «la relación de negocios» (Ley, art. 6; AMLR, art. 26.1): empieza con ella. |
| **IP-2** | `fecha` de la primera revisión `inicial` con resultado que cuente (§2.3) | La diligencia debida inicial es la primera vez que la información está completa y actualizada. El AMLR, art. 33.1.a, permite comprobar la identidad hasta «sesenta días después del establecimiento de la relación». |
| **IP-3** | `fecha` de la primera clasificación | El plazo depende del riesgo (RD 11.2: «en función del riesgo»; AMLR 26.2: «dependerá del riesgo»), y sin clasificación no hay plazo. |

**[D-11]** Si no hay ninguna revisión `inicial` que cuente, IP-2 no existe y se emite un aviso. IP-1 existe siempre, porque `fecha_inicio_relacion` es obligatoria, e IP-3 también, porque la lista de clasificaciones no puede estar vacía (modelo, V-7).

### 2.2. Revisión anticipada: «can reset» (S-3)

**Los textos.**
- AMLR, art. 26.2: el máximo se mide «entre las actualizaciones».
- RD, art. 11.2: periodicidad «de los procesos de revisión documental».
- Borrador AMLA, ap. 2: «If a review is carried out earlier than scheduled, this can reset the timeline for the next required update» [si una revisión se hace antes de lo previsto, puede reiniciar el plazo de la siguiente actualización].

El borrador dice «puede», no «reinicia». Hay tres lecturas, que definen qué revisiones marcan el calendario periódico. El **ancla** es la revisión más reciente, con fecha ≤ R, de entre las que marcan el calendario. Si no hay ninguna, el ancla es el inicio del primer periodo (§2.1).

| Lectura | Qué revisiones marcan el calendario | Próxima revisión periódica |
|---|---|---|
| **RA-1. Siempre reinicia** | Todas las que cuentan (§2.3), de cualquier tipo: `inicial`, `periodica` y `por_evento`. | ancla + P |
| **RA-2. Nunca reinicia** | Solo las de tipo `periodica` que cuentan. Las `inicial` y `por_evento` no mueven el calendario. | ancla + P, con el inicio del primer periodo (IP-n) como ancla mientras no haya ninguna periódica |
| **RA-3. Lo decide la entidad** | Según `revision_anticipada_reinicia_plazo` de la versión del manual vigente en la fecha de cada revisión `inicial` o `por_evento`: `true` como en RA-1; `false` como en RA-2. | ancla + P |

P es la periodicidad aplicable (§3.2 y §4.2).

- **[D-9]** RA-2 se construye como «solo las revisiones periódicas marcan el calendario», y no como «la siguiente fecha se cuenta desde la prevista y no desde la revisión» (fecha prevista + P). La segunda versión permitiría que pasaran más de P meses entre dos actualizaciones, lo que el AMLR prohíbe («no será en ningún caso superior»). La primera nunca da una fecha posterior a RA-1, porque la última periódica no es posterior a la última revisión de cualquier tipo.
- **[D-10]** En RA-3, si el campo es `null` en la versión que rige una revisión, esa revisión se calcula de las dos maneras, como en RA-1 y como en RA-2. La versión que rige es la vigente en la fecha de la revisión, porque es entonces cuando la entidad decide si reinicia el plazo.
- RA-1 y RA-2 existen siempre, aunque el manual diga `true` o `false`: el manual solo decide el resultado de RA-3. Por eso una revisión anticipada da `indeterminado` en cuanto RA-1 y RA-2 difieren (ejemplo 4). Así debe ser: que el manual diga «reinicia» no resuelve si la norma lo permite.
- El borrador AMLA interpreta el AMLR, no el RD. Las tres lecturas se aplican también con el RD porque la pregunta es la misma y el RD tampoco la contesta. Con el RD, RA-3 tiene además un apoyo propio: el RD deja la periodicidad al manual (art. 11.2).

### 2.3. Revisión frente a actualización (S-6)

**Los textos.**
- RD, art. 11.2: cuenta «procesos de revisión documental», que sirven para asegurar que la información «se mantenga[n] actualizados y se encuentren vigentes».
- AMLR, art. 26.2: cuenta «actualizaciones». El art. 26.3 distingue las dos cosas: «revisarán y, cuando proceda, actualizarán».
- AMLR, considerando 70: la diligencia debida puede cumplirse «obteniendo una confirmación del cliente de que la información y los documentos conservados en los registros no han cambiado».

Qué revisiones **cuentan** para el calendario periódico, según `resultado`:

| `resultado` | Ley y RD | AMLR, AC-1 | AMLR, AC-2 |
|---|---|---|---|
| `actualizada` | cuenta | cuenta | cuenta |
| `sin_cambios` | **cuenta** | cuenta | **no cuenta** |
| `no_completada` | no cuenta ([D-8]) | no cuenta ([D-8]) | no cuenta ([D-8]) |

- **Ley y RD.** Una revisión sin cambios es un «proceso de revisión documental» completo. Cuenta sin lectura alternativa: el art. 11.2 fija la periodicidad de la revisión, no de los cambios.
- **AMLR, AC-1.** Una revisión que confirma la información es una actualización: la información queda comprobada a esa fecha (considerando 70).
- **AMLR, AC-2.** Solo es actualización una revisión que cambia algo, por la letra del art. 26.2 y la distinción del art. 26.3. Con esta lectura, un cliente cuya información no cambia nunca estaría siempre vencido. El cálculo no descarta la lectura por ese resultado: lo muestra (ejemplo 3).
- **[D-8]** Una revisión `no_completada` no cuenta en ningún régimen. Con el RD, la revisión no alcanzó su objeto: que la información «se mantenga[n] actualizados». Con el AMLR, no hubo actualización. Además, los dos textos prevén qué pasa si la entidad no consigue la información: terminar la relación (Ley, art. 7.3; AMLR, art. 21.1). El borrador AMLA (aps. 30 a 32) solo admite suspender las operaciones mientras tanto. La alternativa, contarla con el RD como «proceso de revisión», se descartó porque haría cumplido el plazo sin que la información estuviera al día.
- **Revisiones por evento.** Una revisión `sin_cambios` sí **atiende** el evento en los dos regímenes y en las dos lecturas AC, porque el art. 26.3 exige revisar y actualizar solo «cuando proceda» ([D-19]). AC-2 solo decide si esa revisión reinicia además el calendario del art. 26.2.

### 2.4. Clasificación o manual que cambian a mitad de periodo (S-5, S-13)

**Los textos.** Ni el RD ni el AMLR dicen qué clasificación ni qué versión del manual rigen un periodo cuando cambian entre el ancla y R.

**[D-12]** Una sola dimensión de lecturas resuelve las dos preguntas: qué clasificación y qué versión del manual rigen. Es la misma cuestión, qué regla gobierna un periodo en curso cuando cambia lo que la determina, y tratarlas por separado daría combinaciones mixtas sin apoyo en ningún texto.

| Lectura | Clasificación y manual | Desde |
|---|---|---|
| **FR-1. Los del inicio del periodo** | Los vigentes en la fecha del ancla. | ancla |
| **FR-2. Los vigentes en R, desde el ancla** | Los vigentes en R. | ancla |
| **FR-3. Los vigentes en R, desde el cambio** | Los vigentes en R. | La fecha más reciente, posterior al ancla, en que cambió la periodicidad P que resulta. Si P no cambió, el ancla. |

- «Vigente en la fecha F» es la clasificación con la `fecha` más reciente ≤ F y la versión del manual con el `vigente_desde` más reciente ≤ F.
- **[D-13]** En FR-1, si no hay clasificación vigente en la fecha del ancla, se usa la primera clasificación. Lo mismo con el manual. Ocurre cuando la entidad clasificó después del ancla, por ejemplo con IP-1 y una clasificación posterior al inicio de la relación.
- FR-3 solo mira los cambios de P, no los de los datos. Por ejemplo, cuando la entidad añade la calificación con el AMLR sin que cambie el plazo, FR-3 no reinicia nada.

---

## 3. Régimen de la Ley 10/2010 y el RD 304/2014

### 3.1. Qué hecho inicia el cómputo

El ancla de §2.2: la revisión más reciente que marca el calendario según RA-n, contando las revisiones de §2.3. Si no hay ninguna, el inicio del primer periodo según IP-n (§2.1).

### 3.2. Qué plazo aplica según la clasificación

**Los textos.**
- RD, art. 11.2: «El manual a que se refiere el artículo 33 determinará, en función del riesgo, la periodicidad de los procesos de revisión documental que para los clientes de riesgo superior al promedio será, como mínimo, anual».
- RD, art. 33.1.b: el manual incluirá «Un procedimiento estructurado de diligencia debida que incluirá la periódica actualización de la documentación e información exigibles».

Con la clasificación C y la versión del manual M que rigen (§2.4), sea Pm la periodicidad de M para `C.nivel_entidad`:

| `C.superior_al_promedio` | P | Base |
|---|---|---|
| `true` | el menor de Pm y 12 meses. Sin Pm: 12 meses. | RD 11.2: «como mínimo, anual» |
| `false` | Pm. Sin Pm: `sin_plazo`. | RD 11.2: lo «determinará» el manual |
| `null` | lecturas **SP-1** (como `true`) y **SP-2** (como `false`) | [D-15] |

- **[D-14]** Con riesgo superior al promedio, un manual que fija más de 12 meses se recorta a 12 y se emite un aviso de que el manual incumple el art. 11.2. Sin periodicidad en el manual para ese nivel, se aplican 12 meses: el mínimo del RD rige aunque el manual calle. «Como mínimo, anual» se lee como «al menos una vez al año» (modelo, S-11).
- **[D-15]** Un `superior_al_promedio` a `null` significa que la entidad no hizo esa calificación. El cálculo no la deduce de `nivel_entidad`, porque sería decidir por la entidad (modelo, §0, principio 4). Evalúa las dos posibilidades.
- **[D-16]** Si el cliente no es de riesgo superior al promedio y el manual no fija periodicidad para su nivel, el componente periódico es `sin_plazo`. Ningún texto da un plazo supletorio.

**Fecha límite periódica** = ancla + P ([D-1]). La revisión periódica está `en_plazo` si esa fecha ≥ R, y `vencida` si es anterior.

### 3.3. Cómo afectan los eventos

La base es el art. 33.1.b del RD, y según L72-n también el art. 7.2 de la Ley. Detalle en §6.

### 3.4. Qué datos no usa

`riesgo_elevado_amlr`, `medidas_seccion_4_amlr`, `obligacion_contacto_dac` y `sujeto.actividad`. El RD no tiene nada equivalente a las dos primeras, y la Ley no incluye la Directiva 2011/16/UE en el art. 7.2.

---

## 4. Régimen del AMLR

### 4.1. Qué hecho inicia el cómputo

El mismo ancla de §2.2, pero contando las revisiones según AC-n (§2.3).

**[D-24]** El régimen `amlr` se calcula también cuando R es anterior a A, y sobre toda la historia del cliente, porque comparar las normas es uno de los objetivos del proyecto. El resultado lleva el aviso de que el AMLR no es aplicable en esa fecha. Base: art. 90, «Será aplicable a partir del 10 de julio de 2027». Es la misma decisión que D-20 en `plazos-conservacion-pbc`.

### 4.2. Qué plazo aplica según la clasificación

**El texto.** Art. 26.2, párrafo segundo: «El período entre las actualizaciones dela información del cliente conforme al párrafo primero dependerá del riesgo que plantea la relación de negocios y no será en ningún caso superior a: a) un año, en el caso de los clientes de riesgo elevado a los que se aplican las medidas de la sección 4 del presente capítulo; b) cinco años, en el caso de todos los demás clientes».

**Límite legal L.** Con la clasificación C que rige (§2.4), y con E = `riesgo_elevado_amlr` y S4 = `medidas_seccion_4_amlr`:

| E | S4 | PB-1: hacen falta los dos elementos | PB-2: basta uno |
|---|---|---|---|
| `true` | `true` | 12 | 12 |
| `true` | `false` | 60 | 12 |
| `false` | `true` | 60 | 12 |
| `false` | `false` | 60 | 60 |

- **PB-1** lee «de riesgo elevado a los que se aplican las medidas de la sección 4» como una doble condición: el relativo restringe.
- **PB-2** lee que cada elemento basta. Un cliente de riesgo elevado es de los que deben recibir medidas de la sección 4 (art. 20.2, párrafo segundo: «aplicarán medidas reforzadas de diligencia debida conforme a la sección 4»). Un cliente con medidas de la sección 4 es de mayor riesgo (art. 34.1: «y en otros casos de mayor riesgo», que presenta los casos enumerados como de mayor riesgo).
- Las dos lecturas solo difieren cuando E y S4 no coinciden (S-4).

**Datos sin calificar ([D-15]).**
- Si **uno** de los dos es `null`, se evalúa con `true` y con `false`.
- Si **los dos** son `null`, la entidad no ha calificado al cliente con el AMLR. Es el caso típico del cliente existente el día A (S-2). Hay dos lecturas:
  - **NC-1.** «Todos los demás clientes» (art. 26.2.b) es la categoría residual: sin determinación de riesgo elevado, 60 meses.
  - **NC-2.** Se usa la calificación del RD como sustituta: 12 meses si `superior_al_promedio = true` y 60 si es `false`. Si también es `null`, las dos.

**Periodicidad P.** El límite legal L frente al manual (S-11):

| Lectura | P |
|---|---|
| **PM-1. Solo el límite legal** | L. La periodicidad del manual es un procedimiento interno, no el plazo del art. 26.2. |
| **PM-2. El manual si es más corto** | el menor de L y Pm. Sin Pm: L. El art. 26.2 dice que el período «dependerá del riesgo», y el borrador AMLA, ap. 2, pide decidir «whether more frequent updates are needed» [si hacen falta actualizaciones más frecuentes]. |

- **[D-17]** Un manual con una periodicidad mayor que L no alarga el plazo en ninguna lectura. Se aplica L con un aviso, porque el período «no será en ningún caso superior». Tampoco lo alargan las medidas simplificadas del art. 33.1.b («reducir la frecuencia de las actualizaciones»): se leen dentro del límite, por el «en ningún caso». Es una decisión y no una lectura, y el aviso lo recuerda. La lectura contraria, que el art. 33.1.b sea una excepción al art. 26.2.b, no se calcula (modelo, S-11).

**Fecha límite periódica** = ancla + P. Estados como en §3.2.

### 4.3. Cómo afectan los eventos

La base es el art. 26.3, letras a), b) y c). Detalle en §6.

### 4.4. Qué datos no usa

`superior_al_promedio`, salvo en NC-2, y la periodicidad del manual, salvo en PM-2. No usa las lecturas L72-n, LC-n ni FV-n: el art. 26.3 no remite a la Ley.

---

## 5. Transición: clientes existentes el 10 de julio de 2027 (S-2)

### 5.1. Lo que dicen los textos

- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029».
- El AMLR no tiene ninguna disposición transitoria sobre el seguimiento continuo. El considerando 76 habla de los clientes existentes solo para justificar la supervisión periódica de «algunas categorías claramente especificadas de clientes ya existentes».
- La Ley consolidada a 21 de marzo de 2026 no contiene ninguna adaptación al AMLR.
- La Ley, en su día, sí fijó un régimen para los suyos. Disposición transitoria séptima: «los sujetos obligados aplicarán a todos sus clientes existentes las medidas de diligencia debida establecidas en el Capítulo II en un plazo máximo de cinco años, contados a partir de la entrada en vigor de la presente Ley».

**Lo que ningún texto dice:** qué plazo rige, el día A, para un cliente cuyo periodo de revisión empezó con el RD y sigue en curso. Tampoco si los plazos del manual siguen obligando como Derecho nacional después de A.

**Cliente existente** es el que tiene `fecha_inicio_relacion` < A y la relación viva el día A (`fecha_terminacion_relacion` nula o ≥ A).

### 5.2. Lecturas

| Lectura | Idea | Cliente existente, desde A | Cliente nuevo (inicio ≥ A) |
|---|---|---|---|
| **T-1. El periodo en curso termina con el RD** | Un periodo se rige por la norma con que empezó. | El periodo en curso el día A (ancla < A, calculado con `ley_rd`) vence en la fecha del RD. Desde la primera revisión que cuenta con fecha ≥ A, AMLR. Si ese periodo ya estaba vencido el día A, sigue `vencida` hasta la revisión. | AMLR (§4). |
| **T-2. AMLR inmediato desde la última revisión** | El AMLR se aplica desde A a toda la relación, con su historia. | El resultado de `amlr` (§4), con las revisiones anteriores a A contadas según AC-n. Puede estar vencido el mismo día A. | AMLR (§4). |
| **T-3. AMLR desde A, sin superar el RD** | Por analogía con la DT 7.ª de la Ley, el primer periodo del AMLR corre desde A. | El periodo en curso vence en la primera de estas fechas: el vencimiento del RD o A + P, con la P del AMLR que rige en A. Desde la primera revisión que cuenta con fecha ≥ A, AMLR. | AMLR (§4). |
| **T-4. Coexistencia** | La periodicidad del manual sigue obligando como Derecho nacional, porque la Ley y el RD no han cambiado, y el AMLR se añade. | La fecha más temprana entre `ley_rd` y `amlr`. | La fecha más temprana entre `ley_rd` y `amlr`. |

Notas:

- **Antes de A**, los cuatro dan el resultado de `ley_rd`. Se calculan igual ([D-4]) y la comparación dice que coinciden.
- **[D-26] T-3 tiene como límite la fecha del RD** para no convertir el día A en una amnistía. Sin ese límite, un cliente vencido con el RD desde 2026 tendría un plazo nuevo de cinco años desde el 10 de julio de 2027. Es parte de cómo se construye la lectura, igual que en `plazos-conservacion-pbc`, no una decisión sobre cuál aplicar. Con el límite, T-3 solo difiere de T-1 cuando A + P es anterior al vencimiento del RD (ejemplo 9).
- **[D-27] T-1 y T-3, después de la primera revisión posterior a A**, calculan como `amlr` con esa revisión como ancla. Las lecturas de §2 y §4 se aplican dentro de cada T-n: una T-n puede ser `indeterminado` por sí misma.
- **T-4** no es solo transitoria: afecta también a los clientes nuevos. Se incluye aquí porque es la que más cambia el resultado desde A. Es la más exigente por construcción.
- **[D-25] Eventos en la transición.** Con T-1, T-2 y T-3, cada evento se juzga con la norma aplicable en su fecha de activación: el RD si la activación es anterior a A y el AMLR si es posterior o igual. Con T-4, con las dos: el evento obliga si lo activa cualquiera de ellas, y se toma la activación más temprana ([D-21]). La alternativa, aplicar el art. 26.3 del AMLR desde A a eventos anteriores no atendidos, daría a un cambio de titularidad de 2026 que el RD no cubría una revisión exigible desde A. Se descartó porque el art. 26.3 activa la revisión cuando el cambio «se produzca», no después.
- **[D-28]** La salida compara T-1 a T-4 y dice expresamente si no coinciden: el estado del cliente en R depende entonces de cómo se resuelva S-2. También dice si `ley_rd` y `amlr` no coinciden.

---

## 6. Eventos

### 6.1. Cuándo un evento activa una revisión

Un evento activa una revisión en un régimen y una lectura si se cumplen las tres condiciones siguientes:

1. su tipo corresponde a un supuesto de ese régimen en esa lectura (§6.2 y §6.3);
2. `relevante_segun_entidad = true`;
3. la relación estaba viva en la fecha de activación.

**[D-18]** Un evento que la entidad valoró como no relevante no activa nada en ningún régimen. Los dos textos exigen entidad: el RD, art. 33.1.b, un «cambio relevante [...] que pudiera influir en su perfil de riesgo»; el AMLR, art. 26.3, «circunstancias pertinentes» y un «hecho relevante». Valorarlo es tarea de la entidad (modelo, §6.1).

**[D-19]** Un evento está **atendido** si alguna revisión con resultado `actualizada` o `sin_cambios` lo incluye en `eventos`. Da igual la fecha de esa revisión (modelo, V-12). Una revisión que no lo incluye no lo atiende, aunque sea posterior. La alternativa, que cualquier revisión posterior lo atienda, daría por revisado un cambio que la revisión no examinó, y el modelo tiene el campo `eventos` precisamente para saberlo. Una revisión `no_completada` no atiende nada ([D-8]).

**[D-21]** Si en una lectura varios supuestos activan el mismo evento con fechas distintas, se toma la más temprana. Por ejemplo, un cambio de actividad por el RD 33.1.b y por la Ley 7.2. Cualquiera de los supuestos basta para obligar.

### 6.2. Ley y RD

**Los textos.**
- RD, art. 33.1.b: «La actualización será, en todo caso, preceptiva cuando se verifique un cambio relevante en la actividad del cliente que pudiera influir en su perfil de riesgo».
- Ley, art. 7.2, párrafo segundo: «En todo caso, los sujetos obligados aplicarán a los clientes existentes las medidas de diligencia debida en función del riesgo cuando se proceda a la contratación de nuevos productos, cambien las circunstancias del cliente o cuando se produzca una operación significativa por su volumen o complejidad y, en todo caso, cuando el sujeto obligado tenga obligación en el curso del año natural correspondiente de ponerse en contacto con el cliente para revisar la información pertinente relativa al titular o titulares reales».

**Alcance del art. 7.2 (S-10).**
- **L72-1.** Solo se aplica a los clientes existentes cuando entró en vigor la Ley. La Ley se publicó en el «BOE» de 29 de abril de 2010 y entró en vigor «el día siguiente al de su publicación» (disposición final séptima), es decir, el 2010-04-30. Por tanto, solo se aplica si `fecha_inicio_relacion` < 2010-04-30.
- **L72-2.** Se aplica a cualquier cliente con una relación en curso.

**Fecha de «se verifique» en el art. 33.1.b (S-8).** **FV-1**: `fecha_hecho`. **FV-2**: `fecha_conocimiento`.

**Información de riesgo y `otro` en el art. 7.2 (S-9).** **LC-1**: no son un cambio de «las circunstancias del cliente». **LC-2**: sí lo son.

| `tipo` | RD 33.1.b | Ley 7.2 (solo si L72-1 lo permite o con L72-2) | Activación |
|---|---|---|---|
| `cambio_actividad` | sí | sí («cambien las circunstancias») | RD: según FV-n. Ley: `fecha_hecho`. La más temprana ([D-21]). |
| `cambio_identidad`, `cambio_titularidad_real_o_control`, `cambio_situacion_financiera` | no | sí («cambien las circunstancias») | `fecha_hecho` |
| `nuevo_producto` | no | sí («se proceda a la contratación») | `fecha_hecho` |
| `operacion_significativa` | no | sí («se produzca una operación») | `fecha_hecho` |
| `anomalia_operativa` | no | no | — |
| `informacion_de_riesgo`, `otro` | no | LC-1: no. LC-2: sí | `fecha_hecho` |
| `obligacion_contacto_titularidad_real` | no | sí (último inciso) | `fecha_hecho`, con límite el 31 de diciembre de `anio_natural` ([D-20]) |
| `obligacion_contacto_dac` | no | no | — |

La Ley 7.2 se activa en `fecha_hecho` porque sus verbos se refieren al hecho, no a su conocimiento: «se proceda», «cambien», «se produzca».

### 6.3. AMLR

**El texto.** Art. 26.3: «Además de los requisitos previstos en el apartado 2, las entidades obligadas revisarán y, cuando proceda, actualizarán la información del cliente cuando: a) se produzca un cambio en las circunstancias pertinentes de un cliente; b) la entidad obligada tenga una obligación legal, en el trascurso del año natural correspondiente, de ponerse en contacto con el cliente a fin de revisar la información pertinente relacionada con el titular o los titulares reales o de cumplir la Directiva 2011/16/UE del Consejo; c) entren en conocimiento de un hecho relevante relacionado con el cliente».

**La letra decide la fecha.**

| Letra | Qué la activa | Fecha de activación |
|---|---|---|
| a) | «se produzca un cambio» | `fecha_hecho` |
| b) | «tenga una obligación legal, en el trascurso del año natural correspondiente» | `fecha_hecho` (nace la obligación), con límite el 31 de diciembre de `anio_natural` ([D-20]) |
| c) | «entren en conocimiento de un hecho» | `fecha_conocimiento` |

**Qué letra corresponde a cada tipo** (modelo, §6.2). Donde el tipo no tiene una letra clara (S-9), las lecturas **EV-A** (letra a), **EV-C** (letra c) y **EV-N** (ningún supuesto):

| `tipo` | Letra | Lecturas |
|---|---|---|
| `cambio_actividad`, `cambio_identidad`, `cambio_titularidad_real_o_control`, `cambio_situacion_financiera` | a) | — |
| `nuevo_producto` | a) o ninguna | EV-A, EV-N |
| `operacion_significativa`, `anomalia_operativa`, `otro` | a), c) o ninguna | EV-A, EV-C, EV-N |
| `informacion_de_riesgo` | c) | — |
| `obligacion_contacto_titularidad_real`, `obligacion_contacto_dac` | b) | — |

**Un hecho de la letra a) que la entidad aún no conoce.** Con la letra a), la revisión es exigible desde que el cambio se produce, aunque la entidad lo sepa después (S-8). El cálculo lo aplica tal cual. Si la entidad conoce el cambio cuando el plazo del manual ya ha pasado, la revisión sale `vencida` desde el primer día. El resultado lo señala con un aviso, porque es una consecuencia de la letra, no un error de la entrada.

### 6.4. Plazo de la revisión por evento (S-7)

**Los textos.**
- RD, art. 33.1.b: la actualización «será, en todo caso, preceptiva». No da plazo.
- AMLR, art. 26.3: «revisarán y, cuando proceda, actualizarán». No da plazo.
- Borrador AMLA, ap. 20.d: «a customer information review should be initiated without delay» [la revisión debe iniciarse sin demora]. Ap. 25: «without undue delay» [sin demora indebida]. Habla de iniciar la revisión, no de terminarla.

**[D-20]** La fecha límite de un evento activado y no atendido es:
- si la versión del manual vigente en la fecha de activación fija `plazo_revision_por_evento_dias`: la fecha de activación más ese plazo ([D-3]);
- en las obligaciones de contacto (letra b del AMLR; último inciso de la Ley 7.2): el 31 de diciembre de `anio_natural`, porque la obligación es «en el trascurso del año natural correspondiente». Si el manual fija un plazo que acaba antes, rige el del manual;
- si no hay plazo ni en el manual ni en la norma: ninguna. El evento queda en `revision_pendiente_sin_plazo`, con la fecha de activación como fecha desde la que la revisión es exigible.

El «without delay» del borrador no se convierte en un plazo. No tiene efecto normativo y no dice cuántos días. Convertirlo en «el mismo día» o en un número de días sería inventar un plazo que ningún texto fija. Por eso existe el estado `revision_pendiente_sin_plazo`: dice que la revisión se debe y que nadie ha fijado cuándo, en lugar de elegir en silencio entre `en_plazo` y `vencida`.

### 6.5. El evento y el calendario periódico

Una revisión `por_evento` que cuenta (§2.3) mueve el calendario periódico solo con RA-1, o con RA-3 cuando el manual dice `true` (§2.2). Con AC-2, además, solo si su resultado es `actualizada`.

---

## 7. Relación terminada y datos incompletos

- **[D-22]** Si `fecha_terminacion_relacion` ≤ R, el estado es `relacion_terminada` en todos los regímenes y lecturas, y no hay próxima revisión. Las revisiones que estuvieran vencidas ese día se mencionan en un aviso. Motivo: el seguimiento continuo es de la relación (Ley, art. 6; AMLR, art. 26.1), y terminada la relación no hay nada que seguir. Si la relación terminó por no poder actualizar la información, eso es lo que exigen la Ley, art. 7.3, y el AMLR, art. 21.1.
- **Clasificación sin periodicidad en el manual** (modelo, V-6): con la Ley y el RD, [D-14] o [D-16]; con el AMLR, PM-2 usa L.
- **Versión del manual vigente.** Si en una fecha no hay ninguna versión vigente, porque todas son posteriores, se aplica [D-13]: la primera versión.

---

## 8. Resumen: qué hace cada régimen con cada dato

| Pregunta | Ley y RD | AMLR |
|---|---|---|
| Qué inicia el cómputo | Última revisión que cuenta (RA-n); si no hay, IP-n | Igual, pero la revisión sin cambios cuenta según AC-n |
| Plazo del riesgo alto | Manual, con máximo de 12 meses si `superior_al_promedio` | 12 meses si hay riesgo elevado y medidas de la sección 4 (PB-n) |
| Plazo del resto | El del manual; sin él, `sin_plazo` | 60 meses; el manual solo lo acorta con PM-2 |
| Manual más largo que el límite | Solo recortado en el riesgo superior al promedio | Siempre recortado a L ([D-17]) |
| Revisión sin cambios | Cuenta | AC-1 cuenta; AC-2 no |
| Eventos | Cambio de actividad (RD 33.1.b), y los de la Ley 7.2 según L72-n | Letras a), b) y c), con su fecha propia |
| Fecha del evento | «Se verifique»: FV-n | a): hecho; b): obligación; c): conocimiento |
| Obligación de contacto por la Directiva 2011/16/UE | No existe | Letra b) |

---

## 9. Ejemplos

Salvo que se indique otra cosa:
- `sujeto.actividad = "otra"` (A = 2027-07-10);
- relación viva;
- cada revisión atiende los eventos que se indican;
- el manual tiene `plazo_revision_por_evento_dias` y `revision_anticipada_reinicia_plazo` a `null`;
- cuando la entidad «califica con los dos criterios», la clasificación tiene los tres booleanos con valor.

En las tablas, «RD» es el régimen `ley_rd` y «AMLR» el régimen `amlr`.

### Ejemplo 1. Riesgo normal: el manual con el RD, el máximo legal con el AMLR

Relación desde el **2020-03-02**, con diligencia debida inicial ese día (`actualizada`) y sin más revisiones. Clasificación del 2020-03-02: `medio`, con `superior_al_promedio`, `riesgo_elevado_amlr` y `medidas_seccion_4_amlr` a `false`. Manual: `medio` = 36 meses.

Todas las lecturas IP y RA dan como ancla el 2020-03-02, porque la relación, la revisión inicial y la clasificación son del mismo día.

| | RD | AMLR, PM-1 | AMLR, PM-2 |
|---|---|---|---|
| P | 36 (manual) | 60 (art. 26.2.b) | 36 (el menor de 60 y 36) |
| Fecha límite | 2023-03-02 | 2025-03-02 | 2023-03-02 |

**Con R = 2024-06-01:**
- `ley_rd`: `vencida`.
- `amlr`: `indeterminado` (PM-1 `en_plazo`, PM-2 `vencida`), con el aviso de que el AMLR no es aplicable en esa fecha ([D-24]).
- T-1 a T-4: `vencida`, porque antes de A son `ley_rd`.

**Con R = 2028-01-15:** los seis regímenes dan `vencida`. La diferencia entre el RD y el AMLR solo existe en la comparación.

### Ejemplo 2. Poblaciones que no coinciden: persona del medio político que la entidad no considera de riesgo elevado

Relación desde el **2028-03-01**, con revisión inicial ese día. Clasificación: `medio`; `superior_al_promedio = true` (la Ley, art. 14, impone medidas reforzadas a las personas con responsabilidad pública); `riesgo_elevado_amlr = false`; `medidas_seccion_4_amlr = true` (AMLR, art. 42). Manual: `medio` = 36 meses. R = **2029-06-01**.

| | P | Fecha límite | Estado |
|---|---|---|---|
| RD | 12 (el menor de 36 y 12, con aviso [D-14]) | 2029-03-01 | `vencida` |
| AMLR, PB-1 y PM-1 | 60 | 2033-03-01 | `en_plazo` |
| AMLR, PB-1 y PM-2 | 36 | 2031-03-01 | `en_plazo` |
| AMLR, PB-2 | 12 | 2029-03-01 | `vencida` |

Resultado:
- `ley_rd`: `vencida`.
- `amlr`: `indeterminado`.
- El cliente es nuevo (inicio ≥ A), así que T-1, T-2 y T-3 son `amlr`: `indeterminado`.
- T-4: `vencida` en todas las lecturas, porque la fecha del RD es siempre la más temprana.

El RD pone a este cliente en el plazo anual. El AMLR solo lo hace si basta uno de los dos elementos del art. 26.2.a.

### Ejemplo 3. Revisión sin cambios: el RD la cuenta; el AMLR, según la lectura

Relación desde el **2027-09-01**, con revisión inicial ese día (`actualizada`). Clasificación: `alto`, con los tres booleanos a `true`. Manual: `alto` = 12. Revisión `periodica` el **2028-08-20** con resultado `sin_cambios`. R = **2029-01-10**.

| | Ancla | Fecha límite | Estado |
|---|---|---|---|
| RD (cualquier RA) | 2028-08-20 | 2029-08-20 | `en_plazo` |
| AMLR, AC-1 | 2028-08-20 | 2029-08-20 | `en_plazo` |
| AMLR, AC-2, RA-1 | 2027-09-01 (la inicial; la de 2028 no cuenta) | 2028-09-01 | `vencida` |
| AMLR, AC-2, RA-2 | 2027-09-01 (IP-1 = IP-2 = IP-3) | 2028-09-01 | `vencida` |

Resultado:
- `ley_rd`: `en_plazo`.
- `amlr`: `indeterminado`.
- T-1 a T-3 (cliente nuevo): `indeterminado`.
- T-4: `indeterminado`, porque la fecha más temprana es 2029-08-20 con AC-1 y 2028-09-01 con AC-2.

Con AC-2, la entidad revisó a tiempo y aun así está vencida desde 2028-09-02, porque la revisión no cambió nada. Es la consecuencia de leer «actualizaciones» al pie de la letra.

### Ejemplo 4. Revisión anticipada por un evento: las tres lecturas de «can reset»

Relación desde el **2028-01-10**, con revisión inicial ese día. Clasificación: `medio` y todo a `false`. Manual: `medio` = 36.

- Evento EV-1: `cambio_titularidad_real_o_control`, hecho el 2029-05-02 y conocido el 2029-05-20, relevante.
- Lo atiende una revisión `por_evento` del **2029-06-15** (`actualizada`).
- R = **2031-03-01**.

| | Ancla | P | Fecha límite | Estado |
|---|---|---|---|---|
| RD, RA-1 | 2029-06-15 | 36 | 2032-06-15 | `en_plazo` |
| RD, RA-2 | 2028-01-10 (sin periódicas: IP) | 36 | 2031-01-10 | `vencida` |
| AMLR, RA-1, PM-1 | 2029-06-15 | 60 | 2034-06-15 | `en_plazo` |
| AMLR, RA-2, PM-1 | 2028-01-10 | 60 | 2033-01-10 | `en_plazo` |
| AMLR, RA-1, PM-2 | 2029-06-15 | 36 | 2032-06-15 | `en_plazo` |
| AMLR, RA-2, PM-2 | 2028-01-10 | 36 | 2031-01-10 | `vencida` |

RA-3 con el manual a `null` da los dos resultados. Resultado:
- `ley_rd`: `indeterminado`.
- `amlr`: `indeterminado`.
- T-1 a T-4: `indeterminado`.

**Variante con `revision_anticipada_reinicia_plazo = true`:** RA-3 da lo mismo que RA-1, pero RA-2 sigue existiendo, así que los estados no cambian ([D-10] y la nota de §2.2). El manual no puede decidir si la norma permite reiniciar.

El evento no queda pendiente en ninguna lectura, porque está atendido. Con el RD, además, no activa nada con L72-1 (el cliente es de 2028) y sí con L72-2, pero eso no cambia el resultado.

### Ejemplo 5. Las dos fechas del evento según la letra

Relación desde el **2027-10-01**, con revisión inicial ese día. Clasificación: `medio` y todo a `false`. Manual vigente desde 2027-07-10: `medio` = 36 y `plazo_revision_por_evento_dias = 30`. La revisión periódica está `en_plazo` en todos los regímenes: vence el 2030-10-01 con el RD y con PM-2, y el 2032-10-01 con PM-1.

Un evento relevante, **no atendido**: hecho el **2028-04-01** y conocido el **2028-05-10**. R = **2028-05-20**. Se calculan cuatro variantes del mismo evento, cambiando solo su tipo:

| Variante: `tipo` | AMLR | Estado AMLR | RD | Estado RD |
|---|---|---|---|---|
| a. `cambio_titularidad_real_o_control` | Letra a): 2028-04-01 + 30 = **2028-05-01** | `vencida` | No está en el RD 33.1.b. L72-1: nada (cliente de 2027). L72-2: 2028-05-01 | `indeterminado` |
| b. `informacion_de_riesgo` | Letra c): 2028-05-10 + 30 = **2028-06-09** | `en_plazo` | L72-1: nada. L72-2 y LC-1: nada. L72-2 y LC-2: 2028-05-01, `vencida` | `indeterminado` |
| c. `operacion_significativa` | EV-A: 2028-05-01, `vencida`. EV-C: 2028-06-09, `en_plazo`. EV-N: nada, `en_plazo` | `indeterminado` | L72-1: nada. L72-2: 2028-05-01 | `indeterminado` |
| d. `cambio_actividad` | Letra a): 2028-05-01 | `vencida` | RD 33.1.b, FV-1: 2028-05-01, `vencida`. FV-2: 2028-06-09, `en_plazo`. Con L72-2, la Ley activa el 2028-04-01 y rige la fecha más temprana: `vencida` | `indeterminado` |

Qué enseña cada variante:
- **a y b.** El mismo hecho, con las mismas fechas, está vencido o en plazo según sea un cambio de circunstancias (letra a) o un hecho relevante conocido (letra c).
- **c.** Cuando el tipo no tiene letra clara, el AMLR queda indeterminado.
- **d.** Incluso el único supuesto del RD depende de qué significa «se verifique».

Sin `plazo_revision_por_evento_dias` en el manual, las fechas límite de esta tabla no existirían. El evento estaría en `revision_pendiente_sin_plazo` desde su activación en todas las variantes que lo activan, salvo en las que no lo activa ninguna lectura.

### Ejemplo 6. Inicio del primer periodo

Relación desde el **2027-10-01**. La entidad clasificó al cliente antes de establecer la relación, el **2027-09-20**: `alto`, con los tres booleanos a `true`. Completó la diligencia debida inicial el **2027-11-25**, a los 55 días (AMLR, art. 33.1.a). Manual: `alto` = 12. No hay más revisiones. R = **2028-10-10**.

| | Ancla | Fecha límite | Estado |
|---|---|---|---|
| RA-1 (la revisión inicial marca el calendario) | 2027-11-25 | 2028-11-25 | `en_plazo` |
| RA-2 e IP-1 (inicio de la relación) | 2027-10-01 | 2028-10-01 | `vencida` |
| RA-2 e IP-2 (revisión inicial) | 2027-11-25 | 2028-11-25 | `en_plazo` |
| RA-2 e IP-3 (primera clasificación) | 2027-09-20 | 2028-09-20 | `vencida` |

El resultado es el mismo en los dos regímenes, porque P = 12 en todas las lecturas: `indeterminado` en los seis. El inicio del primer periodo solo importa con RA-2, porque con RA-1 la revisión inicial ya es el ancla.

### Ejemplo 7. Reclasificación a mitad de periodo

Relación desde el **2027-12-01**, con revisión inicial ese día. Clasificación inicial: `medio` y todo a `false`. Manual: `medio` = 36, `alto` = 12. El **2029-03-15**, sin revisión, la entidad reclasifica al cliente a `alto`, con los tres booleanos a `true`. R = **2029-06-01**.

| | RD | AMLR |
|---|---|---|
| FR-1 (la clasificación del ancla, `medio`) | 2030-12-01, `en_plazo` | PM-1: 2032-12-01; PM-2: 2030-12-01. `en_plazo` |
| FR-2 (`alto`, desde el ancla 2027-12-01) | 2028-12-01, `vencida` | 2028-12-01, `vencida` |
| FR-3 (`alto`, desde la reclasificación) | 2030-03-15, `en_plazo` | 2030-03-15, `en_plazo` |

Resultado: `indeterminado` en los seis regímenes. Con FR-2, el cliente pasa a estar vencido desde hace seis meses el mismo día en que se le reclasifica.

### Ejemplo 8. Cliente existente el día A, sin calificación con el AMLR

Relación desde el **2015-06-01**, con revisión inicial ese día. Clasificación única, del 2015-06-01: `alto`, `superior_al_promedio = true`, y `riesgo_elevado_amlr` y `medidas_seccion_4_amlr` a `null`. Manual: `alto` = 12. Última revisión: `periodica` del **2026-11-15**, `actualizada`.

AMLR, con ancla 2026-11-15:
- NC-1 y PM-1: 60 meses, 2031-11-15.
- NC-1 y PM-2: 12 meses, 2027-11-15.
- NC-2: 12 meses, 2027-11-15.

| Régimen | Fecha límite | R = 2027-10-01 | R = 2028-02-01 |
|---|---|---|---|
| `ley_rd` | 2027-11-15 | `en_plazo` | `vencida` |
| `amlr` | 2031-11-15 o 2027-11-15 | `en_plazo` | `indeterminado` |
| T-1 (periodo en curso con el RD) | 2027-11-15 | `en_plazo` | `vencida` |
| T-2 (AMLR desde la última revisión) | como `amlr` | `en_plazo` | `indeterminado` |
| T-3 (desde A, sin superar el RD) | el menor de 2027-11-15 y A + P: 2027-11-15 | `en_plazo` | `vencida` |
| T-4 (coexistencia) | 2027-11-15 | `en_plazo` | `vencida` |

El 2028-02-01, T-1 a T-4 no coinciden ([D-28]). Solo T-2 deja abierta la posibilidad de que un cliente de riesgo alto con el RD tenga cinco años con el AMLR, porque la entidad no lo ha calificado de nuevo.

### Ejemplo 9. Cliente existente con un manual más largo que el AMLR

Relación desde el **2012-02-01**. Clasificaciones:
- del 2012-02-01: `bajo`, `superior_al_promedio = false`, y los datos del AMLR a `null`;
- del **2027-07-10**: `bajo` y todo a `false`.

Manual: `bajo` = 120 meses, porque la entidad aplica medidas simplificadas (RD, art. 17.1.b: «Reducir la periodicidad del proceso de revisión documental»). Última revisión: `periodica` del **2024-01-15**, `actualizada`.

Fechas:
- RD: 2024-01-15 + 120 = **2034-01-15**.
- AMLR: 2024-01-15 + 60 = **2029-01-15**, en todas las lecturas: NC-1 y NC-2 dan 60, PM-2 da el menor de 60 y 120, y FR-3 no cambia nada porque P no cambió. Lleva el aviso de que el manual supera el límite ([D-17]).
- T-3: el menor de 2034-01-15 y A + 60 = **2032-07-10**.

| Régimen | Fecha límite | R = 2030-01-01 | R = 2032-09-01 |
|---|---|---|---|
| `ley_rd` | 2034-01-15 | `en_plazo` | `en_plazo` |
| `amlr` | 2029-01-15 | `vencida` | `vencida` |
| T-1 | 2034-01-15 | `en_plazo` | `en_plazo` |
| T-2 | 2029-01-15 | `vencida` | `vencida` |
| T-3 | 2032-07-10 | `en_plazo` | `vencida` |
| T-4 | 2029-01-15 | `vencida` | `vencida` |

Es el caso en que las cuatro lecturas de la transición se separan:
- **T-1** mantiene el plazo del RD hasta 2034.
- **T-2** da el cliente por vencido desde antes de 2030.
- **T-3** le da de plazo hasta cinco años después de A, el 2032-07-10.
- **T-4** coincide con T-2.

---

## 10. Salida

La forma del resultado está en §1.5. La línea de órdenes y los códigos de salida se fijarán con la implementación.

Para cada cliente, el resultado da:

- el estado y la fecha de la próxima revisión obligatoria en los seis regímenes;
- dónde difieren: `ley_rd` frente a `amlr`, y T-1 a T-4 entre sí ([D-28]);
- las lecturas de cada régimen con sus fechas y citas;
- los componentes periódico y por evento;
- los avisos.

Lleva la misma advertencia que en `plazos-conservacion-pbc`: es un cálculo bajo las lecturas que declara esta especificación, no una determinación jurídica.

---

## 11. Índice de decisiones

| Id | Decisión | Sección |
|---|---|---|
| D-1 | «N meses desde F» vence el mismo día N meses después; si no existe, el último día del mes. Un año son 12 meses. | §1.3 |
| D-2 | El día de vencimiento está en plazo; `vencida` desde el día siguiente. | §1.3 |
| D-3 | Los plazos del manual en días son días naturales, y el último día está en plazo. | §1.3 |
| D-4 | El régimen es un parámetro; se calculan siempre los seis y ninguno es principal. | §1.1 |
| D-5 | El resultado tiene una entrada por régimen, con estado, fecha, componentes, lecturas y avisos. | §1.5 |
| D-6 | Si todas las lecturas dan el mismo estado, ese es el estado; si no, `indeterminado`. | §1.5 |
| D-7 | Las lecturas se combinan todas con todas; en los eventos, una lectura por tipo. | §1.5 |
| D-8 | Una revisión `no_completada` no cuenta ni atiende eventos en ningún régimen. | §2.3 |
| D-9 | RA-2 es «solo las revisiones periódicas marcan el calendario», no «fecha prevista + P». | §2.2 |
| D-10 | RA-3 usa el manual vigente en la fecha de cada revisión; con `null`, las dos maneras. | §2.2 |
| D-11 | Sin revisión inicial que cuente, IP-2 no existe, con aviso. | §2.1 |
| D-12 | Una sola dimensión (FR) para el cambio de clasificación y el de manual. | §2.4 |
| D-13 | Sin clasificación o manual vigente en una fecha, se usa la primera. | §2.4, §7 |
| D-14 | Con el RD y riesgo superior al promedio: el menor del manual y 12 meses; sin manual, 12. | §3.2 |
| D-15 | Una calificación a `null` se evalúa con los dos valores (con el AMLR, si faltan las dos: NC-1 y NC-2). | §3.2, §4.2 |
| D-16 | Con el RD, sin riesgo superior al promedio y sin periodicidad en el manual: `sin_plazo`. | §3.2 |
| D-17 | Con el AMLR, la periodicidad nunca supera el límite legal, tampoco con medidas simplificadas; aviso. | §4.2 |
| D-18 | Un evento no relevante no activa nada. | §6.1 |
| D-19 | Un evento está atendido si lo incluye una revisión `actualizada` o `sin_cambios`. | §6.1 |
| D-20 | Plazo de un evento: el del manual; en las obligaciones de contacto, el 31 de diciembre del año; si no hay ninguno, `revision_pendiente_sin_plazo`. | §6.4 |
| D-21 | Si varios supuestos activan el mismo evento, rige la activación más temprana. | §6.1 |
| D-22 | Relación terminada en R o antes: `relacion_terminada`, sin próxima revisión. | §7 |
| D-23 | Prioridad de estados dentro de una lectura. | §1.4 |
| D-24 | El AMLR se calcula también antes de A y sobre toda la historia, con aviso. | §4.1 |
| D-25 | En la transición, cada evento se juzga con la norma de su fecha de activación; con T-4, con las dos. | §5.2 |
| D-26 | T-3 no supera el vencimiento del RD. | §5.2 |
| D-27 | T-1 y T-3 pasan al AMLR desde la primera revisión que cuenta con fecha ≥ A. | §5.2 |
| D-28 | La salida señala si T-1 a T-4 no coinciden y si `ley_rd` y `amlr` no coinciden. | §5.2 |
| D-29 | La próxima revisión obligatoria es la fecha límite sin cumplir más temprana; los eventos sin plazo van aparte. | §1.4 |
