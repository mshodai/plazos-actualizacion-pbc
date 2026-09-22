# plazos-actualizacion-pbc

Un sujeto obligado por la normativa de prevención del blanqueo de capitales tiene que mantener actualizada la información de sus clientes: revisarla cada cierto tiempo y cuando pasa algo que la puede cambiar. Revisar tarde es un incumplimiento. Hasta ahora, en España, para los clientes que no son de riesgo superior al promedio el plazo lo decidía el manual de cada entidad. Con el Reglamento (UE) 2024/1624 (AMLR), aplicable desde el 10 de julio de 2027, hay un máximo: un año para los clientes de riesgo elevado a los que se aplican medidas reforzadas, y cinco para los demás.

Sitio: https://mshodai.github.io/plazos-actualizacion-pbc/, por qué una revisión que no cambia nada puede no reiniciar el plazo del AMLR.

El escenario. Una entidad tiene un cliente de riesgo medio desde 2020. Su manual fija una revisión cada 36 meses. Lo revisó en enero de 2025 y otra vez el 1 de diciembre de 2027, y en esa segunda revisión no encontró nada que cambiar. En marzo de 2028 alguien pregunta cuándo toca la próxima revisión:
- **Con el Real Decreto 304/2014:** la revisión de diciembre cuenta, así que la próxima es en diciembre de 2030.
- **Con el AMLR:** depende de si una revisión que no cambia nada es una «actualización» y de si el plazo que obliga es el del manual o el máximo de cinco años.
- **Para el paso de una norma a otra:** ningún texto dice qué pasa con los clientes que ya lo eran el 10 de julio de 2027. Una de las respuestas posibles es que la revisión de diciembre no la cuenta ninguna norma, y el cliente lleva vencido desde el 16 de enero de 2028.

Esta herramienta no da una fecha. Calcula la próxima revisión en seis regímenes (el RD, el AMLR y cuatro lecturas de la transición entre ambos) y muestra dónde difieren. Cuando el resultado depende de una pregunta que la norma no resuelve, dice cuál es la pregunta, qué pasa con cada respuesta y qué dato de la entrada la pone en juego. El porqué está en el [ADR 0001](docs/adr/0001-calcular-seis-regimenes-y-atribuir.md).

## El caso, calculado

El repositorio incluye un corpus de nueve clientes sintéticos en `corpus/`, cada uno con su resultado esperado. El del escenario es el caso 07:

```
$ plazos-actualizacion corpus/07-revision-de-2027-que-ninguna-norma-cuenta.json
Cliente CLI-FICTICIO-07
Fecha de referencia: 2028-03-01 · AMLR aplicable desde el 2027-07-10

Resultado de un cálculo bajo las lecturas que declara la especificación (docs/especificacion-calculo.md), no una determinación jurídica. Donde la norma no fija un dato, el cálculo da todas las lecturas y no elige; las decisiones propias se citan como D-n.

Próxima revisión y estado el 2028-03-01:
  ley_rd  2030-12-01                                               en_plazo
  amlr    entre el 2028-01-15 y el 2032-12-01 (4 fechas posibles)  indeterminado
  T-1     2028-01-15 o 2030-12-01 o 2032-12-01                     indeterminado
  T-2     entre el 2028-01-15 y el 2032-12-01 (4 fechas posibles)  indeterminado
  T-3     2028-01-15 o 2030-12-01 o 2032-12-01                     indeterminado
  T-4     2028-01-15 o 2030-01-15 o 2030-12-01                     indeterminado

Dónde difieren:
  ley_rd y amlr no coinciden: la norma cambia el resultado.
  T-1 a T-4 no coinciden: el resultado depende de cómo se resuelva la transición del 2027-07-10 (S-2, D-28).
  ley_rd: en_plazo; amlr, T-1, T-2, T-3, T-4: indeterminado
  «indeterminado»: las lecturas de ese régimen dan estados distintos (D-6).

Qué hay que decidir para salir del indeterminado (D-30, D-36):
  amlr:
    AC — ¿Una revisión sin cambios cuenta como actualización para el AMLR? (S-6, §2.3)
      AC-1 (sí cuenta): en_plazo, 2030-12-01 o 2032-12-01
      AC-2 (no cuenta): en_plazo o vencida, 2028-01-15 o 2030-01-15; aún depende de PM
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
    PM — Si el manual fija un plazo más corto que el máximo del AMLR, ¿cuál es el de la revisión obligatoria? (S-11, §4.2)
      PM-1 (el máximo del AMLR): en_plazo, 2030-01-15 o 2032-12-01
      PM-2 (el del manual): en_plazo o vencida, 2028-01-15 o 2030-12-01; aún depende de AC
      Datos: cliente.clasificaciones[0] (2020-01-10)
  T-1:
    AC — ¿Una revisión sin cambios cuenta como actualización para el AMLR? (S-6, §2.3)
      AC-1 (sí cuenta): en_plazo, 2030-12-01 o 2032-12-01
      AC-2 (no cuenta): vencida o en_plazo, 2028-01-15 o 2030-12-01 o 2032-12-01; aún depende de TR
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
    TR — ¿Qué norma decide si una revisión posterior a A cierra el periodo del RD? (S-16, D-33, §5.2)
      TR-1 (el AMLR): en_plazo o vencida, 2028-01-15 o 2030-12-01 o 2032-12-01; aún depende de AC
      TR-2 (el RD, mientras dura su periodo): en_plazo, 2030-12-01 o 2032-12-01
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
  T-2: lo mismo que amlr
  T-3: lo mismo que T-1
  T-4:
    AC — ¿Una revisión sin cambios cuenta como actualización para el AMLR? (S-6, §2.3)
      AC-1 (sí cuenta): en_plazo, 2030-12-01
      AC-2 (no cuenta): en_plazo o vencida, 2028-01-15 o 2030-01-15; aún depende de PM
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
    PM — Si el manual fija un plazo más corto que el máximo del AMLR, ¿cuál es el de la revisión obligatoria? (S-11, §4.2)
      PM-1 (el máximo del AMLR): en_plazo, 2030-01-15 o 2030-12-01
      PM-2 (el del manual): en_plazo o vencida, 2028-01-15 o 2030-12-01; aún depende de AC
      Datos: cliente.clasificaciones[0] (2020-01-10)

Componentes (D-37):
  ley_rd:
    Periódico:
      RD: desde el 2027-12-01, 36 meses → vence el 2030-12-01 (en_plazo)
    Por evento: ninguno pendiente.
  amlr:
    Periódico:
      AMLR: desde el 2027-12-01, 60 meses → vence el 2032-12-01 (en_plazo)  [en 1 de 4 combinaciones]
      AMLR: desde el 2027-12-01, 36 meses → vence el 2030-12-01 (en_plazo)  [en 1 de 4 combinaciones]
      AMLR: desde el 2025-01-15, 60 meses → vence el 2030-01-15 (en_plazo)  [en 1 de 4 combinaciones]
      AMLR: desde el 2025-01-15, 36 meses → vence el 2028-01-15 (vencida)  [en 1 de 4 combinaciones]
    Por evento: ninguno pendiente.
  T-1:
    Periódico:
      AMLR: desde el 2027-12-01, 60 meses → vence el 2032-12-01 (en_plazo)  [en 2 de 6 combinaciones]
      AMLR: desde el 2027-12-01, 36 meses → vence el 2030-12-01 (en_plazo)  [en 2 de 6 combinaciones]
      RD: desde el 2025-01-15, 36 meses → vence el 2028-01-15 (vencida)  [en 2 de 6 combinaciones]
    Por evento: ninguno pendiente.
  T-2: los mismos que amlr
  T-3: los mismos que T-1
  T-4:
    Periódico:
      RD: desde el 2027-12-01, 36 meses → vence el 2030-12-01 (en_plazo)  [en 2 de 4 combinaciones]
      AMLR: desde el 2027-12-01, 36 meses → vence el 2030-12-01 (en_plazo)  [en 1 de 4 combinaciones]
      AMLR: desde el 2025-01-15, 60 meses → vence el 2030-01-15 (en_plazo)  [en 1 de 4 combinaciones]
      AMLR: desde el 2025-01-15, 36 meses → vence el 2028-01-15 (vencida)  [en 1 de 4 combinaciones]
    Por evento: ninguno pendiente.

Avisos:
  (T-1, T-3) Una revisión posterior a A cuenta con una norma y no con la otra, y cambia el periodo en curso: lecturas TR-1 (AMLR) y TR-2 (RD) (D-33).
```

Cómo leerlo:

- **Próxima revisión y estado.** Con el RD, en plazo hasta el 2030-12-01. Con el AMLR y con las cuatro lecturas de la transición, `indeterminado`: la respuesta depende de preguntas que la norma no resuelve.
- **Qué hay que decidir.** Es el producto. En T-1 y T-3 hay dos preguntas:
  - AC: ¿una revisión sin cambios cuenta como actualización para el AMLR?
  - TR: ¿qué norma decide si la revisión de diciembre de 2027 cierra el periodo del RD?

  Si la revisión sin cambios cuenta (AC-1), el cliente está en plazo, y no hace falta responder la otra. Si no cuenta y decide el AMLR (AC-2 y TR-1), nadie cuenta esa revisión: el cliente sigue en el periodo del RD que empezó en 2025 y venció el 2028-01-15. «Aún depende de» dice cuándo una respuesta no basta.
- **Componentes.** De dónde sale cada fecha: la norma, el ancla del periodo, los meses y en cuántas combinaciones de lecturas aparece.
- **Avisos.** Aquí, que una revisión posterior al 10 de julio de 2027 cuenta con una norma y no con la otra (D-33).

El código de salida es 1, porque los regímenes no coinciden y hay `indeterminado`.

## Instalación

Hace falta Python 3.11 o posterior (probado con 3.11, 3.12 y 3.14). No tiene dependencias externas: `pip install` solo descarga setuptools para construir el paquete. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install .
plazos-actualizacion corpus/07-revision-de-2027-que-ninguna-norma-cuenta.json
```

**Uso:** `plazos-actualizacion FICHERO [--json]`. Con `--json`, el mismo informe en JSON, con todas las fechas, todas las combinaciones de lecturas y las fechas en formato `AAAA-MM-DD`. En texto, más de tres fechas posibles se resumen como intervalo.

**Códigos de salida:**
- **0:** en la fecha de referencia, los seis regímenes dan el mismo estado y ninguno es `indeterminado`. Las fechas pueden diferir: el informe lo dice, el código no. En el corpus pasa en los casos 01 y 09.
- **1:** los regímenes dan estados distintos, o alguno es `indeterminado`.
- **2:** el fichero no se puede leer o la entrada no es válida. Los errores de validación salen con su código (`ERR-01` a `ERR-08`) y la ruta del dato.

**Con tu propio cliente.** La entrada es un JSON con:
- el manual de la entidad: la periodicidad para cada nivel de su escala de riesgo, el plazo para las revisiones por evento y si una revisión anticipada reinicia el plazo;
- la clasificación de riesgo del cliente, con cada norma por separado;
- las revisiones, con su tipo y su resultado;
- los eventos, con la fecha del hecho y la de su conocimiento.

El formato, con un ejemplo, está en [docs/modelo-datos.md](docs/modelo-datos.md). La entrada recoge hechos, no el régimen: el régimen es un parámetro del cálculo.

**El corpus.** Los nueve casos, con su tabla de estados, están en [corpus/README.md](corpus/README.md). Se regeneran con `python corpus/generar.py`, que comprueba cada caso contra su resultado esperado antes de escribirlo. Los resultados esperados están escritos a mano desde la especificación.

**Tests:** `pip install pytest` y `pytest` desde la raíz.

## Qué calcula

Para un cliente y una fecha de referencia, la fecha de la próxima revisión obligatoria y su estado en seis regímenes:

- **`ley_rd`:** la Ley 10/2010 y el RD 304/2014.
  - La periodicidad es la del manual, con un año como máximo para los clientes de riesgo superior al promedio (RD 11.2).
  - La revisión por evento se hace ante un cambio relevante en la actividad (RD 33.1.b) y, según la lectura, ante los supuestos de la Ley 7.2.
- **`amlr`:** el AMLR.
  - La periodicidad es un año para los clientes de riesgo elevado con medidas de la sección 4 y cinco años para los demás (art. 26.2).
  - La revisión por evento se hace por las letras a), b) y c) del art. 26.3, cada una con su fecha: el hecho, la obligación de contacto o el conocimiento.
- **`T-1` a `T-4`:** lo que se aplica según cómo se resuelva la transición del 10 de julio de 2027.
  - T-1: el periodo en curso termina con el RD.
  - T-2: el AMLR, desde la última revisión.
  - T-3: el AMLR desde el 10 de julio de 2027, sin pasar de la fecha del RD.
  - T-4: las dos normas a la vez; rige la fecha más temprana.

Los estados son `en_plazo`, `vencida`, `revision_pendiente_sin_plazo` (un evento exige revisar y nadie ha fijado cuándo), `sin_plazo` (el manual no fija periodicidad para el nivel del cliente), `relacion_terminada` e `indeterminado`.

Donde la norma no resuelve una pregunta, el cálculo da una lectura por cada respuesta: desde cuándo cuenta el primer periodo, si una revisión anticipada reinicia el plazo, si una revisión sin cambios es una actualización, qué exige el plazo de un año del AMLR, si manda el manual o el máximo legal, qué letra del art. 26.3 corresponde a cada evento, entre otras. Si las lecturas dan estados distintos, el estado es `indeterminado`, y la salida lo atribuye a las preguntas que lo causan. Las reglas completas, con las decisiones propias numeradas (D-1 a D-40) y su motivo, están en la [especificación del cálculo](docs/especificacion-calculo.md).

## Qué no hace

- **No dice qué lectura es la correcta.** Lo calcula todo y no elige. Por ejemplo: si una revisión anticipada reinicia el plazo, si una revisión sin cambios cuenta, qué rige para los clientes existentes el 10 de julio de 2027.
- **No clasifica clientes.** Usa la clasificación de riesgo que hizo la entidad, con cada norma. No evalúa factores de riesgo ni deduce una clasificación de otra.
- **No valora hechos.** Si un evento es relevante, si una revisión fue suficiente o a qué tipo corresponde un hecho lo afirma la entrada.
- **No revisa nada.** No obtiene información del cliente, no comprueba documentos ni cruza listas de sanciones (AMLR, art. 26.4).
- **No sigue las operaciones.** La vigilancia de operaciones y la detección de operaciones sospechosas quedan fuera.
- **No prevé hechos futuros.** Calcula con los hechos que constan en la entrada en la fecha de referencia.
- **No trata la sospecha de blanqueo ni las dudas sobre los datos** (Ley 7.1; AMLR 19.1.d y e), que obligan a aplicar de nuevo la diligencia debida y no a la revisión del art. 26.3.
- **No trata una cartera.** Calcula un cliente por fichero.

## Los diecisiete casos que la norma no resuelve

Al analizar los textos aparecieron diecisiete puntos en que el resultado no está determinado por un texto único:
- **Trece** vienen de la norma, entre ellos la transición del 10 de julio de 2027, el inicio del primer periodo, la revisión sin cambios, las dos poblaciones de riesgo alto del RD y del AMLR, las dos fechas de cada evento y el manual frente al máximo legal.
- **Tres** aparecieron al implementar la transición: eventos que ninguna norma, o las dos, activan en su propio periodo, y qué norma juzga una revisión posterior a esa fecha.
- **Uno** viene del modelo de datos: una clasificación a la que le falta un dato.
- **El reinicio del plazo tras una revisión anticipada** depende del borrador de la AMLA y está en una sección aparte, porque puede cambiar con las directrices finales. Es uno de los trece de la norma, y en la sección aparte se lista también en qué otros casos se cita el borrador.

Están en [docs/ambiguedades.md](docs/ambiguedades.md), cada uno con qué dice la norma, por qué no determina un comportamiento único, qué hace esta implementación, cómo se señala en la salida y a qué régimen afecta.

## Fuentes

| Documento | Versión |
|---|---|
| Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Texto consolidado, última modificación de 21 de marzo de 2026 |
| Real Decreto 304/2014, de 5 de mayo, Reglamento de la Ley 10/2010 | Texto consolidado, última modificación de 24 de abril de 2024 |
| Reglamento (UE) 2024/1624 (AMLR), de 31 de mayo de 2024 | Texto publicado en el DO L de 19 de junio de 2024, sin consolidar |
| AMLA, «Consultation Paper. Draft Guidelines on ongoing monitoring of a business relationship under Article 26(5) of Regulation (EU) 2024/1624» | **Borrador sometido a consulta, sin efecto normativo.** Fechado el 3 de junio de 2026; consulta cerrada el 3 de septiembre de 2026 |

La Ley, el RD y el AMLR se descargaron el 15 de septiembre de 2026, y el borrador de la AMLA el 21 de septiembre de 2026. Las URL y las huellas SHA-256 de cada versión están en [docs/fuentes/FUENTES.md](docs/fuentes/FUENTES.md). Los PDF no se redistribuyen.

El borrador de la AMLA se usa para construir lecturas del AMLR donde el texto no decide, nunca como norma y nunca para descartar una lectura. Cuando salgan las directrices finales habrá que actualizar el repositorio; el [ADR 0001](docs/adr/0001-calcular-seis-regimenes-y-atribuir.md) dice qué partes.

**Calendario.**
- **10 de julio de 2026:** fecha que fijaba el AMLR para las directrices de la AMLA. Art. 26.5: «A más tardar el 10 de julio de 2026, la ALBC emitirá directrices sobre las medidas de seguimiento continuo de las relaciones de negocios».
- **3 de junio a 3 de septiembre de 2026:** consulta pública del borrador.
- **Cuarto trimestre de 2026:** directrices finales esperadas, según el propio borrador (ap. 2.1: «final guidelines, that will be issued in Q4 2026»).
- **Hasta el 9 de julio de 2027:** se aplican la Ley 10/2010 y el RD 304/2014. La herramienta calcula también el AMLR, para comparar, y avisa de que todavía no es aplicable.
- **10 de julio de 2027:** el AMLR «será aplicable» (art. 90). Ningún texto dice qué pasa con los clientes que ya lo eran; de ahí T-1 a T-4.
- **10 de julio de 2029:** aplicación del AMLR a los agentes de fútbol y a los clubes de fútbol profesional (art. 90).

## Otros repositorios del proyecto

- [validador-cadena-verifactu](https://github.com/mshodai/validador-cadena-verifactu): comprueba la integridad de una cadena de registros de facturación de Verifactu.
- [calculo-titularidad-real](https://github.com/mshodai/calculo-titularidad-real): calcula la titularidad real bajo la Ley 10/2010 y el AMLR.
- [plazos-conservacion-pbc](https://github.com/mshodai/plazos-conservacion-pbc): calcula el estado de conservación de la documentación bajo la Ley 10/2010 y el AMLR.

## Licencia

MIT; el texto completo está en [LICENSE](LICENSE). Cubre el código y la documentación de este repositorio, no los documentos de `docs/fuentes/`, que no se incluyen.

---

Es una implementación de referencia, probada sobre datos sintéticos. No es software de cumplimiento normativo y no constituye asesoramiento jurídico.
