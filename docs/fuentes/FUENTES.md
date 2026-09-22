# Fuentes

Documentos que usa el proyecto. Los PDF no se redistribuyen (están en `.gitignore`), así que cada uno debe descargarse de su URL y guardarse en `docs/fuentes/` con el nombre indicado.

Hay dos grupos:

- **Normativa** (Ley 10/2010, RD 304/2014 y AMLR): la que aplica el cálculo. Estas copias proceden del proyecto `plazos-conservacion-pbc` (`docs/fuentes/`), que a su vez las tomó de `calculo-titularidad-real`. Su SHA-256 coincide con el que figura en el `FUENTES.md` de `plazos-conservacion-pbc` para los mismos ficheros, así que son la misma versión.
- **Borrador de directrices de la AMLA** sobre el seguimiento continuo (art. 26.5 del AMLR). **No es norma.** Es un documento sometido a consulta pública, sin efecto normativo: ni obliga a las entidades ni vincula a los supervisores. Se usa solo para documentar cómo propone la AMLA leer el art. 26 del AMLR en los casos que el texto no resuelve, y siempre se cita como borrador. Se descargó directamente para este repositorio.

**Qué significa cada columna:**

- **Autor.** Órgano emisor, tal como figura en la cabecera del documento. Entre paréntesis, el editor del PDF según sus metadatos (`pdfinfo`).
- **Versión o fecha declarada.** Copiada literalmente del documento.
- **Fecha de descarga.**
  - En la normativa, es la de la descarga original en `calculo-titularidad-real`, tal como la recoge el `FUENTES.md` de `plazos-conservacion-pbc`. Las copias de este repositorio se crearon el 2026-09-21 al copiarlas.
  - En el borrador de la AMLA, es la fecha de creación del fichero (2026-09-21). Los metadatos de origen de macOS (`kMDItemWhereFroms`) solo guardan `https://www.amla.europa.eu/`, no la URL completa.
- **URL.**
  - En la normativa, se copian de `plazos-conservacion-pbc`, donde se explica cómo se obtuvieron y cuáles se comprobaron. Resumen: las del BOE devolvieron allí un fichero idéntico al local; la de EUR-Lex **no se ha podido comprobar**. En este repositorio no se han vuelto a comprobar.
  - En el borrador de la AMLA, se da la página de la consulta y el enlace de descarga que figura en ella. Se comprobó el 2026-09-21: la página responde `200`, y el PDF descargado con `curl` desde ese enlace tiene el mismo SHA-256 que la copia local.

## Documentos

| Fichero | Título | Autor | Versión o fecha declarada | Descarga | URL |
|---|---|---|---|---|---|
| `BOE-A-2010-6737-consolidado.pdf` | Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Jefatura del Estado (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 21 de marzo de 2026». Original: «BOE» núm. 103, de 29 de abril de 2010 | 2026-09-15 | https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2010-6737 |
| `BOE-A-2014-4742-consolidado.pdf` | Real Decreto 304/2014, de 5 de mayo, por el que se aprueba el Reglamento de la Ley 10/2010, de 28 de abril, de prevención del blanqueo de capitales y de la financiación del terrorismo | Ministerio de Economía y Competitividad (Agencia Estatal Boletín Oficial del Estado) | Texto consolidado. «Última modificación: 24 de abril de 2024». Original: «BOE» núm. 110, de 06 de mayo de 2014 | 2026-09-15 | https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf · ficha: https://www.boe.es/buscar/act.php?id=BOE-A-2014-4742 |
| `OJ_L_202401624_ES_TXT.pdf` | Reglamento (UE) 2024/1624 del Parlamento Europeo y del Consejo, de 31 de mayo de 2024, relativo a la prevención de la utilización del sistema financiero para el blanqueo de capitales o la financiación del terrorismo (AMLR) | Parlamento Europeo y Consejo (Oficina de Publicaciones de la Unión Europea) | Texto publicado, no consolidado: «DO L de 19.6.2024». No declara fecha de modificación. Art. 90: aplicable a partir del 10 de julio de 2027 (10 de julio de 2029 para las entidades del art. 3, punto 3, letras n) y o)) | 2026-09-15 | https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624 (comprobado el 22/09/2026 por descarga) · ELI impreso en el documento: http://data.europa.eu/eli/reg/2024/1624/oj |
| `AMLA-CP-Art26-5-AMLR.pdf` | «Consultation Paper. Draft Guidelines on ongoing monitoring of a business relationship under Article 26(5) of Regulation (EU) 2024/1624» (documento de consulta sobre el proyecto de directrices de seguimiento continuo de la relación de negocios del art. 26.5 del AMLR). Solo en inglés | Autoridad de Lucha contra el Blanqueo de Capitales y la Financiación del Terrorismo (AMLA; «ALBC» en la versión española del AMLR) (metadatos: autor personal de la AMLA, generado con Microsoft Word for Microsoft 365) | **Borrador sometido a consulta, sin efecto normativo.** «Frankfurt am Main – 3 June 2026». Plazo de respuesta: «by 03.09.2026»; la página de la consulta la da por cerrada («Status: Closed», «Deadline: 3 September 2026, 23:59 (CEST)»). Apartado 2.1: «final guidelines, that will be issued in Q4 2026». Las directrices finales se esperan, por tanto, en el cuarto trimestre de 2026; no estaban publicadas en la fecha de descarga | 2026-09-21 | Página de la consulta: https://www.amla.europa.eu/policy/public-consultations/consultation-draft-guidelines-ongoing-monitoring-business-relationship_en · descarga: https://www.amla.europa.eu/document/download/46b50078-08ed-4ab1-aea0-28b1a6085755_en?filename=Consultation%20Paper%20-%20Article%2026%285%29%20AMLR.pdf |

**Plazo del mandato.** El AMLR, art. 26.5, fijaba: «A más tardar el 10 de julio de 2026, la ALBC emitirá directrices sobre las medidas de seguimiento continuo de las relaciones de negocios y sobre el seguimiento de las operaciones ejecutadas en el contexto de dicha relación». En la fecha de descarga solo existe este borrador. Cuando se publiquen las directrices finales, habrá que añadirlas aquí como documento distinto y revisar lo que el proyecto toma del borrador.

## Huellas SHA-256

Sirven para comprobar que una copia local es la misma versión con la que se hizo el análisis. El BOE y EUR-Lex regeneran los PDF cuando cambia el texto consolidado, así que una huella distinta indica una versión distinta. En el borrador de la AMLA, una huella distinta puede indicar que la AMLA ha sustituido el fichero de la consulta.

```
4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d  BOE-A-2010-6737-consolidado.pdf
59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d  BOE-A-2014-4742-consolidado.pdf
666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974  OJ_L_202401624_ES_TXT.pdf
affb9871346a5f33947cf818e2e8199083007d383da87a2c1b7ee4c6ea52d7bb  AMLA-CP-Art26-5-AMLR.pdf
```

Para comprobarlas: `cd docs/fuentes && shasum -a 256 -c` pegando el bloque anterior en la entrada estándar.

## Datos para la vigilancia automática

Repite en formato legible por máquina el fichero, la URL de descarga y la huella SHA-256 de cada documento de las secciones anteriores. Lo lee el script de `vigilancia-fuentes`, que comprueba que coincida con el texto. Si difieren, prevalece el texto.

En los borradores, `paginas` recoge sus páginas oficiales, donde se anunciarían las directrices finales. Para cada página se guardan las frases sobre directrices finales y los enlaces de descarga que ofrecía el 2026-09-22. El script avisa si aparece otra frase u otra descarga.

```json
{
  "documentos": [
    {
      "fichero": "BOE-A-2010-6737-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2010/BOE-A-2010-6737-consolidado.pdf",
      "sha256": "4782a40bcf44165a97bc361520fd2b348acf7efbdfaa0a8d876c58332ff8601d"
    },
    {
      "fichero": "BOE-A-2014-4742-consolidado.pdf",
      "url": "https://www.boe.es/buscar/pdf/2014/BOE-A-2014-4742-consolidado.pdf",
      "sha256": "59d7be80313780a8cf48e1f3f87b5bd2860855a126472c0374e1c30c7fc19f0d"
    },
    {
      "fichero": "OJ_L_202401624_ES_TXT.pdf",
      "url": "https://eur-lex.europa.eu/legal-content/ES/TXT/PDF/?uri=OJ:L_202401624",
      "sha256": "666f18e1b5d4dd6bb7e927328bd8d84420d0919e692288f0b917c357df690974"
    },
    {
      "fichero": "AMLA-CP-Art26-5-AMLR.pdf",
      "url": "https://www.amla.europa.eu/document/download/46b50078-08ed-4ab1-aea0-28b1a6085755_en?filename=Consultation%20Paper%20-%20Article%2026%285%29%20AMLR.pdf",
      "sha256": "affb9871346a5f33947cf818e2e8199083007d383da87a2c1b7ee4c6ea52d7bb",
      "borrador": {
        "paginas": [
          {
            "url": "https://www.amla.europa.eu/policy/public-consultations/consultation-draft-guidelines-ongoing-monitoring-business-relationship_en",
            "menciones_conocidas": [],
            "descargas_conocidas": [
              "https://www.amla.europa.eu/document/download/6c232832-524a-4c54-a865-e74889e6561d_en",
              "https://www.amla.europa.eu/document/download/7538f893-c14c-4936-8c4b-c413c8743f6a_en",
              "https://www.amla.europa.eu/document/download/46b50078-08ed-4ab1-aea0-28b1a6085755_en"
            ]
          }
        ]
      }
    }
  ]
}
```
