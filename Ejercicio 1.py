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

# PERSONA 02: MANEJO AVANZADO DE EXCEPCIONES
# Debes crear una jerarquía de excepciones personalizadas para capturar fallos del negocio sin detener la ejecución de la aplicación.

class SoftwareFJException(Exception):
    """
    Excepción base del sistema.
    Todas las excepciones personalizadas deben heredar de esta clase.
    """

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje


# ----------------------------
# EXCEPCIONES DE CLIENTES
# ----------------------------

class ClienteException(SoftwareFJException):
    """Errores relacionados con clientes."""
    pass


class ClienteInvalidoError(ClienteException):
    """Datos inválidos en el registro del cliente."""
    pass


class CorreoInvalidoError(ClienteException):
    """Formato incorrecto de correo electrónico."""
    pass


class DocumentoInvalidoError(ClienteException):
    """Documento no válido."""
    pass


# ----------------------------
# EXCEPCIONES DE SERVICIOS
# ----------------------------

class ServicioException(SoftwareFJException):
    """Errores relacionados con servicios."""
    pass


class ServicioNoDisponibleError(ServicioException):
    """Servicio fuera de disponibilidad."""
    pass


class ParametroServicioError(ServicioException):
    """Parámetros inválidos para el servicio."""
    pass


class CostoInvalidoError(ServicioException):
    """Costo incorrecto o inconsistente."""
    pass


# ----------------------------
# EXCEPCIONES DE RESERVAS
# ----------------------------

class ReservaException(SoftwareFJException):
    """Errores relacionados con reservas."""
    pass


class ReservaDuplicadaError(ReservaException):
    """Intento de crear una reserva ya existente."""
    pass


class ReservaCanceladaError(ReservaException):
    """La reserva ya fue cancelada."""
    pass


class ReservaNoValidaError(ReservaException):
    """La reserva contiene información incorrecta."""
    pass


# ----------------------------
# EXCEPCIONES DE PROCESAMIENTO
# ----------------------------

class OperacionNoPermitidaError(SoftwareFJException):
    """Operación no autorizada o fuera de flujo."""
    pass


class ErrorProcesamientoSistema(SoftwareFJException):
    """Error general del sistema."""
    pass

# PERSONA 03: GESTIÓN DE CLIENTES Y ENCAPSULACIÓN
# Debes implementar la clase Cliente heredando de Entidad, aplicando encapsulación estricta y validaciones en setters para datos personales, cómo
#  se nos pide en la guía.

# PERSONA 04: SERVICIOS ESPECIALIZADOS, POLIMORFISMO Y SOBRECARGA
# Debes desarrollar la clase abstracta Servicio y las 3 subclases (ReservaSala, AlquilerEquipo, AsesoriaEspecializada) con cálculo polimórfico
# y no olvides lasobrecarga de métodos mediante parámetros opcionales.

# PERSONA 05: GESTIÓN DE RESERVAS, CONTROLADOR CENTRAL Y SIMULACIÓN
# Debes implementar la clase Reserva, el controlador en memoria (listas internas), bloques try/except/else/finally, encadenamiento de
# excepciones y ejecutar la simulación de 12 operaciones completas.
