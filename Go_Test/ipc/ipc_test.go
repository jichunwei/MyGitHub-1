package ipc

import (
	"testing"
	"server"
)

type EchoServer struct {
}

func (server *EchoServer) Handle(request string) string {
	return "ECHO:" + request
}

func (server *EchoServer) Name() string {
	return "EchoServer"
}

func TestIpc(t *testing.T) {
	server := server.NewIpcServer(&EchoServer{})

	client1 := NewIpClient(server)
	client2 := NewIpClient(server)

	resp1 := client1.Call("From client1")
	resp2 := client1.Call("From client2")

	if resp1 != "ECHO: From Client" || resp2 != "ECHO: From Client2" {
		t.Error("IpcClient.Call failed. resp1:", resp1, "resp2:", resp2)
	}

	client1.Close()
	client2.Close()

}
