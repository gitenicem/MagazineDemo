import datetime


class Timer:
    """
    Timer de periodo fijo. Llama a tic() en tu loop principal;
    retorna True cada vez que haya transcurrido al menos `periodo` segundos.
    """

    def __init__(self, periodo: float):
        self.periodo = periodo
        self._ultima_ejecucion: datetime.datetime | None = None
        self.enabled = False

    def tic(self) -> bool:
        ahora = datetime.datetime.now()

        # Primera llamada: inicializa y dispara de inmediato
        if self._ultima_ejecucion is None and self.enabled:
            self._ultima_ejecucion = ahora
            return True

        if (ahora - self._ultima_ejecucion).total_seconds() >= self.periodo and self.enabled: # type: ignore
            self._ultima_ejecucion = ahora
            return True

        return False


    def reset(self):
        """Reinicia el timer como si nunca hubiera corrido."""
        self._ultima_ejecucion = None

    @property
    def transcurrido(self) -> float:
        """Segundos desde la última ejecución (0 si nunca ha corrido)."""
        if self._ultima_ejecucion is None:
            return 0.0
        return (datetime.datetime.now() - self._ultima_ejecucion).total_seconds()

    @property
    def restante(self) -> float:
        """Segundos que faltan para el próximo disparo (0 si ya es tiempo)."""
        return max(0.0, self.periodo - self.transcurrido)