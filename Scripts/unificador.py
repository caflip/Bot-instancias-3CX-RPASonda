import pandas as pd
import Scripts.utils as RPA


def unificar_reportes(ruta_reportes, nombre_reportes, ruta_salida, auditoria, fila_auditoria):
    try:
        # Crear un DataFrame vacío para almacenar los datos unificados
        df_unificado = pd.DataFrame()

        # Columnas clave (A a M) para identificar duplicados
        columnas_clave = [
            "Call Time", "From", "To", "Direction", "Status",
            "Ringing", "Talking", "Cost", "Call Activity Details", 
            "Sentiment", "Summary", "Transcription"
        ]

        for idx, nombre_reporte in enumerate(nombre_reportes):
            ruta_completa = f"{ruta_reportes}/{nombre_reporte}"
            df = pd.read_csv(ruta_completa)

            # 1. Eliminar filas que contienen "Totals"
            df = df[~df.apply(lambda row: row.astype(str).str.contains("Totals", case=False, na=False).any(), axis=1)]

            # 2. Agregar columna de origen
            df['Origen'] = nombre_reporte.split('.')[0]

            # Asegurar que las columnas clave existen y son string
            for col in columnas_clave:
                if col in df.columns:
                    df[col] = df[col].astype(str)
                if col in df_unificado.columns:
                    df_unificado[col] = df_unificado[col].astype(str)

            # 3. Desde el segundo reporte, evitar duplicados comparando con el acumulado
            if not df_unificado.empty:
                # Forzar a string las columnas clave en ambos DataFrames
                for col in columnas_clave:
                    if col in df.columns:
                        df[col] = df[col].astype(str)
                    if col in df_unificado.columns:
                        df_unificado[col] = df_unificado[col].astype(str)

                df = df.merge(
                    df_unificado[columnas_clave],
                    how="left",
                    indicator=True,
                    on=columnas_clave
                )
                df = df[df["_merge"] == "left_only"]
                df.drop(columns=["_merge"], inplace=True)


            # 4. Agregar al DataFrame unificado
            df_unificado = pd.concat([df_unificado, df], ignore_index=True)

        # Obtener fecha actual
        fecha_actual = RPA.obtenerFechaActual()
        ruta_unificado = f"{ruta_salida}/Reporte_Unificado_Instancias_3CX-{fecha_actual}.xlsx"
        df_unificado = RPA.limpiar_vacios(df_unificado)
        # Guardar el DataFrame unificado en un archivo Excel
        df_unificado.to_excel(ruta_unificado, index=False)

        # Eliminar archivos originales
        for nombre_reporte in nombre_reportes:
            ruta_completa = f"{ruta_reportes}/{nombre_reporte}"
            RPA.eliminarArchivo(ruta_completa)

        # Auditoría
        fila_auditoria = RPA.diligenciarAuditoria(
            auditoria,
            ["Unificación de reportes", f"Reporte unificado creado: {ruta_unificado}"],
            fila_auditoria
        )

        print(f"Reporte unificado guardado en: {ruta_unificado}")
        return True, ruta_unificado, fila_auditoria

    except Exception as e:
        print(f"Error al unificar reportes: {e}")
        fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Unificación de reportes", str(e)], fila_auditoria)
        return False, None, fila_auditoria
