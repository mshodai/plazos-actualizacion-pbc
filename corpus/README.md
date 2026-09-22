# Corpus

Clientes sintéticos con su resultado esperado. Lo genera `corpus/generar.py`, que comprueba cada caso con el código de `src/` antes de escribirlo. No se edita a mano.

```
python corpus/generar.py
```

Cada caso tiene la entrada (`NN-nombre.json`, según `docs/modelo-datos.md`) y el resultado esperado (`NN-nombre.esperado.json`): en cada uno de los seis regímenes, el estado y las fechas de la próxima revisión en la fecha de referencia, las decisiones que hay que tomar para salir de cada `indeterminado` (con el estado y las fechas de cada respuesta y de qué depende aún), los eventos pendientes con sus bases y los códigos D-n de los avisos. Los resultados esperados están escritos a mano en `generar.py` a partir de `docs/especificacion-calculo.md`. El código de salida es el de `plazos-actualizacion` (§10.3): 1 si alguna lectura de algún régimen exige actuar (`vencida`, `revision_pendiente_sin_plazo` o `sin_plazo`); 0 si ninguna lo exige, aunque los regímenes discrepen (D-41).

| Caso | Referencia | ley_rd | amlr | T-1 | T-2 | T-3 | T-4 | Código |
|---|---|---|---|---|---|---|---|---|
| 01-mismo-resultado-en-los-seis | 2028-09-01 | en_plazo | en_plazo | en_plazo | en_plazo | en_plazo | en_plazo | 0 |
| 02-revision-sin-cambios-vencida-con-ac-2 | 2029-01-10 | en_plazo | indeterminado | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 03-cliente-existente-transicion-diverge | 2030-01-01 | en_plazo | vencida | en_plazo | vencida | en_plazo | vencida | 1 |
| 04-persona-del-medio-politico | 2029-06-01 | vencida | indeterminado | indeterminado | indeterminado | indeterminado | vencida | 1 |
| 05-revision-anticipada-puede-reiniciar | 2033-03-01 | indeterminado | indeterminado | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 06-evento-conocido-despues-del-10-de-julio-de-2027 | 2027-08-20 | indeterminado | en_plazo | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 07-revision-de-2027-que-ninguna-norma-cuenta | 2028-03-01 | en_plazo | indeterminado | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 08-falta-un-dato-de-clasificacion | 2021-06-01 | indeterminado | en_plazo | indeterminado | indeterminado | indeterminado | indeterminado | 1 |
| 09-relacion-terminada | 2026-01-01 | relacion_terminada | relacion_terminada | relacion_terminada | relacion_terminada | relacion_terminada | relacion_terminada | 0 |
| 10-vencida-en-los-seis | 2028-01-15 | vencida | vencida | vencida | vencida | vencida | vencida | 1 |

## Qué demuestra cada caso

**01-mismo-resultado-en-los-seis.** Cliente nuevo de riesgo alto, con los tres criterios de riesgo a true y un manual de 12 meses, revisado al darse de alta el 2028-02-01. Con el RD, el manual (12 meses, que es el mínimo anual del art. 11.2); con el AMLR, el año del art. 26.2.a. Los seis regímenes dan en_plazo con la misma fecha, el 2029-02-01, y no hay ninguna lectura que decidir: código 0.

**02-revision-sin-cambios-vencida-con-ac-2.** Cliente de riesgo alto dado de alta el 2027-09-01, revisado a tiempo el 2028-08-20 sin encontrar cambios, a fecha 2029-01-10. Con el RD la revisión cuenta y vence el 2029-08-20: en_plazo. Con el AMLR depende de AC: si una revisión sin cambios es una «actualización» (AC-1), en_plazo; si no (AC-2), el periodo cuenta desde la inicial y está vencido desde el 2028-09-02, aunque la entidad revisó a tiempo (S-6, §2.3).

**03-cliente-existente-transicion-diverge.** Cliente de riesgo bajo desde el 2012-02-01, con un manual de 120 meses por medidas simplificadas y la última revisión el 2024-01-15, calificado con el AMLR el 2027-07-10; a fecha 2030-01-01. Con el RD vence el 2034-01-15; con el AMLR, el 2029-01-15, porque el manual no puede superar cinco años (D-17). Las cuatro lecturas de la transición se separan: T-1 mantiene el RD (en_plazo), T-2 y T-4 aplican el AMLR (vencida) y T-3 cuenta cinco años desde el 2027-07-10 (en_plazo hasta el 2032-07-10).

**04-persona-del-medio-politico.** Persona del medio político, cliente desde el 2028-03-01: la entidad la considera de riesgo superior al promedio con el RD, le aplica medidas de la sección 4 del AMLR (art. 42), pero no la considera de riesgo elevado. A fecha 2029-06-01, con el RD rige el plazo anual y está vencida desde el 2029-03-02. Con el AMLR depende de si el art. 26.2.a exige los dos elementos (PB-1: cinco años, en_plazo) o basta uno (PB-2: un año, vencida) (S-4). T-4, que aplica también el RD, da vencida.

**05-revision-anticipada-puede-reiniciar.** Cliente de riesgo medio desde el 2028-01-10, con un manual de 60 meses que no dice si una revisión anticipada reinicia el plazo. Un cambio de titularidad provoca una revisión el 2029-06-15. A fecha 2033-03-01, el «can reset» del borrador de la AMLA decide el estado en los seis regímenes: si la revisión reinicia el plazo (RA-1), vence el 2034-06-15; si no (RA-2), venció el 2033-01-10; si lo decide el manual (RA-3), como el manual calla, las dos cosas (S-3, D-10).

**06-evento-conocido-despues-del-10-de-julio-de-2027.** Cliente de riesgo medio desde el 2020-01-10. Una información de riesgo ocurre el 2027-06-01 y la entidad la conoce el 2027-08-01: el hecho y el conocimiento caen a distinto lado del 2027-07-10. El manual da 30 días para revisar tras un evento. A fecha 2027-08-20, con el AMLR (letra c, desde el conocimiento) la revisión vence el 2027-08-31: en_plazo. Con la Ley 7.2, si se aplica a este cliente (L72-2) y la información es un cambio de circunstancias (LC-2), cuenta desde el hecho y venció el 2027-07-01. En T-1 a T-3 las dos normas lo activan en su propio periodo, y además hay que decidir cuál rige (TD, D-32).

**07-revision-de-2027-que-ninguna-norma-cuenta.** Cliente de riesgo medio desde el 2020-01-10, manual de 36 meses, revisado el 2025-01-15 y otra vez el 2027-12-01 sin encontrar cambios; a fecha 2028-03-01. Con el RD la revisión de 2027 cuenta y vence el 2030-12-01. En T-1 y T-3, si una revisión sin cambios no es una actualización (AC-2) y la juzga el AMLR por ser posterior al 2027-07-10 (TR-1), no cuenta para ninguna norma: el cliente sigue en el periodo del RD de 2025, que venció el 2028-01-15. Si la juzga el RD (TR-2), cierra ese periodo y está en plazo (D-33).

**08-falta-un-dato-de-clasificacion.** Cliente desde el 2020-01-10 cuya clasificación no dice si su riesgo es superior al promedio (`superior_al_promedio = null`); a fecha 2021-06-01. Con el RD, si lo es, rige el plazo anual y está vencido; si no, los 36 meses del manual. La salida no plantea una lectura de la norma sino un dato que falta: «¿lo es?». Se sale del indeterminado completando la entrada (D-15, D-36). Con SP-1, además, el manual de 36 meses supera el mínimo anual y se recorta a 12, con aviso (D-14). El AMLR no usa ese dato.

**09-relacion-terminada.** Cliente de riesgo medio con la relación terminada el 2025-06-01, a fecha 2026-01-01. No hay próxima revisión en ningún régimen: relacion_terminada, sin fecha (D-22). El aviso recuerda que el día de la terminación la revisión ya estaba vencida. Los seis coinciden: código 0.

**10-vencida-en-los-seis.** Cliente de riesgo medio desde el 2020-03-02, con un manual de 36 meses y revisado solo al darse de alta; a fecha 2028-01-15. Con el RD venció el 2023-03-02; con el AMLR, el 2025-03-02 (PM-1) o el 2023-03-02 (PM-2). Los seis regímenes dan vencida: coinciden en el estado, pero hay que revisar al cliente. Código 1, porque alguna lectura exige actuar (D-41); con el criterio anterior, retirado (D-38), daba 0.
