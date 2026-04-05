# EFRD v4.0: Sistema de Gobernanza Algorítmica y Red de Seguridad Dinámica

## Filosofía del Sistema: El Estado como Código Abierto

El **Protocolo EFRD (Equilibrio Fiscal y Resiliencia Distributiva)** no es una reforma fiscal; es una sustitución del motor burocrático por uno matemático. Su objetivo es eliminar la arbitrariedad política y el "error de salto" del IRPF tradicional, garantizando que el sistema sea siempre **solvente** (no gasta lo que no recauda) y **digno** (nadie vive bajo el umbral de supervivencia).

## Los Pilares del Suelo Vitalicio ($k$)
A diferencia de otros subsidios, este sistema parte de una base de dignidad y lo expande según las circunstancias del ciudadano.

### La Semilla: Sueldo Vitalicio Base ($k_{base}$)
Se calcula dinámicamente según la capacidad real del país,**no según promesas electorales**:

$$k_{base} = \alpha \cdot \left( \frac{Y}{N} \cdot (1 - G) \right) \cdot \pi$$

El $k_{base}$ es el valor de referencia para un individuo solo ($\phi=1$) en un entorno neutro ($\gamma=1$).

### La Expansión: Umbral Protegido del Hogar ($k_{hogar}$)
El sistema reconoce que no cuesta lo mismo vivir en una gran capital que en un pueblo, ni vivir solo que en familia. **No se suma el $k_{base}$ a la ayuda; el $k_{base}$ se transforma en el $k_{hogar}$**:

$$k_{hogar} = k_{base} \cdot \phi \cdot \gamma$$

- **$\phi$ (Escala OCDE Modificada):** Coeficiente de composición familiar (1.0 primer adulto, 0.5 adicionales, 0.3 menores). Esta variable se calcula mediante el Padrón

- **$\gamma$ (Factor Territorial):** Ajuste por coste de vida local (basado en el índice de precios de vivienda y suministros del municipio). Esta variable debe ser proporcionada por el INE.
## La Variable $x$

El corazón del algoritmo es la **Cuota Líquida (C)**. El sistema utiliza una función de saturación exponencial para determinar cuánto recibe o cuánto paga un ciudadano.

### Definición de la Variable Crítica ($x$)

La variable $x$ representa el **Exceso o Déficit Relativo** de un hogar respecto a su umbral de dignidad:

$$x = \frac{B - k_{hogar}}{k_{hogar}}$$

- Si **$x = 0$**: El hogar gana exactamente lo necesario para ser digno. Indica un equilibrio total.
- Si **$x < 0$**: El hogar está en zona de vulnerabilidad.
- Si **$x > 0$**: El hogar tiene capacidad contributiva.


### La Ecuación de Cuota (C)

$$C = (B - k_{hogar}) \cdot L \cdot (1 - e^{-\sigma \cdot |x|})$$

|**Resultado**|**Acción del Sistema**|**Efecto Social**|
|---|---|---|
|**$C < 0$**|**Transferencia Automática**|El Estado ingresa dinero al ciudadano hasta cubrir su $k_{hogar}$.|
|**$C > 0$**|**Recaudación Progresiva**|El ciudadano tributa sin tramos, acercándose asintóticamente al límite $L$.|


## Sensores de Seguridad y Protocolos de Emergencia

El sistema incluye tres capas de protección "hard-coded" para evitar el colapso del modelo:

1. **Garantía de Solvencia:** El motor audita en cada ciclo que $\sum C_{pos} \ge \sum |C_{neg}| + G_{op}$. Si el saldo es negativo, el sistema entra en **Modo Alerta** y obliga a un ajuste fiscal de $k_{base}$ o a la emisión de deuda.

2. **Incentivo Laboral Inquebrantable:** Mediante la derivada positiva $\frac{d(Neto)}{dB} > 0$, el sistema garantiza que un ciudadano **siempre** tendrá más dinero neto si aumenta su renta bruta. Se elimina el "miedo a perder la ayuda".

3. **Protocolo PSD (Poverty Stop Device):** Si el sistema es solvente y el $k_{base}$ es inferior al umbral oficial de pobreza (**AROPE**), el motor propone automáticamente elevar el coeficiente $\alpha$ para blindar la dignidad nacional.
## Implementación Tecnológica: El principio de la "Caja de Cristal".
- **Base de Datos Unificada:** Fusión mediante SQL de datos catastrales, padrón, hacienda y asistencia social.

- **Transparencia Total:** Cualquier ciudadano puede verificar el cálculo de su cuota introduciendo su renta y código postal, eliminando la opacidad de las liquidaciones fiscales actuales.

- **Licencia:** Distribuido bajo **GNU GPL v3.0**, asegurando que el algoritmo de gestión de la riqueza común nunca pueda ser privatizado o manipulado en secreto.

## FAQ: Casos Específicos y Dinámicas Sociales

1. **¿Qué ocurre con la custodia compartida o padres divorciados?**
	**Respuesta**: El EFRD no reconoce estados civiles, sino flujos de renta y necesidades de protección. El coeficiente del menor ($\phi=0.3$) se divide entra las unidades de convivencia.

2. **¿Elimina el EFRD el incentivo de buscar trabajo?**
	**Respuesta**: En absoluto, de hecho, hace lo contrario. A diferencia del modelo actual donde perder una ayuda al empezar a trabajar puede generar una pérdida de la renta neta (la "trampa de la pobreza"), la derivada positiva del EFRD garantiza matemáticamente que el neto más 1€ sea mayor al neto anterior. Es decir, cada euro ganado siempre suma, solo que la velocidad de crecimiento se suaviza según la variable $x$.

3. **¿Cómo maneja el sistema a los autónomos con rentas variables?**
	**Respuesta**: El sistema permite una recalibración mensual o trimestral (habría que cambiar las entradas del código). Si un autónomo tiene un mes de ingresos cero, el sistema detecta instantáneamente que su $x$ es negativo y emite la transferencia de protección ($C_{neg}$). Cuando los ingresos vuelven, la cuota $C$ se ajusta automáticamente. Es una red de seguridad en tiempo real.

4. **¿Qué pasa si el PIB ($Y$) cae drásticamente (Crísis/Gran Recesión)?**
	**Respuesta**: El sistema activa el Ajuste Fiscal de manera automática. El $k_{base}$ bajaría proporcionalmente para proteger la solvencia del Estado. Es un mecanismo de "reparto de escasez" que evita que el pais quiebre por mantener promesas imposibles, permitiendo una recuperación más rápida sin generar deuda impagable.

5. **¿Cómo se evita el fraude fiscal si el sistema es tan "generoso"?**
	**Respuesta**: Tal como viene en el apartado anterior, el EFRD se basa en el principio de la **Caja de Cristal**. Al unificar las 6 bases de datos (Catastro, Padrón, Hacienda, etc.), las discrepacias saltan de forma algorítmica. Si alguien declara ingresos cero pero su ref. catastral indica una vivienda de alto valor en una zona con $\gamma$ elevada, el sistema bloque el protocolo $C_{neg}$ hasta una resolución.

6. **¿Sustituye este sistema a los políticos?**
	**Respuesta**: No. Los políticos siguen siendo quienes deciden los valores de $\alpha, L$ y $\sigma$. El EFRD es un "sistema de navegación".

7. **¿Sustituye este sistema a los funcionarios?**
	**Respuesta**: Este sistema automatiza la burocracia transaccional de los funcionarios. Actualmente, los funcionarios se encargan de realizar trámites y validarlos, con este sistema se encargarían de auditar a las personas en estado vulnerable y evaluar su estado, además de ser gestores de las 6 bases de datos que alimentan al sistema.
## Notas
**Nota de implementación:** En esta versión v4.0, el sistema reconoce que el PIB no es solo un número, sino el combustible que permite mover el umbral de dignidad. Sin un ciudadano contribuyente ($x > 0$), el protocolo de dignidad ($PSD$) permanece bloqueado para proteger la supervivencia del Estado.