---
title: "¿Una revisión sin cambios reinicia el plazo del AMLR?"
description: "El AMLR fija un máximo entre las «actualizaciones» de la información del cliente; el RD 304/2014 habla de «procesos de revisión». Si una revisión que no cambia nada no es una actualización, un cliente revisado a tiempo sale vencido. Qué dicen los textos, qué dice el borrador de la AMLA y qué debería hacer una herramienta de cálculo."
---

# Revisar no es actualizar: el plazo del AMLR y la revisión que no cambia nada

Un sujeto obligado por la normativa de prevención del blanqueo de capitales tiene un cliente de riesgo alto desde el 1 de septiembre de 2027. Su manual fija una revisión anual. El 20 de agosto de 2028, antes de que venza el año, la entidad revisa la información del cliente y comprueba que todo sigue igual: el mismo titular real, la misma actividad, los mismos datos. No cambia nada. El 10 de enero de 2029, alguien mira el calendario y se pregunta:

**¿La próxima revisión vence el 20 de agosto de 2029, o el cliente está vencido desde septiembre de 2028?**

La respuesta depende de una palabra.

## Lo que dicen los textos

El Reglamento (UE) 2024/1624 (AMLR), aplicable desde el 10 de julio de 2027 (art. 90: «Será aplicable a partir del 10 de julio de 2027»), regula el plazo en su art. 26.2. El primer párrafo fija la obligación: «las entidades obligadas velarán por que los documentos, los datos o la información pertinentes del cliente se mantengan actualizados». El segundo, el plazo: «El período entre las actualizaciones dela información del cliente conforme al párrafo primero dependerá del riesgo que plantea la relación de negocios y no será en ningún caso superior a: a) un año, en el caso de los clientes de riesgo elevado a los que se aplican las medidas de la sección 4 del presente capítulo; b) cinco años, en el caso de todos los demás clientes». («Dela» es una errata del texto publicado).

El plazo se mide entre **actualizaciones**. Y el propio artículo distingue actualizar de revisar. El apartado 3, sobre las revisiones por eventos, dice que las entidades «revisarán y, cuando proceda, actualizarán la información del cliente».

El Real Decreto 304/2014, que se aplica hasta esa fecha, usa otra palabra. Su art. 11.2 dice: «Los sujetos obligados realizarán periódicamente procesos de revisión con objeto de asegurar que los documentos, datos e informaciones obtenidos como consecuencia de la aplicación de las medidas de debida diligencia se mantengan actualizados y se encuentren vigentes». Y fija la periodicidad de esos procesos: «El manual a que se refiere el artículo 33 determinará, en función del riesgo, la periodicidad de los procesos de revisión documental que para los clientes de riesgo superior al promedio será, como mínimo, anual».

El RD cuenta **revisiones**. El AMLR cuenta **actualizaciones**.

## La pregunta

Una revisión que confirma que nada ha cambiado, ¿es una actualización?

Con el RD no hay duda: es un «proceso de revisión», y cuenta. La revisión del 20 de agosto de 2028 abre un nuevo periodo, que vence el 20 de agosto de 2029.

Con el AMLR caben dos lecturas:

- **Sí es una actualización.** Después de la revisión, la información está comprobada a esa fecha, y eso es tenerla «actualizada». El considerando 70 del AMLR admite la confirmación del cliente como forma de cumplir la diligencia debida: puede hacerse «obteniendo una confirmación del cliente de que la información y los documentos conservados en los registros no han cambiado». Pero habla de clientes recurrentes y de la diligencia debida, no del plazo del art. 26.2.
- **No es una actualización.** El art. 26.2 mide el plazo entre actualizaciones («El período entre las actualizaciones»), y el art. 26.3 separa revisar de actualizar «cuando proceda». Si no procedía actualizar nada, no hubo actualización, y el periodo sigue contando desde la anterior.

La segunda lectura tiene una consecuencia incómoda, pero sale de la letra. En el ejemplo, la última actualización es la diligencia debida inicial, del 1 de septiembre de 2027. El año venció el 1 de septiembre de 2028, y el cliente está vencido desde el día siguiente, **aunque la entidad lo revisó a tiempo**. Un cliente cuya información no cambia nunca estaría siempre vencido.

Es el [caso 02 del corpus](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/corpus/02-revision-sin-cambios-vencida-con-ac-2.json) ([resultado esperado](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/corpus/02-revision-sin-cambios-vencida-con-ac-2.esperado.json)), con datos sintéticos:

```
$ plazos-actualizacion corpus/02-revision-sin-cambios-vencida-con-ac-2.json
Cliente CLI-FICTICIO-02
Fecha de referencia: 2029-01-10 · AMLR aplicable desde el 2027-07-10
[…]
Próxima revisión y estado el 2029-01-10:
  ley_rd  2029-08-20               en_plazo
  amlr    2028-09-01 o 2029-08-20  indeterminado
[…]
Qué hay que decidir para salir del indeterminado (D-30, D-36):
  amlr:
    AC — ¿Una revisión sin cambios cuenta como actualización para el AMLR? (S-6, §2.3)
      AC-1 (sí cuenta): en_plazo, 2029-08-20
      AC-2 (no cuenta): vencida, 2028-09-01
      Datos: cliente.revisiones[1] (REV-FICTICIO-2)
[…]
```

Con el RD, en plazo hasta el 20 de agosto de 2029. Con el AMLR, `indeterminado`: con AC-1 en plazo y con AC-2 vencida desde el 2 de septiembre de 2028. La pregunta que decide es una sola, y la salida la nombra.

## La transición lo agrava

El caso anterior es un cliente nuevo, que solo ha conocido el AMLR. Con un cliente que ya lo era el 10 de julio de 2027 aparece otra pregunta, porque ningún texto dice qué norma juzga una revisión hecha después de esa fecha dentro de un periodo que empezó con el RD. El AMLR no tiene ninguna disposición transitoria sobre el seguimiento continuo, y la Ley 10/2010, consolidada a 21 de marzo de 2026, no tiene ninguna adaptación.

El [caso 07 del corpus](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/corpus/07-revision-de-2027-que-ninguna-norma-cuenta.json) ([resultado esperado](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/corpus/07-revision-de-2027-que-ninguna-norma-cuenta.esperado.json)) es un cliente de riesgo medio desde 2020, con un manual de 36 meses. Se revisó el 15 de enero de 2025 y otra vez el 1 de diciembre de 2027, sin encontrar cambios.

Con el RD, la revisión de diciembre cuenta y la próxima vence el 1 de diciembre de 2030. Pero para una de las lecturas de la transición, T-1, el periodo en curso el 10 de julio de 2027 termina con el RD, y la primera revisión que cuenta después de esa fecha lo cierra y abre uno del AMLR. La revisión de diciembre es posterior a esa fecha. Si la juzga el AMLR y una revisión sin cambios no es una actualización, no abre el periodo del AMLR. Y como es posterior al 10 de julio de 2027, tampoco entra en el periodo del RD, que solo cuenta las revisiones anteriores. **Ninguna norma la cuenta.** El cliente sigue en el periodo del RD que empezó en enero de 2025, y ese periodo venció el 15 de enero de 2028. En marzo de 2028, el cliente está vencido desde hace mes y medio. Lo revisaron hace tres meses.

```
$ plazos-actualizacion corpus/07-revision-de-2027-que-ninguna-norma-cuenta.json
[…]
  T-1:
    AC — ¿Una revisión sin cambios cuenta como actualización para el AMLR? (S-6, §2.3)
      AC-1 (sí cuenta): en_plazo, 2030-12-01 o 2032-12-01
      AC-2 (no cuenta): vencida o en_plazo, 2028-01-15 o 2030-12-01 o 2032-12-01; aún depende de TR
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
    TR — ¿Qué norma decide si una revisión posterior a A cierra el periodo del RD? (S-16, D-33, §5.2)
      TR-1 (el AMLR): en_plazo o vencida, 2028-01-15 o 2030-12-01 o 2032-12-01; aún depende de AC
      TR-2 (el RD, mientras dura su periodo): en_plazo, 2030-12-01 o 2032-12-01
      Datos: cliente.revisiones[2] (REV-FICTICIO-3)
[…]
```

Aquí hay dos preguntas y dependen una de otra. Si la revisión sin cambios cuenta (AC-1), no hace falta responder la segunda: el cliente está en plazo. Si no cuenta (AC-2), el resultado depende de qué norma juzga la revisión (TR). Solo la combinación de AC-2 con TR-1 da el vencimiento del 15 de enero de 2028.

## Lo que dice el borrador de la AMLA

El art. 26.5 del AMLR encarga a la Autoridad de Lucha contra el Blanqueo de Capitales (AMLA; «ALBC» en la versión española) directrices sobre el seguimiento continuo. En septiembre de 2026 solo existe **un borrador sometido a consulta, sin efecto normativo**: el «Consultation Paper. Draft Guidelines on ongoing monitoring of a business relationship under Article 26(5) of Regulation (EU) 2024/1624», de 3 de junio de 2026, publicado solo en inglés. La consulta se cerró el 3 de septiembre de 2026, y la AMLA anuncia las directrices finales para el cuarto trimestre (ap. 2.1: «final guidelines, that will be issued in Q4 2026»).

**El borrador no resuelve la pregunta.** No dice en ningún apartado si una revisión que no cambia nada es una actualización a efectos del plazo del art. 26.2. Lo que sí dice, con la traducción propia entre corchetes:

- **Trata la confirmación del cliente como forma de actualizar.** Ap. 12: «Customer information should be updated by using: [...] c) Information or confirmation provided directly by the customer» [la información del cliente debe actualizarse mediante: [...] c) información o confirmación facilitada directamente por el cliente]. Ap. 14: «where a customer provides a written statement with new information or confirms previously collected information, documents, or data, obliged entities should, depending on the level and nature of the risk, consider whether the reliability of that statement needs to be verified» [cuando el cliente aporta información nueva o confirma la ya recogida, las entidades deben valorar, según el riesgo, si hay que verificar esa declaración].
- **Admite revisiones periódicas de menor alcance cuando nada ha cambiado.** Ap. 19: «Periodic reviews must always be conducted in accordance with Article 26(2) of AMLR. However, the depth and intensity of such reviews should follow a risk-based approach» [las revisiones periódicas deben hacerse siempre conforme al art. 26.2; su profundidad debe seguir un enfoque basado en el riesgo]. Ap. 20: una de las consideraciones es que «no new activity has occurred since the last customer information update» [no ha habido actividad nueva desde la última actualización de la información del cliente].
- **Dice que una revisión anticipada «puede» reiniciar el plazo.** Ap. 2: «If a review is carried out earlier than scheduled, this can reset the timeline for the next required update» [si una revisión se hace antes de lo previsto, puede reiniciar el plazo de la siguiente actualización].

Los apartados 12 y 14 apuntan a que confirmar la información es una manera de actualizarla. Los apartados 19 y 20 tratan como revisión periódica del art. 26.2 una revisión que puede no cambiar nada. Pero ninguno dice que esa revisión abra un nuevo periodo. Y el apartado 2, el único que habla del plazo siguiente, dice «can reset», no «resets». Son indicios de un borrador, no una respuesta. Por eso la herramienta mantiene las dos lecturas, y el caso se documenta en [ambiguedades.md, S-6](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/docs/ambiguedades.md#s-6). El «can reset» es otro caso, S-3, que depende solo del borrador y tiene su propia sección.

## La lección: cuatro decisiones que tomaba el orden de las condiciones

La lectura TR del caso 07 no estaba en la primera versión del cálculo. La primera versión decidía, en las lecturas T-1 y T-3, si una revisión posterior al 10 de julio de 2027 cerraba el periodo del RD contando con las reglas del AMLR. No lo decía en ningún sitio: era el orden en que el código comprobaba las condiciones. Al revisar la lógica de transición buscando todos los puntos donde el orden entre las dos normas decidía el resultado, aparecieron cuatro. Todas eran decisiones jurídicas:

1. **Un evento que ninguna norma activa en su propio periodo.** Un cambio de actividad ocurrido antes del 10 de julio de 2027 y conocido después: el RD, leyendo «cuando se verifique» (art. 33.1.b) en el sentido de comprobarse, lo activa después de esa fecha, cuando ya no rige, si además la Ley 7.2 no se aplica a ese cliente. El AMLR, por la letra a) del art. 26.3 («se produzca un cambio»), lo activa antes, cuando aún no regía. El código comprobaba primero una norma y luego la otra; ninguna condición se cumplía, y el evento **desaparecía sin aviso**. Ahora hay tres lecturas: el RD en su fecha, el AMLR desde el 10 de julio de 2027 o ninguna (D-31).
2. **Un evento que las dos normas activan en su propio periodo.** Una información de riesgo ocurrida antes de esa fecha y conocida después: la Ley 10/2010, art. 7.2 («cambien las circunstancias del cliente»), la activa en la fecha del hecho si se aplica al cliente y la información se considera un cambio de circunstancias; el AMLR, por la letra c) («entren en conocimiento de un hecho relevante»), en la del conocimiento. Las dos condiciones se cumplían, y **ganaba el RD porque se comprobaba primero**. Ahora hay dos lecturas (D-32).
3. **Qué norma juzga una revisión posterior al 10 de julio de 2027.** Es la del caso 07. El código usaba las reglas del AMLR, sin que ningún texto lo dijera. Ahora hay dos lecturas: el AMLR o el RD mientras dura su periodo (D-33).
4. **Los empates.** Cuando el RD y el AMLR daban la misma fecha límite, el informe atribuía el plazo al RD, porque era el primero en la comparación. Cuando dos supuestos activaban un evento el mismo día, el informe daba uno, elegido por el orden alfabético de su nombre. No cambiaba ni la fecha ni el estado, solo lo que se informaba. Aquí no hacían falta lecturas sino una regla escrita: los empates se informan todos (D-34).

Las tres primeras cambian el estado del cliente. Ninguna estaba escrita en la especificación, y ninguna habría aparecido en la salida: el resultado habría sido una fecha limpia, sin rastro de que había una elección detrás. **Las cuatro aparecieron al revisar la lógica de transición buscando expresamente dónde decidía el orden de comprobación.** No las encontraron los tests, que comprobaban lo que la especificación decía, ni los ejemplos, que no pasaban por esas combinaciones.

## Qué hace la herramienta

[plazos-actualizacion-pbc](https://github.com/mshodai/plazos-actualizacion-pbc) calcula la fecha de la próxima revisión obligatoria de la información de un cliente, en una fecha dada, en seis regímenes:
- el RD 304/2014;
- el AMLR;
- cuatro lecturas de la transición del 10 de julio de 2027.

Donde la norma no resuelve una pregunta, calcula una lectura por cada respuesta. Si las lecturas dan estados distintos, el régimen da `indeterminado`. Luego atribuye el `indeterminado` a las preguntas que lo causan: una pregunta lo causa si, en alguna combinación de las demás respuestas, cambiar solo la suya cambia el estado (D-30). El informe presenta esas preguntas como decisiones:
- el texto de la pregunta, con su referencia;
- el estado y las fechas que da cada respuesta;
- si con esa respuesta basta o el resultado aún depende de otra pregunta;
- qué dato de la entrada pone la pregunta en juego.

No elige. Quien tiene que decidir sabe qué decide y qué pasa con cada opción.

Las preguntas que la norma deja abiertas, diecisiete en total, están en [docs/ambiguedades.md](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/docs/ambiguedades.md). Cada una lleva qué dice la norma, por qué no determina un comportamiento único, qué hace la implementación y cómo se señala en la salida. Las que dependen del borrador de la AMLA están aparte, porque pueden cambiar con las directrices finales.

## La consecuencia general

Una herramienta que devuelve «próxima revisión: 20 de agosto de 2029» para el cliente del caso 02 ha decidido que una revisión sin cambios es una actualización. Una que devuelve «vencida» ha decidido lo contrario. Las dos decisiones son defendibles, y ninguna la toma un texto.

**Una herramienta que devuelve una sola fecha está respondiendo preguntas jurídicas sin decir cuáles.** Y no todas están a la vista en la especificación: algunas las responde el orden en que el código comprueba las condiciones. La alternativa es que la herramienta calcule todas las respuestas que los textos permiten, diga de qué artículo sale cada una y convierta cada `indeterminado` en las preguntas que hay que responder. La decisión sigue siendo necesaria, pero la toma quien responde de ella, sabiendo que la está tomando.

---

El código, la especificación, el corpus y las fuentes con su versión y su huella están en [github.com/mshodai/plazos-actualizacion-pbc](https://github.com/mshodai/plazos-actualizacion-pbc). Las citas del AMLR son del texto publicado en el DO L de 19.6.2024; las del RD 304/2014, de su texto consolidado con última modificación de 24 de abril de 2024; las del borrador de la AMLA, del documento de consulta de 3 de junio de 2026 ([docs/fuentes/FUENTES.md](https://github.com/mshodai/plazos-actualizacion-pbc/blob/main/docs/fuentes/FUENTES.md)).

Este artículo es un análisis de la arquitectura de una herramienta de cálculo, no asesoramiento jurídico.
