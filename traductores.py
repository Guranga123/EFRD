def get_renta_mediana():
    from requests import get
    url_renta_mediana = "https://servicios.ine.es/wstempus/js/es/DATOS_SERIE/ICV802?nult=1"
    respuesta = get(url_renta_mediana)
    try:
        if respuesta.status_code == 200:
            data = respuesta.json()
            #print(data, "\n")
            for registro in data["Data"]:
                anyo = registro["Anyo"]
                valor = registro["Valor"]
                #print(f"Se ha recogido el dato {valor}€ renta mediana del año {anyo}")
                return valor
        else:
            print(f"Ha ocurrido un error al tratar de recoger el dato renta mediana en {url_renta_mediana}\nError de conexión: {respuesta.status_code}")
    except Exception as e:
        print(f"ERROR CRÍTICO: {type(e).__name__}\n{e}")

def get_pib_nominal_precios_corrientes():
    from requests import get
    url_renta_mediana = "https://servicios.ine.es/wstempus/js/es/DATOS_SERIE/CNTR6164?nult=1"
    respuesta = get(url_renta_mediana)
    try:
        if respuesta.status_code == 200:
            data = respuesta.json()
            #print(data, "\n")
            if "Data" in data and len(data["Data"]) > 0:
                registro = data["Data"][0]
                anyo = registro["Anyo"]
                valor = registro["Valor"]
                #print(f"Se ha recogido el dato {valor}€ renta mediana del año {anyo}")
                return anyo, valor*1e6 # Para que nos de el PIB en billones (escala europea)
            else:
                print(f"Error de conexión: {respuesta.status_code}")
        else:
            print(f"Ha ocurrido un error al tratar de recoger el dato renta mediana en {url_renta_mediana}")
    except Exception as e:
        print(f"ERROR CRÍTICO: {type(e).__name__}\n{e}")

def get_IPC_mas_reciente():
    from requests import get
    
    # URL de la tabla con los 5 últimos datos
    url_tabla = "https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/24077?nult=5"
    cabeceras = {"User-Agent": "Mozilla/5.0"}
    
    respuesta = get(url_tabla, headers=cabeceras)
    try:
        if respuesta.status_code == 200:
            data = respuesta.json()
            
            for serie in data:
                nombre = serie["Nombre"]
                
                # CAMBIO: Filtramos por "Índice general" e "Índice", 
                # tal como aparece en tu respuesta del navegador.
                if "Índice general" in nombre and "Índice" in nombre and "Variación" not in nombre:
                    
                    for registro in serie["Data"]:
                        valor = registro.get("Valor")
                        
                        if valor is not None:
                            anyo = registro.get("Anyo")
                            # print(f"Encontrado: {nombre} -> {valor} (Año {anyo})")
                            return anyo, valor/100
                            
            print("No se encontró la serie específica del Índice General.")
        else:
            print(f"Error HTTP: {respuesta.status_code}")
            
    except Exception as e:
        print(f"ERROR CRÍTICO: {type(e).__name__}\n{e}")

#print(get_renta_mediana())
#print(get_pib_nominal_precios_corrientes())
#print(get_IPC_mas_reciente())