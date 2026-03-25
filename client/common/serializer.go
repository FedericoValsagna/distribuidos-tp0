package common

import (
	"fmt"
	"strings"
)

func BetMessage(bet Bet) string {
	msg := fmt.Sprintf("%s%c%s%c%s%c%s%c%s%c", bet.Nombre, Separator, bet.Apellido, Separator, bet.Documento, Separator, bet.Nacimiento, Separator, bet.Numero, Separator)
	return msg
}

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

func FillPadding(msg string) string {
	extraPaddingRequired := PacketSize - len([]byte(msg))
	extraPadding := strings.Repeat(Padding, extraPaddingRequired)
	msg += extraPadding
	return msg
}

func ParseMessage(msg string) string {
	return RemovePadding(msg)
}
func RemovePadding(msg string) string {
	return strings.Split(msg, Padding)[0]
}

func NotifyMessage(agencyID string) string {
	msg := "N!" + agencyID
	return msg
}

func AskResultsMessage(agencyID string) string {
	msg := "A!" + agencyID
	return msg
}

func SplitMsg(msg string) []string {
	return strings.Split(msg, "!")
}
