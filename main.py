import numpy as np
# Necesitas instalar esta librería: pip install tabulate
from tabulate import tabulate 

def calcular_potencia(resistencias, corrientes_malla):
    """
    Calcula y devuelve un diccionario con la potencia disipada y la corriente 
    para cada resistencia.
    """
    resultados_resistencia = {}
    
    for nombre, info in resistencias.items():
        try:
            r = info['valor']
            
            if 'malla' in info:
                # Es una resistencia propia (no compartida)
                i = info['malla']
                # Se toma el índice 'i' para acceder a la corriente de malla
                corriente_resistor = corrientes_malla[i] 
                
            elif 'mallas' in info:
                # Es una resistencia compartida
                i, j = info['mallas']
                
                # La corriente es la diferencia de las corrientes de malla (I_i - I_j)
                # NOTA: Usamos np.abs() para asegurar que la potencia siempre sea positiva
                corriente_resistor = corrientes_malla[i] - corrientes_malla[j]
            
            # La potencia siempre es positiva, ya que se disipa (P = I^2 * R)
            potencia = (corriente_resistor**2) * r
            
            # Guardamos los resultados en el diccionario
            resultados_resistencia[nombre] = {
                'R': r,
                'Corriente (A)': np.abs(corriente_resistor), # Mostrar valor absoluto de la corriente en el componente
                'Potencia (W)': potencia
            }
            
        except Exception as e:
            resultados_resistencia[nombre] = {'R': r, 'Corriente (A)': 'ERROR', 'Potencia (W)': f'Error: {e}'}

    return resultados_resistencia

def main():
    """
    Función principal para la simulación de análisis de mallas con salida en tabla.
    """
    print("=============================================")
    print("  Simulador de Circuitos CC - Análisis de Mallas  ")
    print("=============================================")
    print("Basado en las Leyes de Kirchhoff (LVK)\n")

    # --- 1. Entrada del Usuario ---
    try:
        N = int(input("Ingrese el número total de mallas: "))
        if N <= 0:
            print("Error: El número de mallas debe ser positivo.")
            return
            
    except ValueError:
        print("Error: Entrada no válida. Debe ingresar un número.")
        return

    # Inicializar las matrices R (Resistencias) y V (Voltajes)
    matriz_R = np.zeros((N, N))
    vector_V = np.zeros(N)
    resistencias = {} # Diccionario para guardar resistencias

    print("\n--- 1. Configuración de Mallas ---")
    
    # Bucle para llenar la diagonal de R y el vector V
    for i in range(N):
        print(f"\n--- Configurando Malla {i+1} ---")
        try:
            # Llenar el Vector V 
            v_fuentes = float(input(f"  Suma de fuentes en Malla {i+1} (V) [Positivo si impulsa en sentido horario]: "))
            vector_V[i] = v_fuentes
            
            # Llenar la Diagonal de R (Resistencias propias)
            num_r_propias = int(input(f"  ¿Cuántas resistencias propias (no compartidas) tiene la Malla {i+1}?: "))
            
            suma_r_propias = 0
            for j in range(num_r_propias):
                r_val = float(input(f"    Valor Resistencia Propia {j+1} (Ohm): "))
                suma_r_propias += r_val
                # Guardamos la resistencia propia. El índice de malla es 'i'
                resistencias[f'R{i+1}_p{j+1}'] = {'valor': r_val, 'malla': i} 
            
            matriz_R[i, i] = suma_r_propias

        except ValueError:
            print("Error: Entrada no válida. Debe ser un número.")
            return

    # Bucle para llenar los elementos fuera de la diagonal (Resistencias compartidas)
    print("\n--- 2. Configuración de Resistencias Compartidas ---")
    for i in range(N):
        for j in range(i + 1, N): 
            try:
                r_comp = float(input(f"  Resistencia compartida entre Malla {i+1} y Malla {j+1} (Ohm) (0 si no hay): "))
                
                if r_comp > 0:
                    matriz_R[i, i] += r_comp
                    matriz_R[j, j] += r_comp
                    matriz_R[i, j] = -r_comp
                    matriz_R[j, i] = -r_comp
                    # Guardamos la resistencia compartida. Las mallas son 'i' y 'j'
                    resistencias[f'R_c{i+1}-{j+1}'] = {'valor': r_comp, 'mallas': (i, j)} 

            except ValueError:
                print("Error: Entrada no válida. Debe ser un número.")
                return

    # --- 3. Resolución y Resultados ---
    
    try:
        # Resolver el sistema: [R] * [I] = [V]
        corrientes_malla = np.linalg.solve(matriz_R, vector_V)
        
        # Obtener los resultados detallados de la potencia
        resultados_potencia = calcular_potencia(resistencias, corrientes_malla)
        
        
        # =========================================================
        # === GENERACIÓN DE LA TABLA FINAL ===
        # =========================================================

        print("\n\n################################################")
        print("###         ✅ RESULTADOS DEL ANÁLISIS ✅         ###")
        print("################################################")
        
        
        # --- A. Tabla de Corrientes de Malla (I) ---
        print("\n--- A. Corrientes de Malla (I) ---")
        
        # Preparar datos para la tabla I
        tabla_I_headers = ["Malla", "Corriente (A)"]
        tabla_I_data = []
        for i in range(N):
            tabla_I_data.append([
                f"I{i+1}", 
                f"{corrientes_malla[i]:.4f}" # 4 decimales para precisión
            ])
            
        print(tabulate(tabla_I_data, headers=tabla_I_headers, tablefmt="fancy_grid"))

        
        # --- B. Tabla de Componentes (R y P) ---
        print("\n--- B. Resultados por Componente (R, I, P) ---")
        
        # Preparar datos para la tabla R, I, P
        tabla_R_headers = ["Resistencia", "Valor (Ohm)", "Corriente (A)", "Potencia Disipada (W)"]
        tabla_R_data = []
        
        for nombre, datos in resultados_potencia.items():
            tabla_R_data.append([
                nombre, 
                f"{datos['R']:.1f}", 
                f"{datos['Corriente (A)']:.4f}",
                f"{datos['Potencia (W)']:.4f}"
            ])
            
        print(tabulate(tabla_R_data, headers=tabla_R_headers, tablefmt="fancy_grid"))
        
        # --- C. Potencia Total Disipada ---
        potencia_total = sum(d['Potencia (W)'] for d in resultados_potencia.values() if isinstance(d['Potencia (W)'], (int, float)))
        
        print("\n--- C. Potencia Total ---")
        print(f" Potencia Total Disipada en el circuito: {potencia_total:.4f} W")
        
        print("################################################")

    except np.linalg.LinAlgError:
        print("\n*** ERROR: Sistema Indeterminado ***")
        print("La matriz de resistencias (R) es singular. Revise el circuito.")
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado: {e}")

# Ejecutar la función principal
if __name__ == "__main__":
    main()