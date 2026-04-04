import pprint

gamma = 1.3  # Valor de ejemplo (no significa nada por sí solo, se usa como fallback)
CODIGO_POSTAL = 28001 # Igual que la anterior variable, se usa para eliminar el error visual, no tiene significado por sí solo.


# Bloque 1: bases de datos de orignes (organización) INPUTs

Data_base_INE = {
    CODIGO_POSTAL: 1.3, # [CODIGO POSTAL]:int : gamma:float
    41001: 0.9
}

Data_base_CNP = {   # DNI/NIE/NIF:str, Edad (Incluye extranjeros):int
    "1000000X": 40,   # Adulto 1
    "2000000X": 39,   # Adulto 2
    "3000000X": 16,   # Menor 1
    "4000000X": 5,    # Menor 2
    "X1234567L": 30,  # NIE: Extranjero con nómina (Sin casa/Asistencia)
    "Y9876543M": 60   # NIE: Sin hogar (En Asistencia Social)
}

Data_base_Hacienda = {  # DNI/NIE/NIF.str, renta_mensual:float
    "1000000X": 21000,
    "2000000X": 20000,
    "X1234567L": 1500  # Renta de entrada detectada
}

Data_base_Ministerio_Vivienda = {
    "0000000 AA0000A 0001 AA": ( # Referencia Catastral:str : (CP:int, Lista DNIs)
        CODIGO_POSTAL, 
        ["1000000X", "2000000X", "3000000X", "4000000X"]
    )
}

Data_base_Padron = { # DNI/NIE/NIF:str : ref_catastral:str
    "1000000X": "0000000 AA0000A 0001 AA",
    "2000000X": "0000000 AA0000A 0001 AA",
    "3000000X": "0000000 AA0000A 0001 AA",
    "4000000X": "0000000 AA0000A 0001 AA"
}

Data_base_Asistencia_Social = { # DNI/NIE/NIF:str : (municipio:str, phi_social:float, gamma_local:float)
    "Y9876543M": ("Madrid", 0.85, 1.35) 
}

# Bloque 2: Transformación (Lógica EFRD - ocurre en la RAM)

""" 
Lógica de Negocio aplicada:
1. edad < 18 (CNP) => phi = 0.3
2. edad >= 18 Y renta > 0 (Hacienda) => phi = 0
3. edad >= 18 Y renta = 0 (Hacienda) => phi = 0.5
4. Si es VIRTUAL y está en Asistencia Social => phi y gamma provienen del Municipio
"""

Data_base_final = {}

# Identificamos a todos los IDs que entran al sistema (Padrón OR Asistencia OR Renta > 0)
ids_activos = set(Data_base_Padron.keys()) | \
              set(Data_base_Asistencia_Social.keys()) | \
              {k for k, v in Data_base_Hacienda.items() if v > 0}

for dni in ids_activos:
    # Denotamos la Unidad de Convivencia (Casa o Virtual)
    ref_cat = Data_base_Padron.get(dni)
    es_virtual = False
    
    if not ref_cat:
        ref_cat = f"VIRTUAL_{dni}"
        es_virtual = True
        
    # Si la unidad no existe en la base final, la inicializamos
    if ref_cat not in Data_base_final:
        if es_virtual:
            # Si es virtual, intentamos sacar gamma de Asistencia Social, si no 1.0
            g = Data_base_Asistencia_Social.get(dni, ("-", 0.5, 1.0))[2]
            tipo = "virtual"
        else:
            # Si es física, sacamos CP de Vivienda y gamma de INE
            cp = Data_base_Ministerio_Vivienda.get(ref_cat, (1, []))[0]
            g = Data_base_INE.get(cp, 1.0)
            tipo = "fisica"
            
        Data_base_final[ref_cat] = {
            "gamma": g,
            "tipo_unidad": tipo,
            "lista_inquilinos": {}
        }

    # datos del inquilino (Renta y Phi)
    renta = Data_base_Hacienda.get(dni, 0.0)
    edad = Data_base_CNP.get(dni, 18)
    
    # Logica de \phi
    if edad < 18:
        phi = 0.3
    elif es_virtual and dni in Data_base_Asistencia_Social:
        phi = Data_base_Asistencia_Social[dni][1] # Phi proporcionado por el municipio
    elif renta > 0:
        phi = 0.0 # phi = 0 si entra dinero
    else:
        phi = 0.5 # phi = 0.5 si es mayor de edad y no hay renta de entrada
        
    Data_base_final[ref_cat]["lista_inquilinos"][dni] = (renta, phi)

# Bloque 3: Salida final (es una analogía al .csv)

print("--- BASE DE DATOS FINAL (OUTPUT) ---")
pprint.pprint(Data_base_final)

# Ejemplo lectura de un registro específico:
# Data_base_final["REF_CATASTRAL"] = (gamma, { DNI: (renta, phi) })