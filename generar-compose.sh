#!/bin/bash
TEMP="temp.txt"
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
PWD=$(pwd | tr "/" "$")
cat ./template/head.txt > $TEMP
for (( CLIENT=1 ; CLIENT<=$2 ; CLIENT++ )); do
    cat ./template/client.txt | tr "#" $CLIENT >> $TEMP
done
cat ./template/tail.txt >> $TEMP
sed -i "s/PWD/$PWD/g" $TEMP
cat $TEMP | tr "$" "/" > $1
rm $TEMP
