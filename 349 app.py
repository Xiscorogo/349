import streamlit as st
import pandas as pd
import io

# Función para generar el archivo TXT con el formato AEAT
def generar_txt(datos_declarante, df_operadores):
    output = io.StringIO()
    
    # Registro Tipo 1 - Identificación del Declarante
    registro_tipo_1 = (
        "1" +  # Tipo de Registro
        "349" +  # Modelo de declaración
        "2024" +  # Año fiscal
        datos_declarante["nif"].rjust(9) +  # NIF del declarante
        datos_declarante["razon_social"].ljust(40)[:40] +  # Nombre de la sociedad
        " " +  # Espacio en blanco
        datos_declarante["telefono"].rjust(9) +  # Teléfono
        datos_declarante["representante"].ljust(40)[:40] +  # Nombre del representante
        "3490000000000" +  # Número de identificación
        datos_declarante["mes"].zfill(2) +  # Mes de presentación
        str(len(df_operadores)).zfill(13) +  # Número de perceptores
        str(df_operadores["Base"].sum()).replace(".", "").zfill(13) +  # Suma total de bases imponibles
        " " * (500 - 147)  # Relleno hasta 500 caracteres
    )

    output.write(registro_tipo_1 + "\n")

    # Registro Tipo 2 - Operadores Intracomunitarios
    for _, row in df_operadores.iterrows():
        registro_tipo_2 = (
            "2" +  # Tipo de Registro
            "349" +  # Modelo de declaración
            "2024" +  # Año fiscal
            datos_declarante["nif"].rjust(9) +  # NIF del declarante
            " " * 67 +  # Espacios en blanco según AEAT
            row["VIES"][:2] +  # Código del país
            row["VIES"].ljust(15)[:15] +  # NIF Operador Comunitario
            row["Nombre"].ljust(40)[:40] +  # Razón Social del Operador
            row["Indicador"][:1] +  # Clave de operación
            str(row["Base"]).replace(".", "").zfill(13) +  # Base Imponible
            " " * (500 - 147)  # Relleno hasta 500 caracteres
        )
        output.write(registro_tipo_2 + "\n")

    return output.getvalue()

# Configurar la aplicación Streamlit
st.title("📄 Generador del Modelo 349 - AEAT")
st.write("Sube un archivo Excel con los operadores intracomunitarios y genera un `.txt` en el formato oficial de la AEAT.")

# Formulario para los datos del declarante
st.header("1️⃣ Datos del Declarante")
nif = st.text_input("📌 NIF del declarante", "")
razon_social = st.text_input("🏢 Nombre de la sociedad", "")
telefono = st.text_input("📞 Teléfono de contacto", "")
representante = st.text_input("👤 Nombre del representante", "")
mes = st.selectbox("📅 Mes de presentación", [str(i).zfill(2) for i in range(1, 13)])

# Subida de archivo Excel
st.header("2️⃣ Subir Archivo Excel con los Operadores Intracomunitarios")
archivo_subido = st.file_uploader("📂 Selecciona un archivo Excel (.xlsx)", type=["xlsx"])

if archivo_subido:
    try:
        df_operadores = pd.read_excel(archivo_subido)
        # Verificar que las columnas sean correctas
        columnas_requeridas = ["Código", "VIES", "Nombre", "Indicador", "Base", "País"]
        if not all(col in df_operadores.columns for col in columnas_requeridas):
            st.error("❌ El archivo no contiene todas las columnas requeridas. Verifica que tenga las siguientes: Código, VIES, Nombre, Indicador, Base, País.")
        else:
            st.success("✅ Archivo cargado correctamente.")
            
            # Procesar el archivo y generar el TXT
            datos_declarante = {
                "nif": nif,
                "razon_social": razon_social,
                "telefono": telefono,
                "representante": representante,
                "mes": mes
            }
            contenido_txt = generar_txt(datos_declarante, df_operadores)

            # Permitir descarga del archivo
            st.download_button(
                label="⬇️ Descargar Archivo TXT",
                data=contenido_txt,
                file_name="Modelo_349_AEAT.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
