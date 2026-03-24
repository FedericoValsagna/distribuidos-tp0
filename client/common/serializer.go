package common

import (
	"fmt"
	"strings"
)

func BetMessage(info *ClientInfo, id string) string {
	msg := fmt.Sprintf("%s%c%s%c%s%c%s%c%s%c%s", info.Nombre, Separator, info.Apellido, Separator, info.Documento, Separator, info.Nacimiento, Separator, info.Numero, Separator, id)
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
