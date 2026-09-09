import socket
import threading
from enum import Enum

from model.dataclass_amr import AmrConfig
from config.db_config import db_config
from helpers.estado_amr import EstadoAmr, Estado
from model.conexion import DAO

class Objetivosseguros(Enum):
    SAFETY_PLACE1 = "SAFETY_POS1"
    SAFETY_PLACE2 = "SAFETY_POS2"

class AMR(DAO):
    """
    Cliente TCP con un hilo dedicado a escuchar mensajes entrantes.
    Si la conexión se pierde, reintenta automáticamente con backoff
    exponencial hasta que el servidor vuelva o se llame disconnect().
    """
    INITIAL_DELAY = 1.0  # segundos entre el primer reintento
    MAX_DELAY = 30.0  # techo del backoff
    STATUS = ["Parking", "Going to", "Arrived at", "Charging", "Waiting", "Teleop", "Undocking", "Paused", "Lost", "Low Batery", "Failed", "Error"]

    def __init__(self,amr_config: AmrConfig):
        super().__init__(db_config)
        #self._version = 0
        self.alias = amr_config.alias
        self.objetivo = ""
        self._ip = amr_config.ip
        self._port = amr_config.puerto
        self._password = amr_config.password
        self._val = ""
        self._message = ""
        self._msg_ant = ["","",""]
        self.estado_amr = EstadoAmr()
        self._sock: socket.socket | None = None
        self._connected = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._listen,
            name="socket-listener",
            daemon=True,
        )

    

    def _update_db_amr_status_config(self, value):
        query = "UPDATE amr_config SET status = %s WHERE alias = %s"
        params = (value, self.alias)
        self.execute_commit(query, params)

    def _listen(self):
        delay = self.INITIAL_DELAY

        while not self._stop.is_set():
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("", f"[{self.alias}] Intentando conexión {self._ip}:{self._port}")
                self._sock.connect((self._ip, self._port))
                self._connected.set()
                delay = self.INITIAL_DELAY  # reset backoff tras conexión exitosa
                print("", f"[{self.alias}] Conectado a {self._ip}:{self._port}")
                self._update_db_amr_status_config("Conectando;-%;-°C")
                self._sock.sendall(f"{self._password}\n".encode('utf-8'))
                self._receive_loop()

            # disconnect() lanza OSError y termina limpiamente
            except OSError as e:
                if not self._stop.is_set():
                    print("", f"[{self.alias}] Error de conexión")
                    self._update_db_amr_status_config("Error de conexión;-%;-°C")
            finally:
                if self._sock:
                    self._sock.close()
                    self._sock = None

            if self._stop.is_set():
                break


            print("",f"[{self.alias}] Reintentando en {delay:.0f}s...")
            # Usa el evento _stop como temporizador para poder cancelar la espera
            self._stop.wait(timeout=delay)
            delay = min(delay * 2, self.MAX_DELAY) # Retorna el mínimo de los dos valores dados

        #print(f"[{self.alias}] Listener finalizado")
        print("", f"[{self.alias}] Listener finalizado")

    def _receive_loop(self):
        buffer = ""
        while not self._stop.is_set():
            self._sock.send("status\n".encode('utf-8')) # type: ignore
            chunk = self._sock.recv(1024) # type: ignore
            if not chunk:  # servidor cerró la conexión limpiamente
                print("", f"[{self.alias}] Servidor cerró la conexión")
                break
            buffer += chunk.decode("utf-8")
            while "\n" in buffer: # mientras haya al menos un mensaje completo
                line, buffer = buffer.split("\n", 1) # extrae el primero, deja el resto
                message = line.strip()
                if message:
                    self._on_message(message)

    def _check_msg_changes(self, message: str) -> bool:
        # Identificación de mensaje existente en la lista filtrando los mensajes vacíos
        if message in [m for m in self._msg_ant if m != ""]:
            return False

        self._msg_ant[0] = self._msg_ant[1]
        self._msg_ant[1] = self._msg_ant[2]
        self._msg_ant[2] = message
        return True

    def _update_status_amr_config(self, message: str):
        self.estado_amr.update_status(message) # Arma el estado actual del AMR
        estado = self.estado_amr.estado
        msg = f"{"Conectado" if not estado.Status else estado.Status};{estado.StateOfCharge}%;{estado.Temperature}°C"

        if self._check_msg_changes(msg):
            #Log.info("", f"Actualizando estado en {self.alias} : {msg}")
            self._update_db_amr_status_config(msg)


    def _on_message(self, message: str):
        """Callback invocado en el hilo listener por cada mensaje recibido."""
        try:
            key, val = message.split(":", 1)
            if key not in Estado.Estados:
                if self._val != val:
                    #if key not in vars(Estado):
                    print("", f"[{self.alias}] Mensaje recibido: {message}")
                self._val = val
        except ValueError:
            pass
        self._update_status_amr_config(message)

    # ------------------------------------------------------------------ #
    # METODOS públicos
    # ------------------------------------------------------------------ #

    def connect(self):
        """Inicia el hilo listener en background. Se conecta en cuanto el servidor esté disponible."""
        self._thread.start()

    def send(self, message: str):
        """Envía un mensaje. Lanza RuntimeError si no hay conexión activa."""
        if self._sock is None:
            raise RuntimeError("Sin conexión — esperando reconexión")
        self._sock.sendall((message + "\n").encode("utf-8"))

    def disconnect(self):
        """Detiene los reintentos, cierra el socket y espera que el hilo termine."""
        self._stop.set()
        if self._sock is not None:
            self._sock.close()
        self._thread.join(timeout=5.0)

    def is_connected(self) -> bool:
        return self._sock is not None

    def get_message(self) -> str:
        return self._message