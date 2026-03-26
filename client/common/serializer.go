package common

import (
	"fmt"
	"strings"
)

const receivedMessage = "R"
const holdMessage = "S"
const notifyMessage = "N"
const askResultsMessage = "A"

// Given a bet it will return the serialized string message
func BetMessage(bet Bet) string {
	msg := fmt.Sprintf("%s%c%s%c%s%c%s%c%s%c", bet.Nombre, Separator, bet.Apellido, Separator, bet.Documento, Separator, bet.Nacimiento, Separator, bet.Numero, Separator)
	return msg
}

// Given an array of bets and the agency id it will return the serialized Batch message as a string
func BatchBetMessage(bets []Bet, id string) string {
	msg := "" + id + BetSeparator
	for i := 0; i < len(bets); i++ {
		bet_msg := BetMessage(bets[i])
		msg += bet_msg
		if i < len(bets)-1 {
			msg += BetSeparator
		}
	}
	return msg
}

// Given a message it fills the string so it matches the packet length
func FillPadding(msg string) string {
	extraPaddingRequired := PacketSize - len([]byte(msg))
	extraPadding := strings.Repeat(Padding, extraPaddingRequired)
	msg += extraPadding
	return msg
}

// Removes the padding of the message
func ParseMessage(msg string) string {
	return RemovePadding(msg)
}

// Removes the padding of the message
func RemovePadding(msg string) string {
	return strings.Split(msg, Padding)[0]
}

// Given the agency id it returns the Notify message as a string
func NotifyMessage(agencyID string) string {
	msg := notifyMessage + BetSeparator + agencyID
	return msg
}

// Given the agency id it returns the asking results message as a string
func AskResultsMessage(agencyID string) string {
	msg := askResultsMessage + BetSeparator + agencyID
	return msg
}

// Given a message it returns the values from the message
func SplitMsg(msg string) []string {
	return strings.Split(msg, BetSeparator)
}
