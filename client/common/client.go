package common

import (
	"bufio"
	"fmt"
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
	BatchMax      int
}

type ClientBet struct {
	Name      string
	Surname   string
	ID        string
	Birthday  string
	BetNumber string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
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
func (c *Client) GracefulShutdown() {
	c.conn.Close()
	log.Infof("action: closing_socket | result: success")
}

func (c *Client) StartClient() {
	lines, readFileErr := c.ReadFile()
	if readFileErr != nil {
		log.Errorf("action: open_bets_file | result: fail | client_id: %v | error: %v",
			c.config.ID,
			readFileErr,
		)
		return
	}
	c.placeBets(lines)
	c.notifyForWinner()
}

func (c *Client) ReadFile() ([]string, error) {
	data, err := os.ReadFile(fmt.Sprintf("agencies/agency-%v.csv", c.config.ID))
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
		)
		return nil, err
	}
	var lines []string = strings.Split(string(data), "\r\n")
	return lines, nil
}
func (c *Client) placeBets(betLines []string) {
	c.createClientSocket()
	for i := 0; i <= len(betLines); i += c.config.BatchMax {
		batchSize := BatchSize(i, c.config.BatchMax, len(betLines))
		clientBets := GenerateClientsBets(betLines[i : i+batchSize])
		msg := BatchBetsMessage(c.config.ID, clientBets)
		// log.Infof("Sending message: %v", msg)
		c.conn.Write(msg)
		_, err := bufio.NewReader(c.conn).ReadString('\n')
		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
	}
}
func (c *Client) notifyForWinner() {
	c.conn.Write(FinishedBetsMessage(c.config.ID))
	// log.Infof("action: all_bets_sent | result: sucess |")
	msg, err := bufio.NewReader(c.conn).ReadString('\n')
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	winners := DecodeWinnersMessage(msg)
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(winners))
	c.conn.Close()
}

func BatchSize(i int, batchMax int, linesLength int) int {
	if linesLength-i < batchMax {
		return linesLength - i - 1
	} else {
		return batchMax
	}
}
