from math import exp, ceil
import matplotlib.pyplot as plt
from numpy import zeros
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
        self.ingresos_pasados = ingresos_totales_pasados 
        self.diccionario_INE = {
            "28001": 1.28,
            "28013": 1.25,
            "08001": 1.26,
            "08007": 1.24,
            "41001": 1.00,
            "46001": 1.05,
            "15001": 0.93,
            "24001": 0.87,
            "default": 1.0
        }
        
        # 1. Cálculo del Suelo Vitalicio Base (k) - Modelo Sen
        self.k_base = self.alpha * (self.Y / self.N_total * (1 - self.G)) * self.pi
        
        # Definición del estándar mínimo de dignidad (60% mediana del INE)
        self.k_arope = 0.6 * mediana_renta_nacional

        # MOTOR DE ESTIMACIÓN MACROECONÓMICA DINÁMICA
        rentas_medias_estimadas = {
            "S0": 8000,                            # Vulnerables (bajo AROPE)
            "S1": mediana_renta_nacional,          # Equilibrio (renta media/mediana)
            "S2": mediana_renta_nacional * 2.5,    # Consolidados (clase media-alta)
            "S3": mediana_renta_nacional * 6.0     # Alto Impacto (clase alta)
        }
        
        poblacion_receptora = self.N_dist["S0"] + self.N_dist["S1"]

        # Función interna para simular el balance con un k_base específico
        def simular_balance(k_prueba):
            # Guardamos el k_base original
            k_temp = self.k_base
            self.k_base = k_prueba 

            recaudacion = 0
            coste = 0

            # Distribución geográfica simplificada (puedes refinarla)
            codigos_tipo = {
                "S0": "24001",  # zona rural (bajo coste)
                "S1": "41001",  # coste medio
                "S2": "28013",  # urbano alto
                "S3": "28001"   # núcleo premium
            }

            rentas_medias_estimadas = {
                "S0": 8000,
                "S1": self.k_arope / 0.6 if self.k_arope else 18000,
                "S2": (self.k_arope / 0.6) * 2.5 if self.k_arope else 45000,
                "S3": (self.k_arope / 0.6) * 6.0 if self.k_arope else 100000
            }

            # SIMULACIÓN CON γ TERRITORIAL
            for estado, num_personas in self.N_dist.items():
            
                cp = codigos_tipo.get(estado, "00000")

                resultado = self.calcular_cuota_hogar(
                    ingresos_brutos_totales=rentas_medias_estimadas[estado],
                    num_adultos_extra=0,
                    num_hijos=0,
                    codigo_postal=cp
                )

                cuota = resultado["C_cuota"]

                if cuota > 0:
                    recaudacion += cuota * num_personas
                else:
                    coste += abs(cuota) * num_personas

            # Balance final
            saldo = recaudacion - self.G_op - coste

            # Restauramos k_base original
            self.k_base = k_temp 

            return saldo, recaudacion

        # Evaluamos el estado inicial
        saldo_actual, rec_actual = simular_balance(self.k_base)
        self.ingresos_totales = rec_actual

        print(f"--- PARÁMETROS DE POLÍTICA FISCAL ---")
        print(f"alpha: {self.alpha} | sigma: {self.sigma} | limite L: {self.L}")
        print(f"Recaudación Bruta Dinámica Estimada: {self.ingresos_totales/1e9:.2f} B€\n")
        

        # PROTOCOLO DE AUDITORÍA Y TOMA DE DECISIONES DE EMERGENCIA
        ajuste_emergencia_activado = False
        
        if saldo_actual < 0:
            print(f" ALERTA CRÍTICA: El sistema es INSOLVENTE con el k_base inicial ({self.k_base:.2f}€). Faltan {abs(saldo_actual)/1e9:.2f} B€.")
            
            # Algoritmo de Búsqueda Binaria: Encuentra el k_base exacto de equilibrio
            k_min = 0.0
            k_max = self.k_base
            
            for _ in range(100): 
                k_mid = (k_min + k_max) / 2
                saldo_mid, _ = simular_balance(k_mid)
                
                if saldo_mid >= 0:
                    k_min = k_mid 
                else:
                    k_max = k_mid 

            # Menú Interactivo de Decisión Política
            while True:
                try:
                    print("\nDECISIÓN REQUERIDA:")
                    print(" 1 - Adquirir deuda pública para pagar el sueldo vitalicio actual.")
                    print(f" 2 - Cambiar el sueldo vitalicio (Resultante de deuda: 0). k_base se ajustará a: {k_min:.2f}€")
                    opcion = int(input("Seleccione (1/2): "))
                    
                    if opcion == 2:
                        self.k_base = k_min # Asignamos el k_base máximo viable
                        ajuste_emergencia_activado = True
                        print(f"\n AJUSTE DE EMERGENCIA: k_base reducido automáticamente a {self.k_base:.2f}€ para garantizar el 100% de los pagos.")
                        break
                    elif opcion == 1:
                        print("\n RESOLUCIÓN: Se asume el déficit vía Deuda Pública. El k_base se mantiene.")
                        break
                    else:
                        print(" Opción no válida. Introduzca 1 o 2.")
                except ValueError:
                    print(" Entrada inválida. Por favor, introduzca un número.")

        else:
            print(f" FINANCIACIÓN ASEGURADA para k_base actual ({self.k_base:.2f}€).")
            
        # VALIDACIÓN DE DIGNIDAD (Evaluada SIEMPRE tras la solvencia)
        if self.k_base < self.k_arope:
            print(f" GESTIÓN INSUFICIENTE: k_base actual ({self.k_base:.2f}€) está por debajo de AROPE ({self.k_arope:.2f}€).")
            
            if ajuste_emergencia_activado:
                print(f" PROTOCOLO PSD BLOQUEADO: Imposible elevar a AROPE tras aplicar un recorte por insolvencia estructural.")
            else:
                # Simulamos el escenario PSD (Dignidad)
                saldo_arope, rec_arope = simular_balance(self.k_arope)
                coste_psd_extra = (self.k_arope - self.k_base) * poblacion_receptora
                
                if saldo_arope >= 0:
                    print(f"\n--- PROYECCIÓN DE IMPACTO PROTOCOLO PSD ---")
                    print(f"Subida de suelo: {self.k_base:.2f}€ -> {self.k_arope:.2f}€")
                    print(f"Coste adicional para el Estado: {coste_psd_extra/1e9:.2f} B€")
                    print(f"Superávit resultante tras PSD: {saldo_arope/1e9:.2f} B€")
                    
                    while True:
                        try:
                            print(f"\n¿Desea aplicar el ajuste de dignidad?")
                            print(f" 1 - NO: Mantener k_base actual y maximizar ahorro.")
                            print(f" 2 - SÍ: Activar PSD (Nivelar con AROPE).")
                            op_psd = int(input("Seleccione (1/2): "))
                            
                            if op_psd == 2:
                                self.k_base = self.k_arope
                                print(f" PROTOCOLO PSD ACTIVADO: El sistema ahora cumple con el estándar de dignidad.")
                                break
                            elif op_psd == 1:
                                print(f" PSD RECHAZADO: Se mantiene el k_base original por prudencia fiscal.")
                                break
                            else:
                                print(" Opción no válida.")
                        except ValueError:
                            print(" Entrada inválida.")
                else:
                    print(f" IMPOSIBILIDAD TÉCNICA: Activar el PSD generaría un déficit de {abs(saldo_arope)/1e9:.2f} B€.")
        else:
            print(f" SISTEMA ÓPTIMO: El suelo vitalicio ya supera el umbral de pobreza.")

        # DEBUG DE LIQUIDACIÓN FINAL CON K_BASE DEFINITIVO
        saldo_final, rec_final = simular_balance(self.k_base)
        self.ingresos_totales = rec_final
        coste_final_sistema = poblacion_receptora * self.k_base
        recaudacion_disponible = self.ingresos_totales - self.G_op
        
        print(f"\n--- DEBUG DE LIQUIDACIÓN FINAL ---")
        print(f"Sueldo Base Definitivo (k): {self.k_base:.2f} €")
        print(f"Coste Total Ayudas: {coste_final_sistema/1e9:.2f} B€")
        print(f"Gastos Operativos (G_op): {self.G_op/1e9:.2f} B€")
        
        if saldo_final > -0.1: 
            print(f" EXCEDENTE DE CAJA: Sobran {max(0, saldo_final)/1e9:.2f} B€ para inversión o reserva.")
        else:
            print(f" DÉFICIT OPERATIVO: Faltan {abs(saldo_final)/1e9:.2f} B€ (Requiere emisión de Deuda Pública).")
        print("\n" + "-="*30 + "\n")
    
    def obtener_gamma(self, codigo_postal):
        return self.diccionario_INE.get(codigo_postal, self.diccionario_INE["default"])

    def coste_ayudas_desde_dataset(dataset_poblacion, k_base):
        total_ayudas = 0
        for p in dataset_poblacion:
            phi = 1.0 + (p['adultos'] - 1) * 0.5 + p['hijos'] * 0.3
            k_hogar = k_base * phi
            saldo = p['ingreso'] - k_hogar
            if saldo < 0:
                total_ayudas += -saldo   # suma del saldo negativo en valor absoluto
        return total_ayudas
    

    


    def calcular_cuota_hogar(self, ingresos_brutos_totales, num_adultos_extra, num_hijos, codigo_postal="00000"):

        gamma = self.obtener_gamma(codigo_postal)
        k_base_ajustado = self.k_base * gamma

        phi = 1.0 + (num_adultos_extra * 0.5) + (num_hijos * 0.3)
        k_hogar = k_base_ajustado * phi

        B = ingresos_brutos_totales
        diferencial = B - k_hogar

        x = diferencial / k_hogar if k_hogar != 0 else 0
        tipo_impositivo = self.L * (1 - exp(-self.sigma * abs(x)))

        cuota_C = diferencial * tipo_impositivo

        return {
            "gamma": gamma,
            "k_base_ajustado": round(k_base_ajustado, 2),
            "k_hogar": round(k_hogar, 2),
            "C_cuota": round(cuota_C, 2),
            "Neto": round(B - cuota_C, 2)
        }

    def auditoria_sistema(self, dataset_poblacion):
        resultados = [self.calcular_cuota_hogar(p['ingreso'], p['adultos'], p['hijos']) for p in dataset_poblacion]
    
        recaudacion = sum(r['C_cuota'] for r in resultados if r['C_cuota'] > 0)
        ayudas = sum(-r['C_cuota'] for r in resultados if r['C_cuota'] < 0)
    
        solvente = recaudacion >= (ayudas + self.G_op)
    
        contribuyentes = [r for r in resultados if r['C_cuota'] > 0]
        n_contrib = len(contribuyentes)
        c_media_pos = sum(c['C_cuota'] for c in contribuyentes) / n_contrib if n_contrib > 0 else 0
        min_contrib_req = (ayudas + self.G_op) / c_media_pos if c_media_pos > 0 else float('inf')
    
        return {
            "Solvencia_Estado": "OK" if solvente else "RIESGO DE QUIEBRA",
            "Balance_Neto_Efectivo": round(recaudacion - ayudas - self.G_op, 2),
            "N_Contribuyentes_Actual": n_contrib,
            "N_Contribuyentes_Minimo_Req": ceil(min_contrib_req),
            "Masa_Critica_Suficiente": n_contrib >= min_contrib_req
        }


    def auditoria_sistema(self, dataset_poblacion):
        """
        Ejecuta las 4 Inecuaciones de Seguridad del Protocolo.
        Dataset esperado: lista de dicts con { 'ingreso': float, 'adultos': int, 'hijos': int }
        """
        resultados = [
            self.calcular_cuota_hogar(
                p['ingreso'],
                p['adultos'],
                p['hijos'],
                p.get('codigo_postal', "00000")
            )
            for p in dataset_poblacion
        ]

        recaudacion = sum(r['C_cuota'] for r in resultados if r['C_cuota'] > 0)
        ayudas = sum(abs(r['C_cuota']) for r in resultados if r['C_cuota'] < 0)
        
        solvente = recaudacion >= (ayudas + self.G_op)
        
        contribuyentes = [r for r in resultados if r['C_cuota'] > 0]
        n_contrib = len(contribuyentes)
        c_media_pos = sum(c['C_cuota'] for c in contribuyentes) / n_contrib if n_contrib > 0 else 0
        min_contrib_req = (ayudas + self.G_op) / c_media_pos if c_media_pos > 0 else float('inf')
        
        return {
            "Solvencia_Estado": "OK" if solvente else "RIESGO DE QUIEBRA",
            "Balance_Neto_Efectivo": round(recaudacion - ayudas - self.G_op, 2),
            "N_Contribuyentes_Actual": n_contrib,
            "N_Contribuyentes_Minimo_Req": ceil(min_contrib_req),
            "Masa_Critica_Suficiente": n_contrib >= min_contrib_req
        }


class EFRD_AdvancedVisualizer:
    def __init__(self, motor):
        self.motor = motor

    def comparar_sigmas(self, ingresos, sigmas, adultos_extra, hijos):
        plt.figure()
        for sigma in sigmas:
            motor_tmp = deepcopy(self.motor)
            motor_tmp.sigma = sigma
            cuotas = [motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["C_cuota"] for i in ingresos]
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
            tipos = [motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["Tipo_Efectivo"] for i in ingresos]
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
            motor_tmp.k_base = motor_tmp.alpha * (motor_tmp.Y / motor_tmp.N_total * (1 - motor_tmp.G)) * motor_tmp.pi
            netos = [motor_tmp.calcular_cuota_hogar(i, adultos_extra, hijos)["Neto"] for i in ingresos]
            plt.plot(ingresos, netos, label=f"alpha={alpha}")

        plt.title("Impacto de α (nivel de renta garantizada)")
        plt.xlabel("Ingreso (€)")
        plt.ylabel("Ingreso Neto (€)")
        plt.legend()
        plt.grid()
        plt.show()

    def mapa_calor(self, ingresos, phis):
        matriz = zeros((len(phis), len(ingresos)))
        for i, phi in enumerate(phis):
            for j, ingreso in enumerate(ingresos):
                adultos_extra = int((phi - 1) / 0.5)
                hijos = int((phi - 1 - adultos_extra * 0.5) / 0.3)
                r = self.motor.calcular_cuota_hogar(
                    ingreso, num_adultos_extra=max(0, adultos_extra), num_hijos=max(0, hijos)
                )
                matriz[i, j] = r["Neto"]

        plt.figure()
        plt.imshow(matriz, aspect='auto', origin='lower', extent=[min(ingresos), max(ingresos), min(phis), max(phis)])
        plt.colorbar(label="Ingreso Neto (€)")
        plt.title("Mapa de Calor del Sistema Redistributivo")
        plt.xlabel("Ingreso Bruto (€)")
        plt.ylabel("Factor hogar (φ)")
        plt.show()