package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"strings"
)

func PlaceBetMessage(clientID string, clientBet ClientBet) []byte {
	var payload string = "%v_%v_%v_%v_%v_%v"
	payload = fmt.Sprintf(payload,
		clientID,
		clientBet.Name,
		clientBet.Surname,
		clientBet.ID,
		clientBet.Birthday,
		clientBet.BetNumber)
	return formMessage("B_", payload)
}

func BatchBetsMessage(clientID string, clientsBet []ClientBet) []byte {
	var payload = fmt.Sprintf("%v_", clientID)
	for _, bet := range clientsBet {
		var payloadLine string = fmt.Sprintf("%v_%v_%v_%v_%v$",
			bet.Name,
			bet.Surname,
			bet.ID,
			bet.Birthday,
			bet.BetNumber)
		payload += payloadLine
	}
	payload = strings.TrimSuffix(payload, "$")
	return formMessage("G_", payload)
}
func FinishedBetsMessage(clientID string) []byte {
	return formMessage("F_", clientID)
}

func GenerateClientBet(line string) ClientBet {
	fields := strings.Split(line, ",")
	return ClientBet{
		Name:      fields[0],
		Surname:   fields[1],
		ID:        fields[2],
		Birthday:  fields[3],
		BetNumber: fields[4],
	}
}

func GenerateClientsBets(lines []string) []ClientBet {
	clientBets := make([]ClientBet, len(lines))
	for i, line := range lines {
		clientBets[i] = GenerateClientBet(line)
	}
	return clientBets
}

func DecodeWinnersMessage(msg string) []string {
	msg = strings.TrimSuffix(msg, "\n")
	msg = strings.TrimSuffix(msg, "_")
	lines := strings.Split(msg, "_")
	lines = lines[1:]
	return lines
}
func formMessage(opcode string, payload string) []byte {
	var payloadLength uint32 = uint32(len(payload))
	buf := new(bytes.Buffer)
	_ = binary.Write(buf, binary.BigEndian, payloadLength)
	payloadLenghtAsBytes := (buf.Bytes())
	var header []byte = append([]byte(opcode), payloadLenghtAsBytes...)
	header = append(header, []byte("_")...)
	msg := append(header, []byte(payload)...)
	return []byte(msg)
}
