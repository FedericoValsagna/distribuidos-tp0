#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"

cat ./template/head.txt > $1
for (( CLIENT=1 ; CLIENT<=$2 ; CLIENT++ )); do
    cat ./template/client.txt | tr "#" $CLIENT >> $1
done
cat ./template/tail.txt >> $1