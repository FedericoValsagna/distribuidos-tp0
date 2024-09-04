package common

import "fmt"

func PlaceBetMessage(client_ID string, client_bet ClientBet) []byte {
	var payload string = "%v_%v_%v_%v_%v_%v"
	payload = fmt.Sprintf(payload,
		client_ID,
		client_bet.Name,
		client_bet.Surname,
		client_bet.ID,
		client_bet.Birthday,
		client_bet.BetNumber)

	var payloadLength rune = rune(len(payload))
	var header string = "B_" + string(payloadLength) + "_"
	return []byte(header + payload)
}
