#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
cat templates/compose/head.txt | envsubst > $1
for i in $(seq $2); do
    CLI_ID=$i
    PATH_COMPLETO= pwd
    export CLI_ID
    export PATH_COMPLETO
    cat templates/compose/client.txt | envsubst >> $1
done
cat templates/compose/tail.txt >> $1
