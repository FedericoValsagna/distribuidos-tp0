package common

import (
	"io"
	"os"
	"strings"
)

// Given an open file it returns the text in string format until it reaches a newline character or an End of File.
func ReadLine(f *os.File) (string, error) {
	buf := make([]byte, 1)
	byteArray := make([]byte, 0)
	for {
		_, err := f.Read(buf)
		if err != nil && err != io.EOF {
			return "", err
		}
		if err == io.EOF {
			line := string(byteArray)
			return line, err
		}
		if string(buf) == "\n" {
			break
		}
		byteArray = append(byteArray, buf[0])
	}
	line := string(byteArray)
	return line, nil

}

// Given a file line it will return the corresponding bet
func lineToClientInfo(line string) Bet {
	values := strings.Split(line, ",")
	clientInfo := Bet{
		Nombre:     values[0],
		Apellido:   values[1],
		Documento:  values[2],
		Nacimiento: values[3],
		Numero:     values[4],
	}
	return clientInfo
}

// Given the file it returns the next corresponding bets in an array of the given amount length or less if it reaches the end of file.
func GetNextBets(file *os.File, amount int) ([]Bet, error) {
	bets := make([]Bet, 0)
	for i := 0; i < amount; i++ {
		bet, err := GetNextBet(file)
		if err == io.EOF {
			return bets, err
		}
		if err != nil {
			return bets, err
		}
		bets = append(bets, bet)
	}
	return bets, nil
}

// Given the file it will return the next corresponding bet
func GetNextBet(file *os.File) (Bet, error) {
	line, err := ReadLine(file)
	if err == io.EOF {
		if len(line) > 0 {
			return lineToClientInfo(line), err
		}
		return Bet{}, err
	}
	if err != nil {
		return Bet{}, err
	}
	return lineToClientInfo(line), nil
}
