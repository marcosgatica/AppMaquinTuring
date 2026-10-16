class MaquinaTuringDPI:
    def __init__(self, cadena_entrada, metodo="FLEXIBLE"):
        # 1. ¿Cadena a analizar? (Agregamos 'B' al final como símbolo de fin de cinta)
        self.cinta = list(cadena_entrada) + ['B']
        self.cabezal = 0
        self.estado_actual = 'q0'
        
        # 2. ¿Alfabeto a utilizar?
        self.digitos = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
        self.separadores = {'-', ' '}
        
        # 3. ¿Número de Nodos? (Generamos los estados q0 a q13, más qa y qr)
        self.metodo = metodo
        self.transiciones = self._generar_tabla_transiciones()
        self.historial = []

    def _generar_tabla_transiciones(self):
        tabla = {}
        # Generamos la lógica para contar exactamente 13 dígitos
        for i in range(14):
            estado = f'q{i}'
            
            # Si lee un dígito, avanza al siguiente estado y se mueve a la derecha (R)
            for d in self.digitos:
                if i < 13:
                    tabla[(estado, d)] = (f'q{i+1}', d, 'R')
                else:
                    # Si ya leyó 13 dígitos y viene otro, rechaza (DPI muy largo)
                    tabla[(estado, d)] = ('qr', d, 'S') 

            # Si lee un separador (guion o espacio)
            for s in self.separadores:
                if self.metodo == "FLEXIBLE" and i < 13:
                    # Lo limpia (escribe B), se queda en el mismo estado esperando el dígito, y mueve a R
                    tabla[(estado, s)] = (estado, 'B', 'R')
                else:
                    # En método estricto, o si hay separadores extras al final, rechaza
                    tabla[(estado, s)] = ('qr', s, 'S')

        # Condición de aceptación: Si está en q13 y lee el fin de cinta 'B'
        tabla[('q13', 'B')] = ('qa', 'B', 'S')  # S = Stop
        
        return tabla

    def procesar(self):
        # 4. ¿Método de solución? (Ejecución de la máquina)
        paso = 1
        
        while self.estado_actual not in ['qa', 'qr']:
            # Leer el símbolo actual de la cinta
            simbolo_leido = self.cinta[self.cabezal] if self.cabezal < len(self.cinta) else 'B'
            
            # Buscar la transición
            clave = (self.estado_actual, simbolo_leido)
            
            if clave in self.transiciones:
                nuevo_estado, simbolo_escrito, movimiento = self.transiciones[clave]
                
                # Guardar el registro para el frontend (historial)
                self.historial.append({
                    "paso": paso,
                    "estado_origen": self.estado_actual,
                    "lee": simbolo_leido,
                    "escribe": simbolo_escrito,
                    "movimiento": movimiento,
                    "estado_destino": nuevo_estado
                })
                
                # Ejecutar la acción en la cinta
                self.cinta[self.cabezal] = simbolo_escrito
                self.estado_actual = nuevo_estado
                
                # Mover el cabezal
                if movimiento == 'R':
                    self.cabezal += 1
                elif movimiento == 'L':
                    self.cabezal -= 1
                    
                paso += 1
            else:
                # Si no hay transición definida (ej. leyó una letra), se va a sumidero
                self.historial.append({
                    "paso": paso,
                    "estado_origen": self.estado_actual,
                    "lee": simbolo_leido,
                    "escribe": simbolo_leido,
                    "movimiento": 'S',
                    "estado_destino": 'qr'
                })
                self.estado_actual = 'qr'

        cinta_final = "".join(self.cinta).replace("B", "") # Quitamos los blancos para ver el DPI limpio
        
        return {
            "estado_final": "ACEPTADO" if self.estado_actual == 'qa' else "RECHAZADO",
            "cinta_resultante": cinta_final,
            "transiciones": self.historial
        }

# --- PRUEBA LOCAL ---
if __name__ == "__main__":
    # DPI con guiones y espacios (Método Flexible)
    dpi_prueba = "1234-56789 0101"
    
    print(f"Analizando cadena: {dpi_prueba}")
    maquina = MaquinaTuringDPI(dpi_prueba, metodo="FLEXIBLE")
    resultado = maquina.procesar()
    
    print(f"Resultado final: {resultado['estado_final']}")
    print(f"Cinta limpia resultante: {resultado['cinta_resultante']}")
    print(f"Total de nodos (pasos) recorridos: {len(resultado['transiciones'])}")