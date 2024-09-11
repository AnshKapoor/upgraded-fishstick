import time
from datetime import datetime


import strictyaml
import path


if __name__ == "__main__":
    timeNs = time.time_ns()

    ba = bytearray(int(timeNs).to_bytes(8, 'big'))
    baInt = int.from_bytes(ba)

    dt = datetime.fromtimestamp(timeNs / 1000000000)
    print(dt)
    print(timeNs)


def test():
    schema = strictyaml.Map({
        "connections": strictyaml.Map({
            "spacewire": strictyaml.MapCombined({}, strictyaml.Str(), strictyaml.Map({
                "host": strictyaml.Str(),
                "port": strictyaml.Int(),
                strictyaml.Optional("sendChannel"): strictyaml.Int(),
                strictyaml.Optional("receiveChannel"): strictyaml.Int()
            })),
            "SPI": strictyaml.Map({
                "port": strictyaml.Str(),
                "baudrate": strictyaml.Int(),
                "timeout": strictyaml.Int()
            }),
            "powersupply": strictyaml.Map({
                "channel": strictyaml.Int(),
                "polling": strictyaml.Bool(),
                "polling_intervall": strictyaml.Int(),
                "port": strictyaml.Str(),
                "baudrate": strictyaml.Int()
            })
        })
    })

    inputFile = "config.yaml"
    parsedData = strictyaml.load(path.Path(inputFile).read_text(), schema).data

    for _ in parsedData["connections"]["spacewire"]:
        print(_)

    print(parsedData)
    print(parsedData["connections"]["spacewire"]["brickmk4"]["host"])


def timestmp():
    print(time.time_ns())

    ba = bytearray(int(time.time_ns()).to_bytes(8, 'big'))
    print(int.from_bytes(ba))


def abc():
    spacewire_connection_schema = Map({
        "host": Str(),
        "port": Int()
    })

    # Define the schema for the `spacewire` section
    spacewire_schema = Map({
        "brickmk4": spacewire_connection_schema,
        "gresb": spacewire_connection_schema,
        "shimafuji": spacewire_connection_schema
    })

    # Define the schema for the `SPI` section
    spi_schema = Map({
        "port": Str(),
        "baudrate": Int(),
        "timeout": Int()
    })

    # Define the schema for the `powersupply` section
    powersupply_schema = Map({
        "channel": Int(),
        "polling": Bool(),
        "polling_intervall": Int(),
        "port": Str(),
        "baudrate": Int()
    })

    # Define the top-level schema
    schema = Map({
        "connections": Map({
            "spacewire": spacewire_schema,
            "SPI": spi_schema,
            "powersupply": powersupply_schema
        })
    })
