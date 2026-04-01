from math import exp, ceil
import matplotlib.pyplot as plt
from numpy import linspace, zeros
from copy import deepcopy

class EFRD_Protocol_v3_2:
    def __init__(self, PIB_Y, Poblacion_Dict, Gini, Alpha, Sigma, Limite_L, G_op, mediana_renta_nacional, ingresos_totales_pasados, IPC_Pi=1.0):
        # Variables de Entrada
        self.Y = PIB_Y
        self.N_dist = Poblacion_Dict  
        self.N_total = sum(self.N_dist.values())
        self.G = Gini   
        self.alpha = Alpha  
        self.sigma = Sigma 
        self.L = Limite_L 
        self.G_op = G_op 
        self.pi = IPC_Pi
        self.ingresos_pasados = ingresos_totales_pasados # Guardado como referencia histórica
        
        # Cálculo del Suelo Vitalicio Base (k) - Modelo Sen
        self.k_base = self.alpha * (self.Y / self.N_total * (1 - self.G)) * self.pi
        
        # Definición del estándar mínimo de dignidad (60% mediana del INE)
        self.k_arope = 0.6 * mediana_renta_nacional


        # MOTOR DE ESTIMACIÓN MACROECONÓMICA DINÁMICA
        # Creamos rentas medias teóricas para cada grupo poblacional 
        # para estimar la recaudación usando las variables L y sigma actuales.
        # Evaluamos solo para k_base (phi=1, 0 adultos extra, 0 hijos).
        
        rentas_medias_estimadas = {
            "S0": 8000,                            # Vulnerables (bajo AROPE)
            "S1": mediana_renta_nacional,          # Equilibrio (renta media/mediana)
            "S2": mediana_renta_nacional * 2.5,    # Consolidados (clase media-alta)
            "S3": mediana_renta_nacional * 6.0     # Alto Impacto (clase alta)
        }
        
        recaudacion_bruta_dinamica = 0
        
        for estado, num_personas in self.N_dist.items():
            renta_grupo = rentas_medias_estimadas[estado]
            # Usamos el método de cálculo para ver cuánto paga este grupo
            simulacion_cuota = self.calcular_cuota_hogar(renta_grupo, num_adultos_extra=0, num_hijos=0)
            
            # Solo sumamos a la caja del Estado si la cuota es positiva (impuestos, no ayudas)
            if simulacion_cuota["C_cuota"] > 0:
                recaudacion_bruta_dinamica += simulacion_cuota["C_cuota"] * num_personas

        self.ingresos_totales = recaudacion_bruta_dinamica # Actualizamos la caja con la predicción
        
        # ==========================================================
        
        # Auditoría de Solvencia y Dignidad (Criterio EFRD v3.2)
        poblacion_receptora = self.N_dist["S0"] + self.N_dist["S1"]
        recaudacion_disponible = self.ingresos_totales - self.G_op
        coste_sistema_actual = poblacion_receptora * self.k_base

        ############################
        coste_arope = poblacion_receptora * self.k_arope
        faltante = (coste_arope - recaudacion_disponible) / 1e9
        # Validación de Solvencia para el k_base actual
        print(f"--- PARÁMETROS DE POLÍTICA FISCAL ---")
        print(f"alpha: {self.alpha} | sigma: {self.sigma} | limite L: {self.L}")
        print(f"Recaudación Bruta Dinámica Estimada: {self.ingresos_totales/1e9:.2f} B€\n")
        
        if recaudacion_disponible < coste_sistema_actual:
            print(f" ALERTA CRÍTICA: El sistema es INSOLVENTE con alpha={self.alpha}. Faltan {abs(faltante):.2f} B€")
        else:
            print(f" FINANCIACIÓN ASEGURADA para k_base actual ({self.k_base:.2f}€).")

        # Validación de Dignidad y Corrección Automática
        if self.k_base < self.k_arope:
            print(f" GESTIÓN INSUFICIENTE: k_base ({self.k_base:.2f}€) por debajo de AROPE ({self.k_arope:.2f}€).")
            
            # ¿Podemos permitirnos subirlo a AROPE?
            if recaudacion_disponible >= coste_arope:
                self.k_base = self.k_arope
                print(f" PROTOCOLO PSD ACTIVADO: k_base elevado a {self.k_base:.2f}€ (Solvencia disponible). Sobran {faltante}")
            else:
                print(f" IMPOSIBILIDAD TÉCNICA: No hay fondos para alcanzar AROPE. Faltarían {faltante:.2f} B€ adicionales.")
        else:
            print(f" SISTEMA ÓPTIMO: El suelo vitalicio supera el umbral de pobreza.")

        # Calculamos el coste final real con el k_base definitivo 
        # (ya sea el original o el corregido por PSD)
        coste_final_sistema = poblacion_receptora * self.k_base
        saldo_final = recaudacion_disponible - coste_final_sistema
        
        print(f"\n--- DEBUG DE LIQUIDACIÓN FINAL ---")
        print(f"Sueldo Base Definitivo (k): {self.k_base:.2f} €")
        print(f"Coste Total Ayudas: {coste_final_sistema/1e9:.2f} B€")
        print(f"Gastos Operativos (G_op): {self.G_op/1e9:.2f} B€")
        
        if saldo_final >= 0:
            print(f" EXCEDENTE DE CAJA: Sobran {saldo_final/1e9:.2f} B€ para inversión o reserva.")
        else:
            print(f" DÉFICIT OPERATIVO: Faltan {abs(saldo_final)/1e9:.2f} B€ (Requiere Deuda Pública).")
        print("\n" + "-="*30 + "\n")


    def calcular_cuota_hogar(self, ingresos_brutos_totales, num_adultos_extra, num_hijos):
        """
        Calcula la Cuota Líquida (C) basada en la Unidad de Convivencia (OCDE modificada).
        phi = 1.0 (principal) + 0.5 (adultos extra) + 0.3 (hijos).
        """
        phi = 1.0 + (num_adultos_extra * 0.5) + (num_hijos * 0.3)
        k_hogar = self.k_base * phi
        
        B = ingresos_brutos_totales
        diferencial = B - k_hogar
        
        # Normalización del excedente para la curva exponencial.
        x = diferencial / k_hogar if k_hogar != 0 else 0
        
        # Función de Tipo Impositivo Continuo (Asíntota L).
        tipo_impositivo = self.L * (1 - exp(-self.sigma * abs(x)))
        
        cuota_C = diferencial * tipo_impositivo
        return {
            "B_bruto": B,
            "phi": phi,
            "k_hogar": round(k_hogar, 2),
            "C_cuota": round(cuota_C, 2),
            "Neto": round(B - cuota_C, 2),
            "Tipo_Efectivo": round((cuota_C / B * 100), 2) if B > 0 else 0
        }

    def auditoria_sistema(self, dataset_poblacion):
        """
        Ejecuta las 4 Inecuaciones de Seguridad del Protocolo.
        Dataset esperado: lista de dicts con {
            'ingreso': float, 
            'adultos': int, 
            'hijos': int
        }
        """
        resultados = [self.calcular_cuota_hogar(p['ingreso'], p['adultos'], p['hijos']) for p in dataset_poblacion]
        
        recaudacion = sum(r['C_cuota'] for r in resultados if r['C_cuota'] > 0)
        ayudas = sum(abs(r['C_cuota']) for r in resultados if r['C_cuota'] < 0)
        
        # Condición de Solvencia.
        solvente = recaudacion >= (ayudas + self.G_op)
        
        # Ratio Crítico de Contribuyentes (R_c).
        contribuyentes = [r for r in resultados if r['C_cuota'] > 0]
        n_contrib = len(contribuyentes)
        c_media_pos = sum(c['C_cuota'] for c in contribuyentes) / n_contrib if n_contrib > 0 else 0
        min_contrib_req = (ayudas + self.G_op) / c_media_pos if c_media_pos > 0 else float('inf')
        
        return {
            "Solvencia_Estado": "OK" if solvente else "RIESGO_DE_QUIEBRA",
            "Balance_Neto_Efectivo": round(recaudacion - ayudas - self.G_op, 2),
            "N_Contribuyentes_Actual": n_contrib,
            "N_Contribuyentes_Minimo_Req": ceil(min_contrib_req),
            "Masa_Critica_Suficiente": n_contrib >= min_contrib_req
        }


class EFRD_AdvancedVisualizer:
    def __init__(self, motor):
        self.motor = motor

    # CURVAS COMPARATIVAS.
    def comparar_sigmas(self, ingresos, sigmas, adultos_extra, hijos):
        plt.figure()

        for sigma in sigmas:
            motor_tmp = deepcopy(self.motor)
            motor_tmp.sigma = sigma

            cuotas = [
                motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["C_cuota"]
                for i in ingresos
            ]

            plt.plot(ingresos, cuotas, label=f"sigma={sigma}")

        plt.title("Impacto de σ en la progresividad")
        plt.xlabel("Ingreso (€)")
        plt.ylabel("Cuota (€)")
        plt.legend()
        plt.grid()
        plt.show()

    def comparar_limite_L(self, ingresos, limites, adultos_extra=0, hijos=0):
        plt.figure()

        for L in limites:
            motor_tmp = deepcopy(self.motor)
            motor_tmp.L = L

            tipos = [
                motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["Tipo_Efectivo"]
                for i in ingresos
            ]

            plt.plot(ingresos, tipos, label=f"L={L}")

        plt.title("Impacto del límite máximo L")
        plt.xlabel("Ingreso (€)")
        plt.ylabel("Tipo efectivo (%)")
        plt.legend()
        plt.grid()
        plt.show()

    def comparar_alpha(self, ingresos, alphas, adultos_extra=0, hijos=0):
        plt.figure()

        for alpha in alphas:
            motor_tmp = deepcopy(self.motor)
            motor_tmp.alpha = alpha

            # recalcular k_base.
            motor_tmp.k_base = motor_tmp.alpha * (
                motor_tmp.Y / motor_tmp.N_total * (1 - motor_tmp.G)
            ) * motor_tmp.pi

            netos = [
                motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["Neto"]
                for i in ingresos
            ]

            plt.plot(ingresos, netos, label=f"alpha={alpha}")

        plt.title("Impacto de α (nivel de renta garantizada)")
        plt.xlabel("Ingreso (€)")
        plt.ylabel("Ingreso Neto (€)")
        plt.legend()
        plt.grid()
        plt.show()

    # MAPA DE CALOR DEL SISTEMA.
    def mapa_calor(self, ingresos, phis):
        matriz = zeros((len(phis), len(ingresos)))

        for i, phi in enumerate(phis):
            for j, ingreso in enumerate(ingresos):
                # invertimos phi → adultos/hijos aproximado.
                adultos_extra = int((phi - 1) / 0.5)
                hijos = int((phi - 1 - adultos_extra * 0.5) / 0.3)

                r = self.motor.calcular_cuota_hogar(
                    ingreso,
                    num_adultos_extra=max(0, adultos_extra),
                    num_hijos=max(0, hijos)
                )

                matriz[i, j] = r["Neto"]

        plt.figure()
        plt.imshow(
            matriz,
            aspect='auto',
            origin='lower',
            extent=[min(ingresos), max(ingresos), min(phis), max(phis)],
        )

        plt.colorbar(label="Ingreso Neto (€)")
        plt.title("Mapa de Calor del Sistema Redistributivo")
        plt.xlabel("Ingreso Bruto (€)")
        plt.ylabel("Factor hogar (φ)")
        plt.show()


# CONFIGURACIÓN DATOS REALES (INE / AEAT 2026)

# Distribución de la población por estados de resiliencia (Total 48.5M)
poblacion_españa = {
    "S0": 10815500, # Vulnerables (22.3%)
    "S1": 16878000, # Equilibrio (34.8%)
    "S2": 14113500, # Consolidados (29.1%)
    "S3": 6693000   # Alto Impacto (13.8%)
}

# Parámetros Macroeconómicos
PIB_actual = 1.6e12
mediana_renta = 18500  # Umbral de referencia INE
ingresos_fiscales_aeat_hist = 350e9 # Recaudación bruta pasada (ahora solo como referencia)
gastos_operativos_estado = 63669590000 # G_op (Sanidad, Educación, Deuda...)

# EJECUCIÓN EFRD (Con motor macro predictivo)

motor = EFRD_Protocol_v3_2(
    PIB_Y=PIB_actual, 
    Poblacion_Dict=poblacion_españa, 
    Gini=0.33, 
    Alpha=0.55, 
    Sigma=0.5, 
    Limite_L=0.65, 
    G_op=gastos_operativos_estado, 
    mediana_renta_nacional=mediana_renta, 
    ingresos_totales_pasados=ingresos_fiscales_aeat_hist
)

# 1. CÁLCULO INDIVIDUAL
print("--- CÁLCULO INDIVIDUAL ---")
print("="*30)
familia = motor.calcular_cuota_hogar(22000, num_adultos_extra=1, num_hijos=4)
print(f"Sueldo Hogar Protegido (k_hogar): {familia['k_hogar']}€")
print(f"Cuota Final (C): {familia['C_cuota']}€ ({'Recibe' if familia['C_cuota'] < 0 else 'Paga'})")
print(f"Dinero Neto Final: {familia['Neto']}€")
print(f"Tipo Impositivo Efectivo: {familia['Tipo_Efectivo']}%\n\n")

# 2. AUDITORÍA DE SEGURIDAD

print("--- AUDITORÍA DE SEGURIDAD ---")
print("="*30)

poblacion_ejemplo = [
    {'ingreso': 12000, 'adultos': 1, 'hijos': 2},
    {'ingreso': 45000, 'adultos': 1, 'hijos': 0},
    {'ingreso': 90000, 'adultos': 1, 'hijos': 1},
    {'ingreso': 500000, 'adultos': 0, 'hijos': 0}
]

motor.G_op = 50000 
reporte = motor.auditoria_sistema(poblacion_ejemplo)

for k, v in reporte.items():
    print(f"{k.replace('_', ' '):<25}: {v}")



# GRÄFICAS

adv = EFRD_AdvancedVisualizer(motor)
rango_ingresos = linspace(0, 150000, 150)

# Comparativas de impacto de parámetros políticos
adv.comparar_sigmas(rango_ingresos, [0.3, 0.75, 1.5], 1, 3) # Curva de agresividad fiscal
adv.comparar_limite_L(rango_ingresos, [0.4, 0.6, 0.8]) # Techo de contribución
adv.comparar_alpha(rango_ingresos, [0.3, 0.45, 0.6])  # Nivel de ambición del suelo vitalicio

# Mapa de calor: Relación Ingreso vs. Carga Familiar (/phi)
rango_phis = linspace(1.0, 3.0, 30)
adv.mapa_calor(rango_ingresos, rango_phis)

