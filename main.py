from EFRD import EFRD_Protocol_v3_2, EFRD_AdvancedVisualizer
from numpy import linspace

# ==========================================================
# CONFIGURACIÓN INE (γ geográfico)
# ==========================================================
diccionario_INE = {
    "28001": 1.28,  # Madrid centro
    "28013": 1.25,
    "08001": 1.26,  # Barcelona
    "08007": 1.24,
    "41001": 1.00,  # Sevilla
    "46001": 1.05,  # Valencia
    "15001": 0.93,  # Galicia
    "24001": 0.87,  # León
    "default": 1.0
}

# ==========================================================
# DATOS MACRO
# ==========================================================
poblacion_españa = {
    "S0": 10815500,
    "S1": 16878000,
    "S2": 14113500,
    "S3": 6693000
}

PIB_actual = 1.6e12
mediana_renta = 18500  
ingresos_fiscales_aeat_hist = 350e9 
gastos_operativos_estado = 73669590000

# ==========================================================
# INICIALIZACIÓN DEL MOTOR
# ==========================================================
motor = EFRD_Protocol_v3_2(
    PIB_Y=PIB_actual, 
    Poblacion_Dict=poblacion_españa, 
    Gini=0.33, 
    Alpha=0.4,
    Sigma=0.7, 
    Limite_L=0.60, 
    G_op=gastos_operativos_estado, 
    mediana_renta_nacional=mediana_renta, 
    ingresos_totales_pasados=ingresos_fiscales_aeat_hist
)

# Inyectamos el diccionario INE al motor
motor.diccionario_INE = diccionario_INE

# ==========================================================
# CÁLCULO INDIVIDUAL (CON γ)
# ==========================================================
print("--- CÁLCULO INDIVIDUAL ---")
print("="*30)

familia = motor.calcular_cuota_hogar(
    ingresos_brutos_totales=22000,
    num_adultos_extra=1,
    num_hijos=4,
    codigo_postal="28001"  # Madrid centro
)

print(f"γ aplicado: {familia['gamma']}")
print(f"k_base ajustado: {familia['k_base_ajustado']}€")
print(f"Sueldo Hogar Protegido (k_hogar): {familia['k_hogar']}€")
print(f"Cuota Final (C): {familia['C_cuota']}€ ({'Recibe' if familia['C_cuota'] < 0 else 'Paga'})")
print(f"Dinero Neto Final: {familia['Neto']}€\n\n")

# ==========================================================
# AUDITORÍA DE SEGURIDAD (GEOGRÁFICA)
# ==========================================================
print("--- AUDITORÍA DE SEGURIDAD ---")
print("="*30)

poblacion_ejemplo = [
    {'ingreso': 12000, 'adultos': 1, 'hijos': 2, 'codigo_postal': "24001"},
    {'ingreso': 45000, 'adultos': 1, 'hijos': 0, 'codigo_postal': "41001"},
    {'ingreso': 90000, 'adultos': 1, 'hijos': 1, 'codigo_postal': "28013"},
    {'ingreso': 500000, 'adultos': 0, 'hijos': 0, 'codigo_postal': "28001"}
]

reporte = motor.auditoria_sistema(poblacion_ejemplo)

for k, v in reporte.items():
    print(f"{k.replace('_', ' '):<30}: {v}")

# ==========================================================
# VISUALIZACIÓN AVANZADA
# ==========================================================
adv = EFRD_AdvancedVisualizer(motor)

rango_ingresos = linspace(0, 150000, 150)
rango_phis = linspace(1.0, 3.0, 30)

# Activar si quieres análisis:
# adv.comparar_sigmas(rango_ingresos, [0.3, 0.75, 1.5], 1, 3) 
# adv.comparar_limite_L(rango_ingresos, [0.4, 0.6, 0.8]) 
# adv.comparar_alpha(rango_ingresos, [0.3, 0.45, 0.6]) 
# adv.mapa_calor(rango_ingresos, rango_phis)