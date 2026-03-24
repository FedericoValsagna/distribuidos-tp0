package common

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"os"
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
	BatchAmount   int
}
type Bet struct {
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
	info    Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, info Bet) *Client {
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

	fmt.Println("BATCH AMOUNT:", c.config.BatchAmount)

	file, err := os.Open(fmt.Sprintf(AgencyFilepath, c.config.ID))
	if err != nil {
		log.Errorf("Error reading file")
		return
	}
	keepLooping := true
	for keepLooping {
		c.createClientSocket()
		bets, err := GetNextBets(file, c.config.BatchAmount)
		if err == io.EOF {
			keepLooping = false
		}
		msg := BatchBetMessage(bets, c.config.ID)
		c.SendMessage(msg)
		msg, err = c.ReceiveMessage()
		if err != nil {
			c.conn.Close()
			return
		}
		if msg == "Apuesta recibida" {
			log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %s", c.info.Documento, c.info.Numero)
		}
		c.conn.Close()
	}
	c.conn.Close()
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) SendMessage(msg string) {
	msg = FillPadding(msg)
	fmt.Println("Message sent:", msg)
	io.WriteString(c.conn, msg)
}

func (c *Client) ReceiveMessage() (string, error) {
	buffer := make([]byte, PacketSize)
	_, err := io.ReadFull(bufio.NewReader(c.conn), buffer)
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return "", err
	}
	msg := string(buffer)
	ParseMessage(msg)
	log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
		c.config.ID,
		msg,
	)
	return msg, nil
}

func (c *Client) GracefulShutdown() {
	c.running = false
	c.conn.Close()
	log.Infof("action: closing_socket | result: success")
}

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

func lineToClientInfo(line string) Bet {
	// fmt.Println("LINEA:", x)
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
