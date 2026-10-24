# Empieza aquí

*[Read in English](START.md)*

No hace falta saber programar. Esto prepara un registro privado de algo de tu vida (un
vehículo, un negocio nuevo, tu carrera, un proyecto) que un asistente de IA mantiene al
día contigo: los datos importantes, los papeles y los plazos.

**Necesitas:** [Claude Code](https://claude.com/claude-code) instalado y con la sesión
iniciada en tu propia cuenta de Claude, y una cuenta gratuita de
[GitHub](https://github.com/signup).

**Después:** abre Claude Code, copia el mensaje de abajo (el botón de copiar está en su
esquina superior derecha), pégalo y responde a sus preguntas. Pregunta una cosa cada vez,
y no se guarda nada hasta que hayas decidido qué no debe entrar nunca. Tu registro es
privado salvo que tú decidas lo contrario.

```text
Quiero que lleves un registro privado de algo de mi vida —qué es, todo lo importante
sobre ello, sus papeles y sus plazos— y que lo mantengas al día conmigo a partir de ahora.
No sé programar: haz tú los pasos técnicos, explícame cada uno con palabras sencillas y
pregúntame antes de hacer cualquier cosa que no se pueda deshacer. Háblame en español.

1. Empieza entrevistándome, una pregunta cada vez: de qué trata este registro, qué quiero
   que haga por mí, a quién le envío documentos alguna vez y qué fechas me cuestan dinero
   o problemas si se me pasan. No supongas nada; si no lo tengo claro, dame ejemplos y deja que elija.
2. Comprueba que git, Python 3 y la herramienta de GitHub (gh) están instalados. Instala lo
   que falte, o dime exactamente dónde hacer clic. Si gh no tiene la sesión iniciada, haz
   que lo ejecute yo: `gh auth login`. Nunca me pidas una contraseña ni un token.
3. Instala el plugin que sabe construir esto:
   claude plugin install system-of-record --marketplace alvaro-francisco-gil/agent-record
   (versión 1.3.0 o posterior). Si sus skills no aparecen, dime que reinicie Claude y que
   vuelva a pegar este mensaje; seguirás donde lo dejamos.
4. Después usa su skill bootstrapping-a-system-of-record, en una carpeta nueva dentro de
   mi carpeta personal con el nombre de lo que vamos a registrar. Síguela al pie de la
   letra, aprovechando lo que ya te he contado: no se guarda nada en el historial hasta
   que hayamos acordado qué no debe entrar nunca, solo añade las herramientas que mis
   respuestas justifiquen, y el repositorio de GitHub es privado salvo que yo diga lo
   contrario.
5. Nunca te inventes una fecha, una cantidad ni un dato. Márcalo como desconocido y
   pregúntame.
6. Cuando termines, dime en tres líneas cortas: dónde está el registro, cómo pedirte que
   añadas algo y qué tengo próximamente en la agenda.
```

Qué construye y por qué está explicado en el [README](README.md) (en inglés).
