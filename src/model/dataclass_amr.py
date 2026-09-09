from dataclasses import dataclass

@dataclass
class AmrConfig:
    id: int
    alias: str
    status: str
    elevador: str
    ip: str
    puerto: int
    password: str
    config: str


AMRs: list[AmrConfig] = []