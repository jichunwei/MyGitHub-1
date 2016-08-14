package ipc

import (
	"encoding/json"
	"server"
)

type IpcClient struct {
	conn chan string
}

func NewIpClient(server *server.IpcServer) *IpcClient {
	c := server.Connect()

	return &IpcClient{c}
}


func (client *IpcClient) Call(method, params string) (resp *server.Response, err error) {
	req := &server.Request{method, params}

	var b []byte
	b, err = json.Marshal(req)

	if err != nil {
		return
	}

	client.conn <- string(b)
	str := <-client.conn

	var respl server.Response
	err = json.Unmarshal([]byte(str), &respl)
	resp = &respl

	return
}

func (client *IpcClient) Close() {
	client.conn <- "CLOSE"
}
