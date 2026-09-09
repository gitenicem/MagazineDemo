class Estado:
    Estados = ["ExtendedStatusForHumans", "StateOfCharge", "Location", "LocalizationScore", "Temperature"]

    def __init__(self):
        self.Status = ""
        self.ExtendedStatusForHumans = ""
        self.StateOfCharge = ""
        self.Location = ""
        self.LocalizationScore = ""
        self.Temperature = ""


class EstadoAmr:

    def __init__(self):
        self.estado = Estado()
        self.status_ant = ""
        self.nuevo = False
        self.extendedStatus = False

    def check(self, val, key):
        if self.status_ant != val and key not in Estado.Estados:
            self.nuevo = True
        else:
            self.nuevo = False

    def update_status(self, message: str):
        try:
            key, val = message.split(":", 1)

            match key:
                case "Status":
                    if "DockingState:" not in message:
                        self.estado.Status = val
                        self.extendedStatus = False
                        self.status_ant = val
                    else:
                        self.extendedStatus = True
                case "ExtendedStatusForHumans":
                    if self.extendedStatus:
                        self.estado.Status = val
                        self.status_ant = val
                case "StateOfCharge":
                    self.estado.StateOfCharge = val
                case "Location":
                    self.estado.Location = val
                case "LocalizationScore":
                    self.estado.LocalizationScore = val
                case "Temperature":
                    self.estado.Temperature = val
                case "Error":
                    self.estado.Status = val
                case _:
                    if val:
                        #print(val)
                        pass

        except ValueError:
            pass