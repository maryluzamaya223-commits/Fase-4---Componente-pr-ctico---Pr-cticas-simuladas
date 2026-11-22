import logging
import uuid
import re
from abc import ABC, abstractmethod

# MARILUZ SUESCA AMAYA 
#MUCHACHOS ACÁ DEJO LA PRIMERA PARTE DE NUESTRO EJERCICIO, Y EN LA PARTE DE BAJO LO FALTANTE, REVISENLO POR FAVOR Y ESCOJAN SU PARTE, GRACIAS.
# PERSONA 01: ARQUITECTURA BASE Y SISTEMA DE LOGS
# Responsabilidad: Configurar el archivo de registro (sin BD) y definir la clase
# abstracta raíz 'Entidad' con generación automática de IDs y contrato base.


logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def registrar_evento(mensaje: str, nivel: str = "INFO"):
    """Registra eventos y errores en el archivo plano software_fj.log."""
    if nivel == "ERROR":
        logging.error(mensaje)
    elif nivel == "WARNING":
        logging.warning(mensaje)
    else:
        logging.info(mensaje)


class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""
    
    def __init__(self, entidad_id: str = None):
        self.__id = entidad_id if entidad_id else str(uuid.uuid4())[:8].upper()

    @property
    def id(self) -> str:
        return self.__id

    @abstractmethod
    def validar_integridad(self) -> bool:
        """Método obligatorio para verificar que el objeto sea válido."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        pass
class SoftwareFJError(Exception):
    """Excepción base para todos los errores controlados de Software FJ."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR-000"):
        self.codigo_error = codigo_error
        super().__init__(f"[{codigo_error}] {mensaje}")


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos ingresados no cumplen el formato o reglas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-DATOS")


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio inactivo u ocupado."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-DISPONIBILIDAD")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza al intentar transiciones de estado inválidas en reservas."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-OPERACION")


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando hay tarifas negativas, descuentos excesivos o errores matemáticos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR-CALCULO")

class Cliente(Entidad):
    """Representa un cliente de Software FJ con datos fuertemente encapsulados."""

    def __init__(self, nombre: str, email: str, telefono: str, cliente_id: str = None):
        super().__init__(cliente_id)
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.validar_integridad()
        registrar_evento(f"Cliente registrado exitosamente: {self.obtener_resumen()}")

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not valor or not re.match(patron, valor):
            raise DatoInvalidoError(f"El correo electrónico '{valor}' no tiene un formato válido.")
        self.__email = valor.lower().strip()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.isdigit() or len(valor) < 7:
            raise DatoInvalidoError("El teléfono debe contener solo números y mínimo 7 dígitos.")
        self.__telefono = valor

    def validar_integridad(self) -> bool:
        return all([self.__nombre, self.__email, self.__telefono])

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}]: {self.nombre} ({self.email})"

class Servicio(Entidad):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__()
        if not nombre or len(nombre.strip()) < 3:
            raise DatoInvalidoError("El nombre del servicio es inválido o está vacío.")
        if tarifa_base <= 0:
            raise CalculoInconsistenteError("La tarifa base debe ser mayor a cero.")
        
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def calcular_costo_base(self, horas: int) -> float:
        """Método polimórfico que cada subclase implementa según sus reglas."""
        pass

    def calcular_costo(self, horas: int, descuento: float = 0.0, aplicar_iva: bool = True, recargo_extra: float = 0.0) -> float:
        """
        Método sobrecargado mediante parámetros opcionales para calcular costos
        con variantes de descuentos, impuestos y recargos.
        """
        if horas <= 0:
            raise DatoInvalidoError("La duración en horas debe ser mayor a cero.")
        if not (0 <= descuento <= 0.5):
            raise CalculoInconsistenteError("El descuento debe estar entre 0% (0.0) y 50% (0.5).")
        if recargo_extra < 0:
            raise CalculoInconsistenteError("El recargo extra no puede ser negativo.")

        subtotal = self.calcular_costo_base(horas) + recargo_extra
        subtotal_con_descuento = subtotal * (1 - descuento)
        total = subtotal_con_descuento * 1.19 if aplicar_iva else subtotal_con_descuento
        return round(total, 2)

    def validar_integridad(self) -> bool:
        return self._tarifa_base > 0 and bool(self._nombre)


class ReservaSala(Servicio):
    """Servicio especializado para alquiler de salas de reuniones o capacitación."""
    def __init__(self, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        if capacidad < 2 or capacidad > 100:
            raise DatoInvalidoError("La capacidad de la sala debe estar entre 2 y 100 personas.")
        self.capacidad = capacidad

    def calcular_costo_base(self, horas: int) -> float:
        factor = 1.10 if self.capacidad > 20 else 1.0
        return self._tarifa_base * horas * factor

    def obtener_resumen(self) -> str:
        return f"Sala '{self.nombre}' (Capacidad: {self.capacidad} pers.) - ${self._tarifa_base}/h"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de hardware y equipos tecnológicos."""
    def __init__(self, nombre: str, tarifa_base: float, gama: str, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        if gama.lower() not in ["estandar", "alta"]:
            raise DatoInvalidoError("La gama del equipo debe ser 'estandar' o 'alta'.")
        self.gama = gama.lower()

    def calcular_costo_base(self, horas: int) -> float:
        seguro = 15.0 if self.gama == "alta" else 0.0
        return (self._tarifa_base * horas) + seguro

    def obtener_resumen(self) -> str:
        return f"Equipo '{self.nombre}' (Gama {self.gama}) - ${self._tarifa_base}/h"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de consultoría técnica o arquitectura de software."""
    def __init__(self, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        super().__init__(nombre, tarifa_base, disponible)
        if not especialidad:
            raise DatoInvalidoError("Debe especificar el área de especialidad.")
        self.especialidad = especialidad

    def calcular_costo_base(self, horas: int) -> float:
        if horas > 5:
            return (self._tarifa_base * horas) * 0.85
        return self._tarifa_base * horas

    def obtener_resumen(self) -> str:
        return f"Asesoría '{self.nombre}' [{self.especialidad}] - ${self._tarifa_base}/h"
class Reserva(Entidad):
    """Gestiona la relación entre un Cliente y un Servicio por un tiempo determinado."""

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: int, descuento: float = 0.0):
        super().__init__()
        
        # Validaciones previas a la creación de la reserva
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere instancias válidas de Cliente y Servicio.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")

        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.descuento = descuento
        self.estado = "PENDIENTE"
        
        # Uso del método sobrecargado calcular_costo()
        self.costo_total = self.servicio.calcular_costo(horas, descuento=descuento)
        self.validar_integridad()

    def confirmar(self):
        """Cambia el estado a CONFIRMADA y bloquea la disponibilidad del servicio."""
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado '{self.estado}'.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' ya fue ocupado.")

        self.estado = "CONFIRMADA"
        self.servicio.disponible = False
        registrar_evento(f"Reserva {self.id} CONFIRMADA | Cliente: {self.cliente.nombre} | Total: ${self.costo_total}")

    def cancelar(self):
        """Cambia el estado a CANCELADA y libera nuevamente el servicio."""
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")

        self.estado = "CANCELADA"
        self.servicio.disponible = True
        registrar_evento(f"Reserva {self.id} CANCELADA | Servicio '{self.servicio.nombre}' liberado.", "WARNING")

    def validar_integridad(self) -> bool:
        return self.costo_total > 0 and self.horas > 0

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | {self.cliente.nombre} -> {self.servicio.nombre} "
            f"({self.horas}h) | Estado: {self.estado} | Total: ${self.costo_total}"
        )


class SistemaSoftwareFJ:
    """Controlador principal del sistema. Gestiona toda la información en listas internas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        registrar_evento("=== INICIO DEL SISTEMA SOFTWARE FJ ===")

    def registrar_cliente(self, nombre: str, email: str, telefono: str):
        """Intenta crear y guardar un cliente usando try/except/else."""
        try:
            nuevo_cliente = Cliente(nombre, email, telefono)
        except SoftwareFJError as error:
            registrar_evento(f"Fallo al registrar cliente ({nombre}): {error}", "ERROR")
            print(f" Error controlado: {error}")
            return None
        else:
            # Solo se ejecuta si la creación fue exitosa
            self.clientes.append(nuevo_cliente)
            print(f"{nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente

    def agregar_servicio(self, servicio: Servicio):
        """Agrega un servicio válido al catálogo en memoria."""
        self.servicios.append(servicio)
        registrar_evento(f"Servicio agregado al catálogo: {servicio.obtener_resumen()}")
        print(f"Servicio agregado: {servicio.obtener_resumen()}")

    def procesar_reserva(self, cliente: Cliente, servicio: Servicio, horas: int, descuento: float = 0.0, confirmar_auto: bool = True):
        """
        Procesa una reserva completa aplicando:
        - try/except/else/finally
        - Encadenamiento de excepciones (raise ... from ...)
        """
        nueva_reserva = None
        try:
            nueva_reserva = Reserva(cliente, servicio, horas, descuento)
            if confirmar_auto:
                nueva_reserva.confirmar()
            self.reservas.append(nueva_reserva)

        except (ValueError, TypeError) as error_tecnico:
            # Encadenamiento de excepciones: transforma un error nativo de Python en uno de negocio
            try:
                raise CalculoInconsistenteError("Error interno de tipos de datos al calcular la reserva.") from error_tecnico
            except CalculoInconsistenteError as error_encadenado:
                registrar_evento(
                    f"Excepción encadenada: {error_encadenado} | Causa original: {error_encadenado.__cause__}",
                    "ERROR"
                )
                print(f" Error crítico encadenado: {error_encadenado}")

        except SoftwareFJError as error_negocio:
            registrar_evento(f"Reserva rechazada: {error_negocio}", "ERROR")
            print(f" Reserva rechazada: {error_negocio}")

        else:
            print(f"{nueva_reserva.obtener_resumen()}")

        finally:
            # Siempre se ejecuta al terminar el intento, haya fallado o no
            registrar_evento("Auditoría de transacción de reserva finalizada.")

        return nueva_reserva


 OPERACIONES COMPLETAS (EXITOSAS Y FALLIDAS)

if __name__ == "__main__":
    sistema = SistemaSoftwareFJ()

    print("\n--- 1. GESTIÓN DE CLIENTES ---")
    # Op 1 y 2: Registros exitosos
    cliente_1 = sistema.registrar_cliente("Laura Gómez", "laura.gomez@empresa.com", "3104567890")
    cliente_2 = sistema.registrar_cliente("Carlos Mendoza", "cmendoza@tech.co", "3209876543")
    
    # Op 3 y 4: Registros fallidos (el programa captura el error y continúa)
    sistema.registrar_cliente("Ana Perez", "ana_sin_arroba.com", "3001234567")
    sistema.registrar_cliente("Jo", "jo@mail.com", "ABC1234")

    print("\n--- 2. CREACIÓN DE SERVICIOS ---")
    # Op 5: Creación correcta de los 3 servicios especializados
    sala_norte = ReservaSala("Sala Ejecutiva Norte", 50.0, capacidad=25)
    servidor_dell = AlquilerEquipo("Servidor Dell PowerEdge", 35.0, gama="alta")
    asesoria_cloud = AsesoriaEspecializada("Arquitectura Cloud", 80.0, especialidad="AWS/Azure")

    sistema.agregar_servicio(sala_norte)
    sistema.agregar_servicio(servidor_dell)
    sistema.agregar_servicio(asesoria_cloud)

    # Op 6: Creación incorrecta de servicio (tarifa negativa)
    try:
        ReservaSala("Sala Fantasma", -20.0, capacidad=10)
    except SoftwareFJError as error:
        registrar_evento(f"Creación de servicio fallida: {error}", "ERROR")
        print(f"Error al crear servicio: {error}")

    print("\n--- 3. PROCESAMIENTO DE RESERVAS Y EXCEPCIONES ---")
    # Op 7: Reserva exitosa con descuento del 10%
    reserva_1 = sistema.procesar_reserva(cliente_1, sala_norte, horas=4, descuento=0.10)

    # Op 8: Intento fallido de reservar la misma sala (ocupada)
    sistema.procesar_reserva(cliente_2, sala_norte, horas=2)

    # Op 9: Cancelación válida + intento fallido de doble cancelación
    if reserva_1:
        reserva_1.cancelar()
        print(f" Estado actualizado: {reserva_1.obtener_resumen()}")
        try:
            reserva_1.cancelar()
        except SoftwareFJError as error:
            registrar_evento(f"Operación inválida controlada: {error}", "ERROR")
            print(f"Error controlado: {error}")

    # Op 10: Reserva exitosa de la sala tras haber sido liberada
    sistema.procesar_reserva(cliente_2, sala_norte, horas=3)

    # Op 11: Reserva fallida por descuento superior al permitido (> 50%)
    sistema.procesar_reserva(cliente_1, asesoria_cloud, horas=6, descuento=0.80)

    # Op 12: Prueba de encadenamiento de excepciones (dato tipo str en vez de int)
    sistema.procesar_reserva(cliente_1, servidor_dell, horas="cinco_horas")

    print("\n--- RESUMEN FINAL DEL SISTEMA ---")
    print(f"Total clientes activos: {len(sistema.clientes)}")
    print(f"Total servicios registrados: {len(sistema.servicios)}")
    print(f"Total reservas válidas procesadas: {len(sistema.reservas)}")
    print("Auditoría guardada en el archivo 'software_fj.log'.")

