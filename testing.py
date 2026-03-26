
def convert_to_bytes(string):
    b = bytes(string, "utf-8")
    return b


FILEPATH = ["./.data/agency-1.csv", "./.data/agency-2.csv", "./.data/agency-3.csv", "./.data/agency-4.csv","./.data/agency-5.csv"]


files = {}
files["nombre"] = []
files["apellido"] = []
files["documento"] = []
files["fecha"] = []
files["numero"] = []

for filepath in FILEPATH:
    with open(filepath) as file:
        for line in file.readlines():
            line = line.rstrip()
            line = line.split(",")
            files["nombre"].append(line[0])
            files["apellido"].append(line[1])
            files["documento"].append(line[2])
            files["fecha"].append(line[3])
            files["numero"].append(line[4])


print(f"Cantidad de registros: {len(files["nombre"])}")
arraybytes = list(map(convert_to_bytes, files["numero"]))
largos = list(map(len, arraybytes))
print(max(largos))

# Nombre mas largo 23
# Apellido mas largo 10
# Documento 8
# Fecha 10
# Numero 4

## 55 bytes de info
# 4 mas de separadores
# Tamaño de paquete 59


