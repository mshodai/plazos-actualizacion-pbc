# Modelo de datos de entrada

Este documento define el JSON que recibe el cálculo de la **fecha de la próxima revisión obligatoria de la información de un cliente** en una fecha dada. Solo describe la entrada: el cálculo y su salida se definirán más adelante, en otro documento.

Siglas y fuentes (detalle y huellas en [`fuentes/FUENTES.md`](fuentes/FUENTES.md)):

- **Ley**: Ley 10/2010, texto consolidado con última modificación de 21 de marzo de 2026.
- **RD**: Reglamento aprobado por el Real Decreto 304/2014, texto consolidado con última modificación de 24 de abril de 2024.
- **AMLR**: Reglamento (UE) 2024/1624, texto publicado en el DO L de 19.6.2024.
- **Borrador AMLA**: documento de consulta de la AMLA sobre las directrices del art. 26.5 del AMLR, de 3 de junio de 2026. **Es un borrador sometido a consulta y no tiene efecto normativo.** La consulta se cerró el 3 de septiembre de 2026 y las directrices finales se esperan en el cuarto trimestre de 2026. Aquí solo se usa para documentar cómo propone la AMLA leer el art. 26 en lo que el texto no resuelve. Ningún campo es obligatorio solo por lo que diga el borrador.

Convenciones:

- Las citas van entre comillas «» y son literales. Las del borrador AMLA están en inglés, el único idioma en que se publicó, y van seguidas de una traducción propia entre corchetes cuando hace falta.
- **[Decisión propia]** marca lo que no sale de los textos, sino del diseño de este proyecto.
- Los casos que la norma no resuelve (S-1 a S-13) están en la sección [Casos que la norma no resuelve](#casos-que-la-norma-no-resuelve). El modelo no los decide: recoge los hechos que hacen falta para calcular cada lectura.

---

## 0. Principios

1. **La entrada recoge hechos, no conclusiones.** **[Decisión propia]** El JSON dice cómo ha clasificado la entidad al cliente, qué dice su manual, cuándo revisó la información y qué pasó entre medias. No dice qué plazo aplica, desde cuándo cuenta ni si una revisión está vencida: eso lo deduce el cálculo, y depende del régimen y de la lectura.
2. **El régimen no forma parte de la entrada.** **[Decisión propia]** El régimen es un parámetro del cálculo. El mismo JSON se calcula con la Ley y el RD, con el AMLR y con cada lectura de la transición entre ambos. Si la entrada incluyera un campo `regimen`, quien la rellena estaría eligiendo sin saberlo cómo se trata a los clientes existentes el 10 de julio de 2027 ([S-2](#s-2)), que ningún texto resuelve.
3. **La validación no depende del régimen.** **[Decisión propia]** Un hecho que un régimen no usa no es un error de entrada. Por ejemplo, la calificación de riesgo según el AMLR de un cliente cuya fecha de referencia es de 2026, o un evento que el RD no menciona.
4. **La clasificación de riesgo es un dato, no un cálculo.** **[Decisión propia]**, apoyada en que los dos regímenes dejan la clasificación a la entidad:
   - RD, art. 11.1: riesgos superiores al promedio «por disposición normativa o porque así se desprenda del análisis de riesgo del sujeto obligado». Art. 33.1.a: el manual contiene «una descripción precisa de los clientes que potencialmente puedan suponer un riesgo superior al promedio».
   - AMLR, art. 20.2, párrafo segundo: «Cuando las entidades obligadas determinen un riesgo mayor de blanqueo de capitales o financiación del terrorismo, aplicarán medidas reforzadas de diligencia debida conforme a la sección 4 del presente capítulo».

   El cálculo no vuelve a evaluar los factores de riesgo (RD, art. 19; AMLR, anexos II y III). Usa la calificación que hizo la entidad.

---

## 1. Ejemplo completo

```json
{
  "version_modelo": 1,
  "fecha_referencia": "2027-11-15",
  "sujeto": {
    "actividad": "otra"
  },
  "manual": {
    "versiones": [
      {
        "id": "MANUAL-2019",
        "vigente_desde": "2019-01-01",
        "periodicidades": [
          { "nivel_entidad": "bajo", "meses": 60 },
          { "nivel_entidad": "medio", "meses": 36 },
          { "nivel_entidad": "alto", "meses": 12 }
        ],
        "plazo_revision_por_evento_dias": null,
        "revision_anticipada_reinicia_plazo": null
      },
      {
        "id": "MANUAL-2027",
        "vigente_desde": "2027-07-10",
        "periodicidades": [
          { "nivel_entidad": "bajo", "meses": 60 },
          { "nivel_entidad": "medio", "meses": 36 },
          { "nivel_entidad": "alto", "meses": 6 }
        ],
        "plazo_revision_por_evento_dias": 30,
        "revision_anticipada_reinicia_plazo": true
      }
    ]
  },
  "cliente": {
    "id": "CLI-0042",
    "fecha_inicio_relacion": "2019-05-10",
    "fecha_terminacion_relacion": null,
    "clasificaciones": [
      {
        "fecha": "2019-05-10",
        "nivel_entidad": "medio",
        "superior_al_promedio": false,
        "riesgo_elevado_amlr": null,
        "medidas_seccion_4_amlr": null
      },
      {
        "fecha": "2027-07-10",
        "nivel_entidad": "medio",
        "superior_al_promedio": false,
        "riesgo_elevado_amlr": false,
        "medidas_seccion_4_amlr": false
      },
      {
        "fecha": "2027-09-20",
        "nivel_entidad": "alto",
        "superior_al_promedio": true,
        "riesgo_elevado_amlr": true,
        "medidas_seccion_4_amlr": true
      }
    ],
    "revisiones": [
      {
        "id": "REV-1",
        "tipo": "inicial",
        "fecha": "2019-05-10",
        "resultado": "actualizada",
        "eventos": []
      },
      {
        "id": "REV-2",
        "tipo": "periodica",
        "fecha": "2025-02-14",
        "resultado": "sin_cambios",
        "eventos": []
      },
      {
        "id": "REV-3",
        "tipo": "por_evento",
        "fecha": "2027-09-20",
        "resultado": "actualizada",
        "eventos": ["EV-1"]
      }
    ],
    "eventos": [
      {
        "id": "EV-1",
        "tipo": "cambio_titularidad_real_o_control",
        "descripcion": "Entrada de un nuevo socio mayoritario",
        "fecha_hecho": "2027-09-01",
        "fecha_conocimiento": "2027-09-12",
        "relevante_segun_entidad": true
      }
    ]
  }
}
```

---

## 2. Campos de primer nivel

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `version_modelo` | entero | sí | Versión de este esquema. Es `1`. **[Decisión propia]** |
| `fecha_referencia` | fecha ISO 8601 (`AAAA-MM-DD`) | sí | Fecha para la que se calcula la próxima revisión obligatoria. Ver §7. |
| `sujeto` | objeto | sí | La entidad que revisa. Ver §2.1. |
| `manual` | objeto | sí | Lo que dice el manual de la entidad sobre las revisiones. Ver §3. |
| `cliente` | objeto | sí | La relación de negocios, su clasificación de riesgo, sus revisiones y sus eventos. Ver §4 a §6. |

No hay campo de régimen (§0, principio 2). Un JSON con `regimen`, o con cualquier otro campo que el modelo no define, es un error de validación (§9). **[Decisión propia]**

Todas las fechas son de día, sin hora ni zona horaria. **[Decisión propia]**: ninguna de las fuentes fija estos plazos por horas.

**Un JSON, un cliente.** **[Decisión propia]** El cálculo es por cliente. El AMLR mira la relación en su conjunto (art. 26.1, párrafo segundo: «Cuando las relaciones de negocios abarquen más de un producto o servicio, las entidades obligadas velarán por que las medidas de diligencia debida con respecto al cliente abarquen todos esos productos y servicios»; considerando 71: la actualización «no pretende centrarse en el producto o servicio concreto, sino en la relación de negocios en su totalidad»), y el RD también (art. 11.1: «El escrutinio tendrá carácter integral, debiendo incorporar todos los productos del cliente»).

**Solo relaciones de negocios.** El seguimiento continuo solo existe en una relación de negocios (Ley, art. 6: «Los sujetos obligados aplicarán medidas de seguimiento continuo a la relación de negocios»; AMLR, art. 26.1). Una operación ocasional no tiene revisiones periódicas y no se representa en este modelo.

### 2.1. `sujeto`

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `actividad` | `"agente_de_futbol"` \| `"club_de_futbol_profesional"` \| `"otra"` | sí | Hecho del que depende la fecha de aplicación del AMLR. Art. 90: «Será aplicable a partir del 10 de julio de 2027, excepto para las entidades obligadas a que se refiere el artículo 3, punto 3, letras n) a o), para quienes será aplicable desde el 10 de julio de 2029». Letra n): «los agentes de fútbol». Letra o): «los clubes de fútbol profesional» en relación con determinadas operaciones. Mismo campo y mismos valores que en `plazos-conservacion-pbc`. **[Decisión propia]** |

---

## 3. Manual de la entidad: `manual`

### 3.1. Por qué hace falta

**En España no hay plazo legal para los clientes que no son de riesgo superior al promedio: lo fija el manual.** RD, art. 11.2, párrafo segundo: «El manual a que se refiere el artículo 33 determinará, en función del riesgo, la periodicidad de los procesos de revisión documental que para los clientes de riesgo superior al promedio será, como mínimo, anual». Art. 33.1.b: el manual incluirá «Un procedimiento estructurado de diligencia debida que incluirá la periódica actualización de la documentación e información exigibles».

El RD solo fija un límite para los clientes de riesgo superior al promedio. Para el resto, la periodicidad del manual es la única fuente del plazo.

El AMLR fija los dos límites. Art. 26.2, párrafo segundo: «El período entre las actualizaciones dela información del cliente conforme al párrafo primero dependerá del riesgo que plantea la relación de negocios y no será en ningún caso superior a: a) un año, en el caso de los clientes de riesgo elevado a los que se aplican las medidas de la sección 4 del presente capítulo; b) cinco años, en el caso de todos los demás clientes». (La errata «dela» es del texto publicado.) Con el AMLR, la periodicidad del manual no hace falta para calcular el límite legal. Qué papel tiene cuando es más corta que ese límite es el caso [S-11](#s-11).

### 3.2. Periodicidades por nivel, no un solo plazo para el riesgo normal

**[Decisión propia]** El manual no da un plazo para el «riesgo normal», sino una periodicidad por cada nivel de su escala de riesgo. Motivos:

- El RD pide periodicidades «en función del riesgo» (art. 11.2), no una para el riesgo superior al promedio y otra para el resto.
- El RD permite alargar el plazo a los clientes de riesgo bajo. Art. 17.1.b: entre las medidas simplificadas está «Reducir la periodicidad del proceso de revisión documental». Por eso un manual puede tener dos niveles por debajo del riesgo superior al promedio, con periodicidades distintas.
- El manual también puede fijar para el riesgo superior al promedio un plazo más corto que el año del RD.

Así, «la periodicidad del manual para los clientes de riesgo normal» es la de cada nivel en que `superior_al_promedio` es `false` (§4).

### 3.3. Versiones del manual

**[Decisión propia]** El manual cambia con el tiempo (RD, art. 33.2: «Los sujetos obligados, deberán proceder a la verificación y actualización periódicas del manual»), y un cambio de periodicidad puede caer en mitad de un periodo. Por eso la entrada recoge todas las versiones con su fecha de entrada en vigor. Qué versión rige un periodo que empezó con otra es el caso [S-13](#s-13).

`manual.versiones[]`:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Identificador de la versión. Único en la lista. |
| `vigente_desde` | fecha | sí | Fecha desde la que se aplica. Única en la lista. |
| `periodicidades` | lista de `{ "nivel_entidad": cadena, "meses": entero > 0 }` | sí | Periodicidad de la revisión para cada nivel de la escala de la entidad. `nivel_entidad` no se repite dentro de una versión. **[Decisión propia]**: en meses, porque los textos hablan de años («anual», «un año», «cinco años») y los manuales suelen usar meses o años. |
| `plazo_revision_por_evento_dias` | entero > 0 \| `null` | sí | Plazo que fija el manual para hacer la revisión después de un evento. `null` si el manual no fija ninguno. Ni el RD ni el AMLR fijan un plazo ([S-7](#s-7)). |
| `revision_anticipada_reinicia_plazo` | booleano \| `null` | sí | Si el manual dice que una revisión hecha antes de tiempo reinicia el cómputo de la siguiente. `null` si no lo dice. Ningún texto normativo trata la cuestión; el borrador AMLA dice que «can reset» ([S-3](#s-3)). |

Los dos últimos campos son hechos del manual, no de la norma. Se piden siempre, con `null` cuando el manual no dice nada, para que un campo olvidado no se confunda con un manual que calla. **[Decisión propia]**

---

## 4. Clasificación de riesgo: `cliente.clasificaciones[]`

### 4.1. Dos poblaciones distintas

Los dos regímenes no clasifican con el mismo criterio, y los dos plazos cortos se aplican a grupos de clientes que pueden no coincidir.

**Ley y RD: riesgo «superior al promedio».**
- RD, art. 11.2: la periodicidad «para los clientes de riesgo superior al promedio será, como mínimo, anual».
- Ley, art. 26.2: la política de admisión «incluirá una descripción de aquellos tipos de clientes que podrían presentar un riesgo superior al riesgo promedio».
- RD, art. 20.1: «En los supuestos de riesgo superior al promedio previstos en el artículo precedente o que se hubieran determinado por el sujeto obligado conforme a su análisis de riesgo». El artículo precedente, el 19, enumera los supuestos de medidas reforzadas: banca privada, envíos de dinero de más de 3.000 euros por trimestre, etc.

**AMLR: riesgo elevado **y** medidas de la sección 4.**
- Art. 26.2.a: «un año, en el caso de los clientes de riesgo elevado a los que se aplican las medidas de la sección 4 del presente capítulo». La sección 4 del capítulo III («Medidas reforzadas de diligencia debida») comprende los arts. 34 a 46.
- Art. 34.1: las medidas reforzadas se aplican «En los casos a que se refieren los artículos 29, 30, 31 y 36 a 46, y en otros casos de mayor riesgo que determinen las entidades obligadas conforme al artículo 20, apartado 2, párrafo segundo».
- Los factores de riesgo son los de los anexos II y III del AMLR y las directrices del art. 20.3, no los del art. 19 del RD.

Por qué pueden no coincidir:
- El criterio es distinto: la lista del art. 19 del RD no es la de los arts. 29 a 31 y 36 a 46 del AMLR, y la entidad valora factores distintos.
- El art. 26.2.a del AMLR tiene dos elementos, riesgo elevado y medidas de la sección 4, y el art. 11.2 del RD solo uno.
- Antes del 10 de julio de 2027 la entidad puede no haber calificado todavía a sus clientes con el AMLR.

### 4.2. Cómo se representa

**[Decisión propia]** Cada clasificación recoge, por separado, la calificación de la entidad con cada norma. Ninguna se deduce de otra.

| Campo | Tipo | Obligatorio | Régimen | Descripción |
|---|---|---|---|---|
| `fecha` | fecha | sí | ambos | Fecha desde la que rige esta clasificación. Única en la lista. |
| `nivel_entidad` | cadena | sí | ambos, a través del manual | Nivel en la escala propia de la entidad (por ejemplo `"bajo"`, `"medio"`, `"alto"`). Enlaza con `manual.versiones[].periodicidades[].nivel_entidad`. |
| `superior_al_promedio` | booleano \| `null` | sí | Ley y RD | Si la entidad considera al cliente de riesgo superior al promedio (RD 11.2; Ley 26.2). `null` si la entidad no hizo esta calificación. |
| `riesgo_elevado_amlr` | booleano \| `null` | sí | AMLR | Si la entidad ha determinado un riesgo mayor según el AMLR (art. 20.2, párrafo segundo; art. 26.2.a: «de riesgo elevado»). `null` si la entidad no hizo esta calificación. |
| `medidas_seccion_4_amlr` | booleano \| `null` | sí | AMLR | Si la entidad aplica a la relación medidas de la sección 4 del capítulo III del AMLR (arts. 34 a 46). `null` si no consta. |

Alternativas descartadas:

- **Un nivel común (`alto` / `normal` / `bajo`) del que el cálculo deduzca cada régimen.** Daría por hecho que «superior al promedio» y «riesgo elevado con sección 4» son lo mismo, que es justo lo que no se sabe.
- **Deducir las calificaciones de `nivel_entidad` con una tabla del manual.** Escondería la decisión de la entidad con cada norma. Además, el RD asigna la descripción de los clientes de riesgo superior al manual (art. 33.1.a) y el AMLR no.
- **Un solo campo para el AMLR.** Obligaría a elegir qué significa el art. 26.2.a cuando sus dos elementos no coinciden ([S-4](#s-4)).

Todas las combinaciones de valores se admiten, incluidas las que parecen contradictorias. Una de ellas es `riesgo_elevado_amlr = true` con `medidas_seccion_4_amlr = false`, contraria al art. 20.2, párrafo segundo: es un hecho, y el cálculo decide qué hacer con él (§0, principio 3).

### 4.3. Por qué una lista

Hace falta el historial, no solo la clasificación actual. Una reclasificación a mitad de periodo cambia el plazo que se aplica, y el RD y el AMLR no dicen desde cuándo cuenta el plazo nuevo ([S-5](#s-5)). La lista no puede estar vacía. **[Decisión propia]**

---

## 5. Revisiones: `cliente.revisiones[]`

La fecha de la última actualización no basta: hace falta el historial. **[Decisión propia]**, por tres motivos:
- el cálculo tiene que saber si la última revisión fue anticipada ([S-3](#s-3));
- tiene que distinguir una revisión que actualizó la información de otra que no cambió nada o que no se completó ([S-6](#s-6));
- tiene que saber qué eventos atendió cada revisión (§6).

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. |
| `tipo` | `"inicial"` \| `"periodica"` \| `"por_evento"` | sí | `inicial`: la diligencia debida al establecer la relación (Ley, art. 3 y siguientes; AMLR, art. 19.1.a). `periodica`: RD 11.2; AMLR 26.2. `por_evento`: RD 33.1.b; AMLR 26.3. |
| `fecha` | fecha | sí | Fecha en que concluyó la revisión. **[Decisión propia]**: la de conclusión y no la de inicio, porque el AMLR cuenta «el período entre las actualizaciones» (art. 26.2) y la información solo está actualizada cuando la revisión termina. |
| `resultado` | `"actualizada"` \| `"sin_cambios"` \| `"no_completada"` | sí | `actualizada`: se obtuvo información nueva o se corrigió la que había. `sin_cambios`: se revisó y la información seguía siendo correcta. `no_completada`: la entidad no pudo obtener la información, por ejemplo porque el cliente no respondió. Qué resultados cuentan como actualización es el caso [S-6](#s-6). |
| `eventos` | lista de cadenas | sí (puede estar vacía) | `id` de los eventos que atendió esta revisión. Cada uno debe existir en `cliente.eventos`. |

**Tipo y anticipación.** **[Decisión propia]** No hay un tipo «anticipada». Una revisión periódica hecha antes de su fecha es `periodica`, y una revisión por evento también puede caer antes de la fecha de la periódica. Que una revisión sea anticipada depende del plazo que se aplica, y el plazo depende del régimen: es una conclusión del cálculo, no un hecho.

La lista puede estar vacía. Qué fecha inicia entonces el primer periodo es el caso [S-1](#s-1).

---

## 6. Eventos: `cliente.eventos[]`

### 6.1. Campos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Único en la lista. |
| `tipo` | ver §6.2 | sí | Qué ocurrió. |
| `descripcion` | cadena | sí si `tipo = "otro"`; si no, opcional | Texto libre. |
| `fecha_hecho` | fecha | sí | Fecha en que ocurrió el hecho. En los dos tipos de obligación de contacto (§6.2), fecha en que nace la obligación. |
| `fecha_conocimiento` | fecha | sí | Fecha en que la entidad tuvo conocimiento del hecho. No puede ser anterior a `fecha_hecho`. |
| `anio_natural` | entero | sí en los dos tipos de obligación de contacto; en los demás no se admite | Año natural en que la entidad tiene la obligación de ponerse en contacto con el cliente (AMLR 26.3.b; Ley 7.2). |
| `relevante_segun_entidad` | booleano | sí | Si la entidad valoró el hecho como relevante. |

**Dos fechas.** Los textos no activan la revisión en el mismo momento:
- AMLR, art. 26.3.a: «se produzca un cambio en las circunstancias pertinentes de un cliente». Cuenta cuándo ocurre el hecho.
- AMLR, art. 26.3.c: «entren en conocimiento de un hecho relevante relacionado con el cliente». Cuenta cuándo lo conoce la entidad.
- RD, art. 33.1.b: «cuando se verifique un cambio relevante». «Verificarse» puede significar tanto producirse como comprobarse.

Por eso se piden las dos ([S-8](#s-8)).

**Relevancia.** Los dos textos exigen que el hecho tenga cierta entidad. El RD, art. 33.1.b, habla de un «cambio relevante en la actividad del cliente que pudiera influir en su perfil de riesgo». El AMLR, art. 26.3, habla de «circunstancias pertinentes» en la letra a) y de un «hecho relevante» en la c). Valorarlo es tarea de la entidad, igual que la clasificación (§0, principio 4). **[Decisión propia]**: un solo campo para los dos regímenes. El RD añade a la relevancia la condición de que el cambio «pudiera influir en su perfil de riesgo», y el AMLR no. Se da por hecho que la entidad valora con ese criterio cuando calcula con el RD.

### 6.2. Tipos de evento y supuesto al que corresponden

**[Decisión propia]** El tipo describe **qué ocurrió**, no qué artículo se aplica. La correspondencia con cada régimen la hace el cálculo según esta tabla. Los tipos siguen los textos y, donde estos no concretan, los ejemplos del borrador AMLA (ap. 27) y del considerando 69 del AMLR.

| `tipo` | RD 33.1.b | Ley 7.2, párr. 2 ([S-10](#s-10)) | AMLR 26.3 | Borrador AMLA, ap. 27 |
|---|---|---|---|---|
| `cambio_actividad` | **Sí** | Sí («cambien las circunstancias del cliente») | a) | d) «business activity» |
| `cambio_identidad` | No | Sí («cambien las circunstancias») | a) | a) |
| `cambio_titularidad_real_o_control` | No | Sí («cambien las circunstancias») | a) (considerando 69: «cambios en la titularidad real») | a) |
| `cambio_situacion_financiera` | No | Sí («cambien las circunstancias») | a) | d) |
| `nuevo_producto` | No | **Sí** («contratación de nuevos productos») | a) o ninguno ([S-9](#s-9)) | d) «new products or services used by the customer» |
| `operacion_significativa` | No | **Sí** («operación significativa por su volumen o complejidad») | a), c) o ninguno ([S-9](#s-9)) | b) |
| `anomalia_operativa` | No | No | a), c) o ninguno ([S-9](#s-9)) | b) |
| `informacion_de_riesgo` | No | No, salvo que sea un cambio de circunstancias ([S-9](#s-9)) | c) | c) |
| `obligacion_contacto_titularidad_real` | No | **Sí** (último inciso) | **b)**, primer inciso | — |
| `obligacion_contacto_dac` | No | No | **b)**, segundo inciso | — |
| `otro` | No | Sin determinar | Sin determinar ([S-9](#s-9)) | — |

Qué es cada tipo:

- `cambio_actividad`: cambio en la actividad profesional o empresarial del cliente.
- `cambio_identidad`: cambio de los datos identificativos, la nacionalidad, la residencia o la forma jurídica.
- `cambio_titularidad_real_o_control`: cambio de titulares reales, estructura de propiedad, administradores, apoderados o representantes.
- `cambio_situacion_financiera`: cambio significativo en la situación financiera, el origen de los fondos o el patrimonio.
- `nuevo_producto`: el cliente contrata un producto o servicio nuevo.
- `operacion_significativa`: una operación significativa por su volumen o su complejidad.
- `anomalia_operativa`: una alerta del seguimiento de operaciones o una pauta que no encaja con el perfil del cliente.
- `informacion_de_riesgo`: información nueva sobre el cliente que afecta al riesgo: noticias adversas, adquisición de la condición de persona del medio político, procedimientos judiciales, avisos de autoridades.
- `obligacion_contacto_titularidad_real`: la entidad tiene una obligación legal de ponerse en contacto con el cliente para revisar la información sobre sus titulares reales.
- `obligacion_contacto_dac`: la entidad tiene una obligación legal de ponerse en contacto con el cliente para cumplir la Directiva 2011/16/UE.
- `otro`: cualquier otro hecho. Exige `descripcion`.

Textos:

- **RD, art. 33.1.b:** «La actualización será, en todo caso, preceptiva cuando se verifique un cambio relevante en la actividad del cliente que pudiera influir en su perfil de riesgo». Es el único supuesto de revisión por evento del RD, y solo habla de la actividad.
- **AMLR, art. 26.3:** «Además de los requisitos previstos en el apartado 2, las entidades obligadas revisarán y, cuando proceda, actualizarán la información del cliente cuando: a) se produzca un cambio en las circunstancias pertinentes de un cliente; b) la entidad obligada tenga una obligación legal, en el trascurso del año natural correspondiente, de ponerse en contacto con el cliente a fin de revisar la información pertinente relacionada con el titular o los titulares reales o de cumplir la Directiva 2011/16/UE del Consejo; c) entren en conocimiento de un hecho relevante relacionado con el cliente».
- **Ley, art. 7.2, párrafo segundo:** «En todo caso, los sujetos obligados aplicarán a los clientes existentes las medidas de diligencia debida en función del riesgo cuando se proceda a la contratación de nuevos productos, cambien las circunstancias del cliente o cuando se produzca una operación significativa por su volumen o complejidad y, en todo caso, cuando el sujeto obligado tenga obligación en el curso del año natural correspondiente de ponerse en contacto con el cliente para revisar la información pertinente relativa al titular o titulares reales». No está entre los supuestos pedidos para este modelo, pero se recoge en la tabla porque su último inciso es casi literal al art. 26.3.b del AMLR y porque recoge tres eventos que el RD no menciona. Su alcance es el caso [S-10](#s-10).
- **AMLR, considerando 69:** la entidad «debe considerar la necesidad de revisar el archivo del cliente en respuesta a cambios materiales, como un cambio en las jurisdicciones con las que se hayan realizado operaciones, en el valor o el volumen de las operaciones, cuando se soliciten nuevos productos o servicios que sean significativamente diferentes en términos de riesgo, o a raíz de cambios en la titularidad real». Un considerando no es parte dispositiva, y además dice «considerar la necesidad».
- **Borrador AMLA, ap. 27:** «The following non-exhaustive list of events are provided as instances of what may trigger a review of customer information based on changes in the relevant circumstances of the customer or facts which pertain to the customer, pursuant to Article 26(3) AMLR» [la siguiente lista no exhaustiva de eventos se da como ejemplo de lo que puede activar una revisión de la información del cliente por cambios en sus circunstancias pertinentes o hechos que le atañen, conforme al art. 26.3 del AMLR]. Sus letras: a) «Changes in identity, legal status or ownership»; b) «Behavioural, activity-based or transactional anomalies»; c) «Risk‑relevant information or adverse findings»; d) «Changes in financial situation, source of funds or wealth or business activity». El borrador no asigna cada ejemplo a una letra del art. 26.3.

**Fuera del modelo.** **[Decisión propia]** No se recogen:
- la sospecha de blanqueo de capitales o de financiación del terrorismo;
- las dudas sobre la veracidad de los datos (Ley, art. 7.1, párrafo tercero; AMLR, art. 19.1.d y e);
- la comprobación periódica de las sanciones financieras específicas (AMLR, art. 26.4).

Las dos primeras obligan a aplicar de nuevo la diligencia debida (art. 19 del AMLR), no a la revisión del art. 26.3. La tercera tiene su propia frecuencia, «proporcional a la exposición» (art. 26.4). Ninguna cambia la fecha de la revisión del art. 26.2 salvo a través de una revisión, y las revisiones ya se recogen en §5.

---

## 7. Fecha de referencia

`fecha_referencia` es la fecha para la que se calcula la próxima revisión obligatoria.

- Es obligatoria. **[Decisión propia]**: no se toma la fecha del sistema por defecto, para que el mismo JSON dé siempre el mismo resultado.
- Puede ser anterior o posterior al 10 de julio de 2027. **[Decisión propia]**: la fecha no restringe con qué régimen se puede calcular.
- Los hechos del cliente no pueden ser posteriores a ella: clasificaciones, revisiones, eventos (las dos fechas), inicio y terminación de la relación. Tampoco `vigente_desde` de una versión del manual. Si lo son, es un error de validación. **[Decisión propia]**: los hechos posteriores a la fecha de referencia no se conocían en esa fecha, igual que en `plazos-conservacion-pbc`.
- Se exceptúa `anio_natural`, que puede ser el año de la fecha de referencia o uno posterior: es el año en que se debe cumplir una obligación, no un hecho ocurrido.

**Relación terminada.** `fecha_terminacion_relacion` indica que el seguimiento continuo terminó: no hay próxima revisión. Se recoge porque sin ella no se distingue un cliente vivo sin revisiones de uno que ya no lo es. La relación puede terminar precisamente por no poder actualizar la información. AMLR, art. 21.1: la entidad «pondrá fin a la relación de negocios»; Ley, art. 7.3: «Cuando se aprecie la imposibilidad en el curso de la relación de negocios, los sujetos obligados pondrán fin a la misma».

| Campo de `cliente` | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | cadena | sí | Identificador del cliente. |
| `fecha_inicio_relacion` | fecha | sí | Fecha en que se estableció la relación de negocios. Candidata a inicio del primer periodo ([S-1](#s-1)). |
| `fecha_terminacion_relacion` | fecha \| `null` | sí | `null` mientras la relación siga viva. No puede ser anterior a `fecha_inicio_relacion`. |
| `clasificaciones` | lista | sí, no vacía | §4. |
| `revisiones` | lista | sí (puede estar vacía) | §5. |
| `eventos` | lista | sí (puede estar vacía) | §6. |

---

## 8. Qué dato exige cada régimen y cuál no tiene el otro

Todos los datos se validan igual con independencia del régimen (§0, principio 3). Esta tabla solo dice quién los usa.

| Dato | Ley y RD | AMLR | Base |
|---|---|---|---|
| `manual.versiones[].periodicidades` | **Sí**: única fuente del plazo de los clientes que no son de riesgo superior al promedio | Solo para [S-11](#s-11): el límite legal no depende del manual | RD 11.2 y 33.1.b; AMLR 26.2 |
| `clasificaciones[].superior_al_promedio` | **Sí** | No | RD 11.2; Ley 26.2 |
| `clasificaciones[].riesgo_elevado_amlr` | No | **Sí** | AMLR 20.2 y 26.2.a |
| `clasificaciones[].medidas_seccion_4_amlr` | No | **Sí** | AMLR 26.2.a y 34.1 |
| `clasificaciones[].nivel_entidad` | Sí, para buscar la periodicidad | Solo para [S-11](#s-11) | RD 11.2 |
| `revisiones[].fecha` | Sí | Sí | RD 11.2; AMLR 26.2 |
| `revisiones[].resultado` | Cuenta el «proceso de revisión» ([S-6](#s-6)) | Cuenta la «actualización» ([S-6](#s-6)) | RD 11.2; AMLR 26.2 y 26.3 |
| Evento `cambio_actividad` | **Sí** | Sí (a) | RD 33.1.b; AMLR 26.3.a |
| Eventos de cambio de identidad, titularidad o situación financiera | No en el RD; sí en la Ley 7.2 ([S-10](#s-10)) | **Sí** (a) | AMLR 26.3.a |
| `nuevo_producto`, `operacion_significativa` | No en el RD; sí en la Ley 7.2 ([S-10](#s-10)) | Sin determinar ([S-9](#s-9)) | Ley 7.2; AMLR considerando 69 |
| `informacion_de_riesgo` | No | **Sí** (c) | AMLR 26.3.c |
| `obligacion_contacto_titularidad_real` y `anio_natural` | No en el RD; sí en la Ley 7.2 ([S-10](#s-10)) | **Sí** (b) | AMLR 26.3.b; Ley 7.2 |
| `obligacion_contacto_dac` y `anio_natural` | **No** | **Sí** (b) | AMLR 26.3.b |
| `eventos[].fecha_conocimiento` | Sin determinar ([S-8](#s-8)) | **Sí** en la letra c) | AMLR 26.3.c; RD 33.1.b |
| `eventos[].fecha_hecho` | Sin determinar ([S-8](#s-8)) | **Sí** en la letra a) | AMLR 26.3.a |
| `manual.versiones[].plazo_revision_por_evento_dias` | Ningún texto lo pide ([S-7](#s-7)) | Ningún texto lo pide ([S-7](#s-7)) | — |
| `manual.versiones[].revision_anticipada_reinicia_plazo` | Ningún texto lo pide ([S-3](#s-3)) | Ningún texto lo pide; lo menciona el borrador AMLA ([S-3](#s-3)) | Borrador AMLA, ap. 2 |
| `sujeto.actividad` | No | **Sí** | AMLR 90 |

**Lo que tiene un régimen y no el otro, en resumen:**

- **Solo la Ley y el RD:** un plazo que depende del manual. RD, art. 11.2: el manual «determinará, en función del riesgo, la periodicidad». El AMLR no remite a ningún manual para el plazo máximo: lo fija él.
- **Solo el AMLR:**
  - un plazo máximo para todos los clientes (art. 26.2.b: «cinco años, en el caso de todos los demás clientes»);
  - dos elementos para el plazo de un año: riesgo elevado **y** medidas de la sección 4 (art. 26.2.a);
  - las revisiones por obligación de contacto (26.3.b) y por hecho relevante conocido (26.3.c).
- **Solo el RD:** la revisión por evento se limita a los cambios en la actividad del cliente (art. 33.1.b). Los demás eventos solo tienen base en la Ley, art. 7.2, cuyo alcance es dudoso ([S-10](#s-10)).

---

## 9. Validación

La validación no depende del régimen (§0, principio 3). Se recogen todos los errores de la entrada, no solo el primero, y si hay alguno la entrada se rechaza entera. Los códigos de error se fijarán con la implementación.

Todas estas reglas son **[Decisión propia]**.

| Id | Regla | Motivo |
|---|---|---|
| V-1 | Un campo que el modelo no define es un error, en cualquier objeto. También lo es `anio_natural` en un evento que no es de obligación de contacto. | Un campo que el cálculo no lee pasaría como si sirviera de algo. Es la misma regla que en `plazos-conservacion-pbc` (V-2). |
| V-2 | Los campos que admiten `null` se piden siempre: omitirlos es un error. | Un campo olvidado no se distingue de un `null` intencionado. |
| V-3 | `version_modelo` debe ser `1`. | — |
| V-4 | `id` únicos dentro de cada lista (versiones del manual, revisiones, eventos). `vigente_desde` y `clasificaciones[].fecha` únicas dentro de su lista. | Con dos clasificaciones o dos versiones del mismo día no se sabe cuál rige. |
| V-5 | `nivel_entidad` no se repite dentro de las periodicidades de una versión. | El nivel tendría dos periodicidades. |
| V-6 | No se comprueba que el `nivel_entidad` de una clasificación exista en las periodicidades del manual. | Que falte es un hecho posible, por ejemplo si el manual cambia de escala, y qué hace el cálculo depende de qué versión rija ([S-13](#s-13)). |
| V-7 | `clasificaciones` no puede estar vacía. | Sin clasificación no hay plazo en ningún régimen. |
| V-8 | Los `id` de `revisiones[].eventos` deben existir en `cliente.eventos`. | — |
| V-9 | `fecha_conocimiento` no puede ser anterior a `fecha_hecho`. | No se puede conocer un hecho antes de que ocurra. En las obligaciones de contacto, la obligación nace en `fecha_hecho`. |
| V-10 | `fecha_terminacion_relacion` no puede ser anterior a `fecha_inicio_relacion`. | — |
| V-11 | Un hecho posterior a `fecha_referencia` es un error (§7), salvo `anio_natural`. | — |
| V-12 | No se comprueba que las revisiones sean posteriores a `fecha_inicio_relacion`, ni que los eventos que atiende una revisión sean anteriores a ella. | La diligencia debida inicial puede preceder al día de establecimiento de la relación, y una revisión puede atender un evento conocido después si se registra así. El cálculo no depende de ese orden. |
| V-13 | Se admiten todas las combinaciones de `superior_al_promedio`, `riesgo_elevado_amlr` y `medidas_seccion_4_amlr`. | Son hechos (§4.2). |

---

## Casos que la norma no resuelve

Para cada caso: régimen afectado, qué dice la norma, por qué no determina un resultado único y qué recoge el modelo para poder calcular cada lectura. El modelo no los decide. Los identificadores S-n son estables: no se renumeran ni se reutilizan.

<a id="s-1"></a>
### S-1. Fecha de inicio del primer periodo

**Régimen.** Los dos.

**Qué dice la norma.**
- RD, art. 11.2: fija la «periodicidad» de los procesos de revisión, pero no dice desde cuándo cuenta.
- AMLR, art. 26.2: «El período entre las actualizaciones dela información del cliente». Cuenta entre actualizaciones, y no dice qué ocurre antes de la primera.
- Ni la Ley ni el RD ni el AMLR dicen si la diligencia debida inicial cuenta como la primera actualización.

**Por qué no determina un resultado único.** Hay al menos tres fechas candidatas, y pueden ser distintas:
- el establecimiento de la relación (`fecha_inicio_relacion`);
- la conclusión de la diligencia debida inicial (revisión `inicial`). Puede ser posterior al establecimiento: el AMLR, art. 33.1.a, permite comprobar la identidad «después del establecimiento de la relación de negocios [...] pero en ningún caso más de sesenta días después», y el RD, art. 17.1.a, cuando se supere un umbral;
- la primera clasificación de riesgo.

El borrador AMLA tampoco lo fija. Ap. 21: la entidad debe valorar «the information collected at customer onboarding and during the most recent customer review» [la información recogida al dar de alta al cliente y en la revisión más reciente]. Menciona la incorporación del cliente, pero no como inicio de un plazo.

**Qué recoge el modelo.** Las tres fechas: `fecha_inicio_relacion`, la revisión de tipo `inicial` si existe y `clasificaciones[0].fecha`.

<a id="s-2"></a>
### S-2. Clientes existentes el 10 de julio de 2027

**Régimen.** Transición entre la Ley y el RD y el AMLR.

**Qué dice la norma.**
- AMLR, art. 90: «Será aplicable a partir del 10 de julio de 2027» (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)).
- El AMLR no tiene ninguna disposición transitoria sobre el seguimiento continuo ni sobre los clientes que ya lo eran ese día. Su considerando 76 reconoce que el examen de los clientes existentes en el marco anterior «ya se basa en el riesgo», pero solo para justificar la supervisión periódica de «algunas categorías claramente especificadas de clientes ya existentes».
- La Ley consolidada a 21 de marzo de 2026 no contiene ninguna adaptación al AMLR.
- Precedente: cuando entró en vigor, la Ley sí fijó un régimen para los clientes existentes. Disposición transitoria séptima: «los sujetos obligados aplicarán a todos sus clientes existentes las medidas de diligencia debida establecidas en el Capítulo II en un plazo máximo de cinco años, contados a partir de la entrada en vigor de la presente Ley». El AMLR no tiene nada equivalente.

**Por qué no determina un resultado único.** Para un cliente con la relación viva el 10 de julio de 2027:
1. **Qué plazo del AMLR se aplica** si en esa fecha la entidad no lo ha calificado aún con el AMLR (`riesgo_elevado_amlr` y `medidas_seccion_4_amlr` a `null`). Puede aplicarse el de cinco años, deducirse de `superior_al_promedio` o considerar que no hay plazo calculable.
2. **Desde cuándo cuenta el primer periodo del AMLR**: desde la última revisión hecha con el RD o desde el 10 de julio de 2027. Con la primera lectura, un cliente de riesgo superior al promedio revisado en enero de 2026 tendría el plazo de un año vencido el primer día. Con la segunda, un cliente de riesgo normal revisado en 2020 no tendría revisión obligatoria hasta 2032.
3. **Qué pasa con una revisión que el manual exigía antes del 10 de julio de 2027 y no se hizo**: si sigue siendo exigible con el plazo del RD o si pasa al del AMLR.

**Qué recoge el modelo.** Todas las clasificaciones y revisiones con su fecha, con independencia de la norma con que se hicieron, y `sujeto.actividad` para saber qué fecha de aplicación rige. El régimen es un parámetro del cálculo (§0, principio 2), y cada lectura de la transición se podrá calcular como un régimen propio, igual que en `plazos-conservacion-pbc`.

<a id="s-3"></a>
### S-3. Revisión anticipada: «can reset» del borrador AMLA

**Régimen.** AMLR. Con la Ley y el RD, la cuestión es la misma y tampoco hay texto.

**Qué dice la norma.**
- AMLR, art. 26.2: fija el período máximo «entre las actualizaciones». No dice si una actualización hecha antes de tiempo, por ejemplo por un evento del art. 26.3, inicia un período nuevo.
- Borrador AMLA, ap. 2: «Article 26(2) of AMLR sets the maximum periods of time for updating customer information for both higher-risk customers and all the other customers. However, obliged entities should decide whether more frequent updates are needed based on the customer's risk profile. If a review is carried out earlier than scheduled, this can reset the timeline for the next required update» [si una revisión se hace antes de lo previsto, puede reiniciar el plazo de la siguiente actualización].
- RD: nada.

**Por qué no determina un resultado único.**
- El borrador no tiene efecto normativo, y su redacción final puede cambiar.
- Dice que la revisión anticipada «puede» reiniciar el plazo, no que lo reinicie. Admite tres lecturas: siempre lo reinicia; nunca lo reinicia (el calendario de revisiones periódicas es fijo); lo decide la entidad.
- No dice si vale para cualquier revisión o solo para una periódica adelantada. Tampoco si vale para una revisión por evento que solo cubrió parte de la información: el borrador, ap. 3, pide valorar «which elements of the customer information [...] require updating» [qué elementos de la información del cliente hay que actualizar].

**Qué recoge el modelo.** Todas las revisiones con su tipo y su fecha (§5). También lo que dice el manual, en `revision_anticipada_reinicia_plazo`, que sirve para la tercera lectura. Con `null`, esa lectura no tiene dato.

<a id="s-4"></a>
### S-4. Riesgo superior al promedio frente a riesgo elevado con medidas de la sección 4

**Régimen.** Los dos, y la transición.

**Qué dice la norma.** Ver §4.1. El RD usa un criterio: riesgo superior al promedio (art. 11.2). El AMLR usa dos: riesgo elevado y medidas de la sección 4 (art. 26.2.a).

**Por qué no determina un resultado único.**
- **Si el relativo del art. 26.2.a restringe o describe.** «Clientes de riesgo elevado a los que se aplican las medidas de la sección 4». Si restringe, un cliente de riesgo elevado al que no se aplican esas medidas tiene cinco años. Si describe, todo cliente de riesgo elevado tiene un año.
- **Clientes con medidas de la sección 4 por disposición y no por valoración propia.** Por ejemplo, una persona del medio político (arts. 42 y siguientes) o un tercer país de alto riesgo (art. 29), cuando la entidad no lo considera de riesgo elevado. El art. 34.1 enumera esos casos junto a «otros casos de mayor riesgo», lo que sugiere que todos son de mayor riesgo, pero el art. 26.2.a no lo dice.
- **Medidas de la sección 4 sobre una operación y no sobre el cliente.** El art. 34.2 obliga a examinar el origen y destino de los fondos de ciertas operaciones de cualquier cliente. Si un examen así basta para que al cliente «se le apliquen las medidas de la sección 4», cualquier cliente con una operación inusual pasaría a tener un plazo de un año. **[Decisión propia]**: `medidas_seccion_4_amlr` recoge si las medidas se aplican a la relación, no a una operación aislada. Se descartó registrar también los exámenes del art. 34.2 porque convertiría una medida sobre la operación en una clasificación del cliente. Esta decisión no resuelve el caso: solo fija qué significa el dato.
- **Clientes sin calificación con el AMLR.** Ver [S-2](#s-2).

**Qué recoge el modelo.** Las tres calificaciones por separado (§4.2), sin deducir ninguna de otra.

<a id="s-5"></a>
### S-5. Reclasificación a mitad de un periodo

**Régimen.** Los dos.

**Qué dice la norma.** Ni el RD, art. 11.2, ni el AMLR, art. 26.2, dicen qué ocurre cuando el cliente cambia de clasificación entre dos revisiones. El borrador AMLA, ap. 3, dice que al revisar se valore si hay que actualizar «the customer risk classification» [la clasificación de riesgo del cliente], pero no qué pasa con el plazo en curso.

**Por qué no determina un resultado único.** Un cliente revisado hace 18 meses pasa hoy a riesgo superior al promedio. El plazo de un año puede contarse desde la última revisión, y entonces está vencido desde hace seis meses. También puede contarse desde la reclasificación, y entonces vence dentro de un año. Al bajar de clasificación, la duda es la contraria: si el plazo largo se aplica al periodo en curso o solo desde la siguiente revisión.

**Qué recoge el modelo.** El historial de clasificaciones con su fecha (§4.3). Una reclasificación que resulta de una revisión tiene la misma fecha que ella, como en el ejemplo del §1.

<a id="s-6"></a>
### S-6. Revisión sin cambios o no completada: revisión frente a actualización

**Régimen.** Los dos, con textos distintos.

**Qué dice la norma.**
- RD, art. 11.2: la periodicidad es la «de los procesos de revisión documental». Cuenta la revisión.
- AMLR, art. 26.2: «El período entre las actualizaciones». Cuenta la actualización. El art. 26.3 distingue «revisarán y, cuando proceda, actualizarán».
- AMLR, considerando 70: para clientes recurrentes, la diligencia debida puede cumplirse «obteniendo una confirmación del cliente de que la información y los documentos conservados en los registros no han cambiado».
- Borrador AMLA, aps. 30 a 32: si el cliente no responde, la entidad puede suspender temporalmente las operaciones antes de terminar la relación.

**Por qué no determina un resultado único.**
- Con el AMLR, no está claro si una revisión que confirma que nada ha cambiado es una «actualización» que inicia un nuevo período. El considerando 70 apunta a que sí, pero habla de la diligencia debida en clientes recurrentes, no del art. 26.2.
- Con los dos regímenes, no está claro si una revisión no completada cuenta. Con el RD, podría contar como «proceso de revisión». Con el AMLR, no hay actualización.

**Qué recoge el modelo.** `revisiones[].resultado` con tres valores (§5).

<a id="s-7"></a>
### S-7. Plazo para hacer la revisión por evento

**Régimen.** Los dos.

**Qué dice la norma.**
- RD, art. 33.1.b: la actualización «será, en todo caso, preceptiva». No da plazo.
- AMLR, art. 26.3: «revisarán y, cuando proceda, actualizarán». No da plazo.
- Borrador AMLA, ap. 20.d: «where this is the case, a customer information review should be initiated without delay» [en ese caso, la revisión debe iniciarse sin demora]. Ap. 25: los cambios deben detectarse, revisarse y tratarse «without undue delay» [sin demora indebida]. Habla de iniciar la revisión, no de terminarla.

**Por qué no determina un resultado único.** Sin plazo, la «fecha de la próxima revisión obligatoria» tras un evento puede ser la del evento (sin demora), la que fije el manual o no existir, y entonces solo sigue vigente el plazo periódico.

**Qué recoge el modelo.** `manual.versiones[].plazo_revision_por_evento_dias`, `null` si el manual no fija plazo, y las dos fechas del evento ([S-8](#s-8)).

<a id="s-8"></a>
### S-8. Fecha en que el evento activa la revisión

**Régimen.** Los dos.

**Qué dice la norma.** AMLR, art. 26.3.a: «se produzca un cambio». Art. 26.3.c: «entren en conocimiento de un hecho». RD, art. 33.1.b: «cuando se verifique un cambio relevante».

**Por qué no determina un resultado único.**
- En la letra a) del AMLR, la obligación nace cuando se produce el cambio, aunque la entidad no lo sepa. Sin embargo, no se puede revisar lo que no se conoce.
- En el RD, «verificarse» admite los dos sentidos: producirse y comprobarse.
- Cuando un mismo hecho encaja en la letra a) y en la c), las dos fechas compiten.

**Qué recoge el modelo.** `fecha_hecho` y `fecha_conocimiento` en todos los eventos (§6.1).

<a id="s-9"></a>
### S-9. Eventos sin supuesto claro

**Régimen.** Los dos.

**Qué dice la norma.** Ver §6.2.

**Por qué no determina un resultado único.**
- **RD.** El art. 33.1.b solo menciona el cambio en la actividad. Un nuevo producto, una operación significativa o una noticia adversa solo activan la revisión con el RD si se consideran un cambio en la actividad «que pudiera influir en su perfil de riesgo», o por la Ley, art. 7.2 ([S-10](#s-10)).
- **AMLR.** La frontera entre la letra a) («cambio en las circunstancias pertinentes») y la c) («hecho relevante») no está trazada. Un nuevo producto o un volumen anómalo de operaciones puede ser una circunstancia pertinente, un hecho relevante o ninguna de las dos. El considerando 69 y el borrador AMLA (ap. 27) los tratan como ejemplos de lo que «puede» activar una revisión, no de lo que la activa. La letra importa por la fecha ([S-8](#s-8)).
- **`otro`.** No se puede asignar a ningún supuesto sin valorar su contenido.

**Qué recoge el modelo.** El tipo de evento como hecho, la valoración de relevancia de la entidad y las dos fechas. La correspondencia con cada supuesto es la tabla del §6.2, con estas casillas marcadas como sin determinar.

<a id="s-10"></a>
### S-10. Alcance del art. 7.2 de la Ley

**Régimen.** Ley y RD.

**Qué dice la norma.** Ley, art. 7.2, párrafo primero: los sujetos obligados aplicarán la diligencia debida «no solo [...] a todos los nuevos clientes sino, asimismo, a los clientes existentes, en función de un análisis del riesgo». El párrafo segundo enumera los supuestos (§6.2). La disposición transitoria séptima fija un plazo de cinco años para «todos sus clientes existentes» desde la entrada en vigor de la Ley.

**Por qué no determina un resultado único.** «Clientes existentes» puede significar:
- los que ya lo eran cuando entró en vigor la Ley en 2010: lectura apoyada en la disposición transitoria séptima y en el tercer párrafo del art. 7.2, que habla de «obligaciones vigentes con anterioridad a la entrada en vigor de esta ley»;
- cualquier cliente con una relación en curso, por oposición a los «nuevos clientes».

Con la primera lectura, la revisión por evento del régimen español para los clientes posteriores a 2010 se limita al art. 33.1.b del RD. Con la segunda, se añaden los nuevos productos, las operaciones significativas, los cambios de circunstancias y la obligación de contacto sobre titulares reales.

**Qué recoge el modelo.** Los tipos de evento de la Ley 7.2 como hechos (§6.2), y `fecha_inicio_relacion` para distinguir los clientes anteriores a la Ley.

<a id="s-11"></a>
### S-11. Periodicidad del manual frente a los límites legales

**Régimen.** Los dos.

**Qué dice la norma.**
- RD, art. 11.2: para los clientes de riesgo superior al promedio, la periodicidad «será, como mínimo, anual». Para el resto, la que fije el manual, sin límite.
- AMLR, art. 26.2: el período «dependerá del riesgo que plantea la relación de negocios y no será en ningún caso superior» a uno o cinco años.
- AMLR, art. 33.1.b: entre las medidas simplificadas, «reducir la frecuencia de las actualizaciones de la identificación del cliente».
- Borrador AMLA, ap. 2: «obliged entities should decide whether more frequent updates are needed based on the customer's risk profile» [las entidades deben decidir, según el perfil de riesgo del cliente, si hacen falta actualizaciones más frecuentes].

**Por qué no determina un resultado único.**
- **Manual más corto que el límite del AMLR.** Si el manual fija 36 meses para el riesgo medio, la revisión es obligatoria para la entidad a los 36 meses por su propio procedimiento, pero el AMLR solo exige los cinco años. No está claro cuál es la «próxima revisión obligatoria». Con el RD no hay duda: el RD delega el plazo en el manual.
- **Manual más largo que el límite.** Con el RD, un manual con 18 meses para el riesgo superior al promedio incumple el mínimo anual. Con el AMLR, un manual con 72 meses para el riesgo bajo supera los cinco años. En los dos casos cabe aplicar el límite legal o señalar el incumplimiento.
- **Medidas simplificadas del AMLR.** El art. 33.1.b permite reducir la frecuencia de las actualizaciones de la identificación. Puede leerse dentro del límite de cinco años del art. 26.2.b («en ningún caso») o como excepción.
- **«Como mínimo, anual».** **[Decisión propia]**: se lee como «al menos una vez al año», es decir, un periodo de 12 meses o menos. La lectura literal contraria, un periodo de al menos un año, dejaría sin límite a los clientes de mayor riesgo y contradiría el art. 11.1 («incrementarán el seguimiento»).

**Qué recoge el modelo.** Las periodicidades del manual tal como son, sin recortarlas al límite legal (§3).

<a id="s-12"></a>
### S-12. Fecha de aplicación y fecha de referencia anteriores al AMLR

**Régimen.** AMLR.

**Qué dice la norma.** AMLR, art. 90: aplicable desde el 10 de julio de 2027, o desde el 10 de julio de 2029 para agentes de fútbol y clubes de fútbol profesional.

**Por qué no determina un resultado único.** Con una fecha de referencia anterior a la aplicación, calcular con el AMLR puede ser un error, una simulación («qué pasaría si ya se aplicara») o un cálculo de la primera fecha obligatoria después de la aplicación. En los clubes de fútbol, el art. 3, punto 3, letra o), limita la condición de entidad obligada a ciertas operaciones: con inversores, patrocinadores, agentes u otros intermediarios, y traspasos. No está claro si el seguimiento continuo alcanza a relaciones que solo en parte tienen que ver con esas operaciones.

**Qué recoge el modelo.** `sujeto.actividad` y `fecha_referencia` sin restricción (§7). No recoge qué operaciones del club están en el ámbito de la letra o). **[Decisión propia]**: se deja para cuando haya un caso que lo necesite.

<a id="s-13"></a>
### S-13. Versión del manual aplicable

**Régimen.** Ley y RD; con el AMLR, solo en la medida de [S-11](#s-11).

**Qué dice la norma.** RD, art. 33.2: el manual se actualiza periódicamente. Ningún texto dice qué versión rige un periodo de revisión que empezó con otra.

**Por qué no determina un resultado único.** Si el manual pasa de 36 a 24 meses para el riesgo medio, un cliente revisado antes del cambio puede tener la próxima revisión a los 36 meses (versión vigente en la última revisión) o a los 24 (versión vigente en la fecha de referencia). Con la segunda lectura, puede estar vencido desde el mismo día del cambio. Si la versión nueva ya no tiene el `nivel_entidad` del cliente, no hay periodicidad para él hasta que se le reclasifique.

**Qué recoge el modelo.** Todas las versiones con `vigente_desde` (§3.3).
