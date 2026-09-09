import json
from dataclasses import dataclass, field
from typing import Dict, Optional

# noinspection SpellCheckingInspection
@dataclass
class PisoConfig:
    tipo: str
    alias: str
    altura: int
    recibe: bool
    entregar: bool
    tipo_recibo: str
    tipo_entrega: str
    orientacion_magazine: str
    orientacion_permitida_amr: str
    recibe_de: list[str]
    funcion_alamacenamiento: bool = False
    #TODO agreagar parametro en base de datos

# noinspection SpellCheckingInspection
@dataclass
class PisosConfig:
    configs: Dict[str, PisoConfig] = field(default_factory=dict)

    @property
    def piso1(self) -> Optional[PisoConfig]:
        return self.configs.get("piso1")

    @property
    def piso2(self) -> Optional[PisoConfig]:
        return self.configs.get("piso2")

    # Opcional: acceso genérico si algún día hay más pisos
    def get_piso(self, clave: str) -> Optional[PisoConfig]:
        return self.configs.get(clave)

    # Opcional: para evitar None-checks constantes
    def tipo_entrega(self, clave: str = "piso1") -> str:
        piso = self.get_piso(clave)
        return piso.tipo_entrega if piso else "desconocido"

    def __getitem__(self, clave: str) -> Optional[PisoConfig]:
        return self.configs.get(clave)

    # noinspection PyArgumentList
    def __post_init__(self):
        """Se ejecuta automáticamente después de crear la instancia"""
        # Acepta tanto string JSON como dict directamente
        raw_data = self.configs  # ← lo que el usuario pasó

        if raw_data is None:
            raw_data = {}

        # Si viene como string JSON → lo parsea
        if isinstance(raw_data, str):
            try:
                raw_data = json.loads(raw_data)
            except (json.JSONDecodeError, TypeError):
                raw_data = {}

        # Aseguramos que siempre sea un dict
        if not isinstance(raw_data, dict):
            raw_data = {}

        # Conversión automática
        self.configs: Dict[str, PisoConfig] = {
            clave: PisoConfig(**config_dict) # type: ignore
            for clave, config_dict in raw_data.items()
        }

# noinspection SpellCheckingInspection
@dataclass
class PisosEstado:
    pisos: Dict[str, str] = field(default_factory=dict)

    @property
    def p1(self) -> str | None:
        return self.pisos.get("P1")

    @property
    def p2(self) -> str | None:
        return self.pisos.get("P2")

    def __post_init__(self):
        """Se ejecuta automáticamente después de crear la instancia"""
        # Acepta tanto string JSON como dict directamente
        raw_data = self.pisos  # ← lo que el usuario pasó

        if raw_data is None:
            raw_data = '{"P1":"","P2":""}'

        # Si viene como string JSON → lo parsea
        if isinstance(raw_data, str):
            try:
                raw_data = json.loads(raw_data)
            except (json.JSONDecodeError, TypeError):
                raw_data = {}

        # Aseguramos que siempre sea un dict

        if not isinstance(raw_data, dict):
            raw_data = {}

        # Sobrescribimos con la versión limpia
        self.pisos: Dict[str, str] = raw_data


# noinspection SpellCheckingInspection
@dataclass
class Estacion:
    id: int
    alias: str
    mac: str
    smema: str
    pisos_estado: PisosEstado
    servidor_acciones: dict[str,str]
    amr_estado: dict[str,str]
    tipo: str
    habilitado: bool
    modo_operacion: str
    recibe: list[str]
    coordenadas : dict[str,str]
    pisos_configuracion: PisosConfig
    ultima_modificacion: str

@dataclass
class Detectadas:
    id: int
    alias: str
    mac: str
    ip: str
    ultima_modificacion: str

    # MAC ADDRESS
    # IP

@dataclass
class ManagerConfig:
    id: int
    cfg_estaciones: str
    cfg_magazine: str

@dataclass
class EstacionConfig:
    id: int
    tipo_estacion: str
    prioridad_estacion: str
    tipo_magazine: str
    prioridad_magazine: str