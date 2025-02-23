import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuración inicial
st.set_page_config(page_title="NeoAssistant", layout="wide")
st.title("Asistente Neonatal Integral 🍼")

# =================================================================
# BASE DE DATOS DE DIAGNÓSTICOS Y TRATAMIENTOS
# =================================================================
treatment_guidelines = {
    # Infecciones
    "Sepsis neonatal temprana": {
        "medicamentos": [
            {
                "nombre": "Ampicilina",
                "dosis": "50 mg/kg",
                "intervalo": "Cada 12h",
                "via": "IV",
                "duracion": "7-10 días",
                "consideraciones": "Ajustar según cultivos"
            },
            {
                "nombre": "Gentamicina",
                "dosis": "4 mg/kg",
                "intervalo": "Cada 24h",
                "via": "IV",
                "consideraciones": "Monitorear función renal"
            }
        ],
        "fuente": "SEN 2023"
    },
    "Shock séptico": {
        "medicamentos": [
            {
                "nombre": "Fluidos (SSN 0.9%)",
                "dosis": "20 mL/kg en 10-20 min",
                "intervalo": "Repetir hasta 60 mL/kg",
                "via": "IV"
            },
            {
                "nombre": "Dopamina",
                "dosis": "5-20 mcg/kg/min",
                "intervalo": "Infusión continua",
                "via": "IV"
            }
        ],
        "fuente": "Surviving Sepsis Campaign 2024"
    },
    "Lúes congénita": {
        "medicamentos": [
            {
                "nombre": "Penicilina G Benzatínica",
                "dosis": "50,000 U/kg IM",
                "intervalo": "Dosis única",
                "via": "IM"
            }
        ],
        "fuente": "OMS 2023"
    },

    # Metabólicos
    "Hipoglucemia neonatal": {
        "medicamentos": [
            {
                "nombre": "Glucosa IV 10%",
                "dosis": "2 mL/kg (200 mg/kg)",
                "intervalo": "Bolo inicial",
                "via": "IV"
            },
            {
                "nombre": "Dextrosa al 10%",
                "dosis": "80-100 mL/kg/día",
                "intervalo": "Continua",
                "via": "IV"
            }
        ],
        "fuente": "AAP 2023"
    },
    "Ictericia neonatal": {
        "medicamentos": [
            {
                "nombre": "Fototerapia",
                "dosis": "Según nomograma de Bhutani",
                "intervalo": "Continua",
                "via": "Cutánea"
            }
        ],
        "fuente": "OMS 2023"
    },

    # Cardiovasculares
    "Ductus arterioso persistente": {
        "medicamentos": [
            {
                "nombre": "Ibuprofeno",
                "dosis": "10 mg/kg día 1, luego 5 mg/kg días 2-3",
                "intervalo": "Cada 24h",
                "via": "IV/PO"
            }
        ],
        "fuente": "J Pediatrics 2023"
    },
    "Cardiopatía congénita (crítica)": {
        "medicamentos": [
            {
                "nombre": "Prostaglandina E1",
                "dosis": "0.01-0.05 mcg/kg/min",
                "intervalo": "Infusión continua",
                "via": "IV"
            }
        ],
        "fuente": "Circulation 2023"
    },

    # Hematológicos
    "Anemia del prematuro": {
        "medicamentos": [
            {
                "nombre": "Eritropoyetina",
                "dosis": "200-400 U/kg",
                "intervalo": "3 veces/semana",
                "via": "SC"
            }
        ],
        "fuente": "NeoReviews 2023"
    },

    # Neurológicos
    "Apnea del prematuro": {
        "medicamentos": [
            {
                "nombre": "Citrato de cafeína",
                "dosis": "Carga: 20 mg/kg | Mantenimiento: 5 mg/kg/día",
                "intervalo": "Cada 24h",
                "via": "IV/PO"
            }
        ],
        "fuente": "NeoReviews 2023"
    },
    "Convulsiones neonatales": {
        "medicamentos": [
            {
                "nombre": "Fenobarbital",
                "dosis": "20 mg/kg (dosis carga)",
                "intervalo": "Mantenimiento: 3-5 mg/kg/día",
                "via": "IV"
            }
        ],
        "fuente": "Epilepsia 2023"
    },
    "Encefalopatía hipóxico-isquémica (HIE)": {
        "medicamentos": [
            {
                "nombre": "Hipotermia terapéutica",
                "dosis": "33.5°C durante 72h",
                "intervalo": "Mantener temperatura central",
                "via": "Sistema de enfriamiento"
            }
        ],
        "fuente": "NICE 2024"
    },

    # Respiratorios
    "Displasia broncopulmonar": {
        "medicamentos": [
            {
                "nombre": "Dexametasona",
                "dosis": "0.15 mg/kg/día",
                "intervalo": "Cada 12h x3 días",
                "via": "IV"
            }
        ],
        "fuente": "ERS 2023"
    }
}

# =================================================================
# INTERFAZ DE USUARIO
# =================================================================

# --- Sidebar: Datos del paciente ---
with st.sidebar:
    st.header("Datos del Paciente")
    gestational_age = st.number_input("Edad gestacional (semanas)", 22, 42, 34)
    weight = st.number_input("Peso (kg)", 0.5, 5.0, 1.8)
    postnatal_age = st.number_input("Edad postnatal (días)", 0, 90, 3)
    diagnosis = st.multiselect("Diagnóstico(s)", list(treatment_guidelines.keys()))

# --- Pestañas Principales ---
tab1, tab2, tab4, tab5, tab6 = st.tabs(["Tratamientos", "Nutrición", "Monitorización", "I/E", "Líquidos/Electrolitos"])

# Pestaña 1: Tratamientos
with tab1:
    st.header("Recomendaciones de Tratamiento")
    
    if not diagnosis:
        st.warning("Seleccione al menos un diagnóstico en el sidebar.")
    else:
        for dx in diagnosis:
            if dx not in treatment_guidelines:
                st.error(f"Error: '{dx}' no está en la base de datos.")
                continue
            
            guidelines = treatment_guidelines[dx]
            st.subheader(f"🗒️ {dx}")
            
            for med in guidelines["medicamentos"]:
                with st.expander(f"💊 *{med['nombre']}*"):
                    # Calcular dosis por peso (versión corregida)
                    if "mg/kg" in med["dosis"]:
                        try:
                            # Extraer solo la parte numérica de la dosis
                            dose_str = med["dosis"].split(":")[1].split("mg")[0].strip() if ":" in med["dosis"] else med["dosis"].split(" ")[0]
                            dose_per_kg = float(dose_str)
                            total_dose = dose_per_kg * weight
                            
                            # Mostrar dosis calculada manteniendo la descripción original
                            st.write(f"*Dosis Calculada:* {total_dose:.1f} mg")
                            st.write(f"*Base de Dosificación:* {med['dosis']}")
                            
                        except (ValueError, IndexError) as e:
                            st.error(f"Error en formato de dosis para {med['nombre']}: {str(e)}")
                            continue
                    else:
                        st.write(f"*Dosis:* {med.get('dosis', '--')}")
                    
                    # Resto de la información
                    st.write(f"*Frecuencia:* {med.get('intervalo', '--')}")  
                    st.write(f"*Vía:* {med.get('via', '--')}")  
                    st.write(f"*Duración:* {med.get('duracion', '--')}")

                    # Horarios de administración
                    if "Cada" in med.get('intervalo', ''):
                        try:
                            horas = int(med['intervalo'].split(" ")[1].replace("h",""))
                            next_dose = datetime.now().strftime("%H:%M")
                            siguiente_dosis = (datetime.now() + timedelta(hours=horas)).strftime("%H:%M")
                            st.write(f"⏰ *Próximas dosis (hoy):* {next_dose}, {siguiente_dosis}")
                        except Exception as e:
                            st.error(f"Error en formato de intervalo: {str(e)}")
            
            st.caption(f"📚 Fuente: {guidelines['fuente']}")

# Pestaña 2: Nutrición
with tab2:
    st.header("Cálculo Nutricional")
    
    if weight <= 0:
        st.error("Peso inválido.")
    else:
        # Requerimientos calóricos
        base_cal = 120 if gestational_age < 37 else 100
        protein_needs = 3.5 if gestational_age < 37 else 2.5
        lipid_needs = 3.0
        
        st.write(f"""
        *Requerimientos Diarios:*
        - Calorías: {base_cal * weight:.1f} kcal/día ({base_cal} kcal/kg)
        - Proteínas: {protein_needs * weight:.1f} g/día
        - Lípidos: {lipid_needs * weight:.1f} g/día
        """)



# Pestaña 4: Monitorización
with tab4:
    st.header("Monitorización de Crecimiento")
    
    # Gráfico de peso (ejemplo)
    days = list(range(1, postnatal_age + 1))
    weights = [weight + i*0.05 for i in range(postnatal_age)]
    
    fig, ax = plt.subplots()
    ax.plot(days, weights, marker='o', color='#1f77b4')
    ax.set_xlabel("Día de vida")
    ax.set_ylabel("Peso (kg)")
    ax.grid(linestyle='--', alpha=0.5)
    st.pyplot(fig)

# Pestaña 5: I/E
with tab5:
    st.header("Balance de Ingresos/Egresos (I/E)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ingresos (mL)")
        oral = st.number_input("Vía oral", 0, 500, 0)
        iv = st.number_input("Intravenoso", 0, 500, 120)
    
    with col2:
        st.subheader("Egresos (mL)")
        orina = st.number_input("Orina", 0, 500, 80)
        heces = st.number_input("Heces", 0, 500, 10)
    
    balance = (oral + iv) - (orina + heces)
    st.metric("Balance Neto", f"{balance} mL")


with tab6:
    st.header("Balance Hídrico y Electrolitos")
    
    # --- Velocidad de Infusión de Glucosa (GIR) ---
    st.subheader("Velocidad de Infusión de Glucosa (GIR)")
    dextrosa = st.number_input("Concentración de dextrosa (%)", 5, 20, 10)
    volumen_total = st.number_input("Volumen de líquidos IV (mL/kg/día)", 60, 200, 120)
    
    gir = (dextrosa * volumen_total) / (144 * weight) if weight > 0 else 0
    st.metric("GIR", f"{gir:.2f} mg/kg/min")
    if gir < 4:
        st.warning("GIR bajo: Aumentar concentración de dextrosa o volumen")
    elif gir > 6:
        st.warning("GIR alto: Considerar reducir dextrosa para evitar hiperglucemia")
    
    # --- Flujo Urinario ---
    st.subheader("Monitoreo de Diuresis")
    volumen_orina = st.number_input("Volumen de orina en 24h (mL)", 
                                   min_value=0, 
                                   max_value=1000, 
                                   value=200,
                                   help="Volumen total de orina recolectado en 24 horas")
    
    if weight > 0:
        flujo_urinario = (volumen_orina / weight) / 24
    else:
        flujo_urinario = 0
    
    st.metric("Flujo Urinario", f"{flujo_urinario:.2f} mL/kg/h")
    
    if flujo_urinario < 0.5:
        st.error("🚨 Anuria: Flujo urinario < 0.5 mL/kg/h - Evaluar función renal")
    elif flujo_urinario > 5:
        st.warning("⚠️ Poliuria: Flujo urinario > 5 mL/kg/h - Controlar balance hídrico")
    else:
        st.success("✅ Flujo urinario dentro de rango normal (0.5 - 5 mL/kg/h)")
    
    # --- Electrolitos en mL (para enfermería) ---
    st.subheader("Electrolitos en mL")
    if postnatal_age >= 2:
        col1, col2 = st.columns(2)
        with col1:
            concentracion_na = st.number_input("Concentración de NaCl (%)", 
                                              min_value=0.9, 
                                              max_value=10.0, 
                                              value=3.0, 
                                              step=0.1)
        with col2:
            concentracion_k = st.number_input("Concentración de KCl (%)", 
                                             min_value=5.0, 
                                             max_value=15.0, 
                                             value=10.0, 
                                             step=0.1)

        na_meq = 3.0 * weight
        k_meq = 2.0 * weight
        
        na_ml = na_meq / (concentracion_na * 0.171) if concentracion_na > 0 else 0
        k_ml = k_meq / (concentracion_k * 0.134) if concentracion_k > 0 else 0
        
        st.write(f"""
        *Sodio (NaCl {concentracion_na}%):*  
        - {na_meq:.1f} mEq/día → {na_ml:.1f} mL/día  
        
        *Potasio (KCl {concentracion_k}%):*  
        - {k_meq:.1f} mEq/día → {k_ml:.1f} mL/día  
        """)
    else:
        st.warning("No administrar electrolitos en primeras 48h")
# =================================================================
# EJECUCIÓN
# =================================================================
if __name__ == "_main_":
    st.write("Desarrollado por Willian y Andres | Basado en guías internacionales")