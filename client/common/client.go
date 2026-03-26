package common

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"strings"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}
type ClientInfo struct {
	Nombre     string
	Apellido   string
	Documento  string
	Nacimiento string
	Numero     string
}

// Client Entity that encapsulates how
type Client struct {
	config  ClientConfig
	conn    net.Conn
	running bool
	info    ClientInfo
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, info ClientInfo) *Client {
	client := &Client{
		config: config,
		info:   info,
	}
	client.running = true
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// Messages if the message amount threshold has not been surpassed
	// Create the connection the server in every loop iteration. Send an
	c.createClientSocket()
	msg := ParseClientInfo(&c.info, c.config.ID)
	io.WriteString(c.conn, msg)
	// fmt.Fprintf(c.conn, msg)
	// log.Debugf("Mensaje enviado: '%s'", msg)
	buffer := make([]byte, PacketSize)
	_, err := io.ReadFull(bufio.NewReader(c.conn), buffer)
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	msg = string(buffer)
	// log.Debugf("Mensaje recibido: '%s'", msg)
	msg = ParseMessage(msg)
	if msg == "Apuesta recibida" {
		log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %s", c.info.Documento, c.info.Numero)
	}

	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		c.config.ID,
		msg,
	)
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	c.conn.Close()
}

func (c *Client) GracefulShutdown() {
	c.running = false
	c.conn.Close()
	log.Infof("action: closing_socket | result: success")
}

func ParseClientInfo(info *ClientInfo, id string) string {
	msg := fmt.Sprintf("%s%c%s%c%s%c%s%c%s%c%s", info.Nombre, Separator, info.Apellido, Separator, info.Documento, Separator, info.Nacimiento, Separator, info.Numero, Separator, id)
	msg = FillPadding(msg)
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
