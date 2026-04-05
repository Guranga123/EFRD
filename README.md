# EFRD (Equilibrio Fiscal Y Resiliencia Distributiva) v4.0

Una de las ventajas que ofrece este sistema es que elimina los saltos de los tramos del IRPF. Esto se logra gracias a una **Curva de transferencia continua y asintótica**. Esto garantiza que nunca se gane menos trabajando más y que la progresividad sea infinita.
## Conceptos Clave
El sistema se basa en la **Caja de Cristal**: transparencia total y automatización mediante variables macroeconómicas públicas

| Variable | Definición                           | Rango Operativo                                     |
| -------- | ------------------------------------ | --------------------------------------------------- |
| $Y$      | PIB Nominal anual (Riqueza Nacional) | Real (INE)                                          |
| $G$      | Coeficiente de Gini (desigualdad)    | 0.00 - 1.00, manual                                 |
| $\alpha$ | Coeficiente de Bienestar             | 0.30 - 0.50, (consenso político)                    |
| $L$      | Límite Fiscal (Techo)                | 0.45 - 0.70, (consenso político) recomendable: 0.60 |
| $\pi$    | Factor de Ajuste IPC                 | 0.80 - 1.20 (INE)                                   |

### Variables del Sistema.

Esta versión usa una base de datos transformada a través del código: ![[conexion/transformador.py]]
Esta pieza de código recoge 6 Bases de datos de diferentes organizaciones nacionales para luego fusionarlo en una base de datos final a través de SQL.
Las bases de entrada son:
1. **INE**: Proporciona un valor gamma(constante proporcional al precio de los bienes de un municipio) junto al código postal.
2. **CNP**: Proporciona los DNIs y NIEs junto a la edad de cada individuo.
3. **Hacienda**: Proporciona el DNI/NIE correspondiente a la renta mensual
4. **Ministerio de Vivienda**: Relaciona el número de referencia catastral al código postal de una vivienda.
5. **Padrón**: Relaciona El DNI/NIE con una referencia catastral
6. **Asistencia Social**: Relaciona un DNI/NIE con un municipio de asistencia (en caso de no tener vivienda) junto a un número $\phi$ que indica la vulnerabilidad (definido por el trabajador social) y un número $\gamma$ que depende del coste de vida local (dependiendo del municipio donde se encuentra, también lo define el trabajador social).

El esquema de la base de datos de salida se especifica en ![[Croquis_base_datos.pdf]]
### Factor Familiar $\phi$ (Escala OCDE Modificada).
El umbral de dignidad $k$ se ajusta según la unidad de convivencia $\phi$:
- **1.0**: Primer adulto.
- **0.5**: Segundo adulto / Familiar extra (sea o no contribuyente).
- **0.3**: Por cada hijo/menor.
### El impacto familiar
El sistema toma en cuenta la cantidad de personas que viven en la vivienda, su estado económico y el lugar en el que habitan para proporcionar un $k_{hogar}$ suficiente para sobrevivir
## Arquitectura Matemática
#### Sueldo Vitalicio Real ($K_{base}$)
Basado en la Renta de Bienestar de Sen para evitar sesgos de medias aritméticas: $$k_{base}=\alpha \cdot \frac{Y}{N}\cdot(1-G) \cdot \pi$$
Donde N es la cantidad de donantes y receptores.
#### Cuota Líquida (C)
El dinero que mueve el ciudadano al gob. o viceversa. 
$$C=(B-k_{hogar})\cdot L \cdot (1-e^{-\sigma\cdot|x|})$$
Si $C>0$, el ciudadano hace una transferencia al gobierno, lo que se conoce comúnmente como IRPF.
Y, Si $C<0$, el ciudadano recibe dinero del estado para llegar a la cantidad de $k_{base}$ en bruto.

#### Variable x (Exceso Relativo / de renta):
x es el indicador de posición socioeconómica respecto al umbral de protección. Se define como:
$$x = \frac{B-k_{hogar}}{k_{hogar}}$$
Permite que la curva de impuestos sea "justa" independientemente de si el umbral de una persona son 10.000€ o 40.000€. 

Al estar dentro del exponente ($-\sigma\cdot|x|$), determina que tan rápido el ciudadano alcanza el límite fiscal $L$.

Al usar el valor absoluto ($|x|$) en la fórmula de la cuota, el algoritmo trata con la misma "fuerza" el crecimiento del impuesto para el rico que el crecimiento del subsidio para el pobre, garantizando un equilibrio de tensiones en el modelo.

## ¿Se suma $k_{base}$ con $k_{hogar}$?
No. Hacerlo sería un error de duplicidad muy apreciable que quebraría el sistema en la primera iteración. 
La relación es de jerarquía y transformación, no de suma:
- $k_{base}$ es la constante teórica (la "base" de dignidad). Es lo que le correspondería a un adulto solo en una zona de coste de vida neutro ($\gamma=1.0$).
- $k_{hogar}$ es el $k_{base}$ ya procesado por las circunstancias del ciudadano. Es el umbral final que el motor usa para calcular la cuota $C$

La fórmula que transforma $k_{base}$ en $k_{hogar}$ es: $$k_{hogar}=k_{base}\cdot\phi\cdot\gamma$$
Donde se puede visualizar que tanto $\phi$ (circunstancias familiares del hogar) y $\gamma$ (coste de vida del lugar donde se habita) son directamente proporcionales a $k_{base}$

Entonces, ejemplificando la respuesta: Un sin hogar que gane 0€ se le donará un $k_{hogar}$ correspondiente a sus circunstancias.
## Inecuaciones de Seguridad
Hay que especificar que el sistema no solo calcula, sino que audita la viabilidad del Estado en tiempo real:
1. Si el sistema detecta un déficit, propone automáticamente un ajuste del $k_{base}$ tal que el saldo neto sea 0€ o la emisión de deuda para pagar todos los donativos.
2. El **Protocolo PSD**: Si existe superávit y el sueldo vitalicio es inferior al umbral AROPE (60% de la renta mediana nacional), el algoritmo solicita permiso para elevar el bienestar general.
Además de estos protocolos de seguridad, se conservan los de la versión anterior:
3. La **Solvencia**: $\sum C_{pos}\ge \sum |C_neg| + G_{op}$
4. La **Masa Crítica**: Ratio mínimo de contribuyentes activos necesarios.
5. El **Incentivo Laboral**: La derivada de la renta siempre es positiva.

## Pruebas (sección bajo actualizaciones).
Se ha agregado un stress test por medio de las cadenas de Markov, ver el documento 'Analisis_tecnico.md' y 'Markov.ipynb' de la carpeta "Analisis-Cadenas_Markov" para más información.


## Guia de Inicio Rápido (Quick Start)
### Ejecución y simulación
```
# Clonar el repositorio
git clone https://github.com/mouse3/EFRD
cd EFRD

# Instalar dependencias
pip install -r requirements.txt
 
# Crear las bases de datos de entrada

python3 conexion/crear_db_ejemplo.py

# Transformar las bases de datos de entrada a una final

python3 conexion/transformador.py

# Visualizar el croquis de la base de datos
Abrir conexion/Croquis/Croquis_base_datos.pdf con cualquier lector PDF

python3 conexion/lector.py #Lee la base de datos transformada (conexion/outputs/base_final_efrd.db)

# Si desea visualizar en un .csv la disposición de la base de datos final, abra el archivo conexion/outputs/base_final_efrd.csv

# Ejecutar el motor central
python3 main.py
```

Téngase en cuenta que el sistema toma de entrada las bases de datos de ejemplo. Para ser más precisos, habría que construir una base de datos transformada con varias filas (referencias catastrales útiles).

## Ejemplos de Casos de Uso

| Perfil            | Renta Bruta | Escenario Económico | Resultado EFRD                    |
| ----------------- | ----------- | ------------------- | --------------------------------- |
| Hogar Vulnerable  | 0           | PIB Estable         | Recibe $k_{hogar}$                |
| Clase Trabajadora | 22.000 €    | Crisis (Déficit)    | Protección del neto / pago mínimo |
| Renta Alta        | 120.000 €   | Abundancia          | Contribución progresiva ($L=0.6$) |

## Téngase en cuenta

Los datos de entrada han de actualizarse anualmente, tales como el índice Gini y el IPC. Además, es importante que el PIB sea lo más reciente posible.

Para visualizar más detalles, entre en 'Documentacion/propuesta técnica.md'
## Licencia
Este -ambicioso- proyecto está bajo la licencia **GNU General Public License v3.0 (GPL-3.0)**. Esto garantiza que el algoritmo permanezca abierto, auditable y que cualquier cambio o mejora sea compartida y de libre acceso con la comunidad. Esto garantiza esa "Caja de Cristal", es decir, garantiza que la transparencia se mantenga aún habiendo realizado cambios.
