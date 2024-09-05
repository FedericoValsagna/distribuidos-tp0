### Modo de Ejecución
#### Ejercicio 1
```
./generar-compose.sh docker-compose-dev.yaml 5
```
#### Ejercicio 2
```
./generar-compose.sh docker-compose-dev.yaml 5 && make docker-compose-up
```
#### Ejercicio 3
```
./generar-compose.sh docker-compose-dev.yaml 5 && ./validar-echo-server.sh
```
#### Ejercicio 4
```
./generar-compose.sh docker-compose-dev.yaml 5 && make docker-compose-up
```
#### Ejercicio 5
```
make docker-compose-up
```
#### Ejercicio 6 y 7
```
./generar-compose.sh docker-compose-dev.yaml 5 && make docker-compose-up
```
En caso de querer volver a ejecutar el ejercicio frenar el server.
