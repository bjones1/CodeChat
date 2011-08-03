// camerasock.cpp : Defines the entry point for the console application.<br />*******************************************************<br />Process: CP Client<br />Author:      Jacob Bowen<br />Description: This process sends either a TCP or UDP 
//              message to a server based on the 
//              command-line arguments that it is given.
//              It then waits for a response.
// *******************************************************

using namespace std;

#pragma (lib, "Ws2_32.lib")

#include "stdafx.h"
#include <winsock2.h>
#include <conio.h>
#include <iostream>
#include <string>


#define EXIT_SUCCESS    0
#define EXIT_ERROR      1
#define TCP_PROTOCOL    6
#define UDP_PROTOCOL    17
#define TCP             1
#define UDP             2
#define MSG_SIZE        7
#define MIN_BUFFER_SIZE 1

// Note: calling this _tmain confuses the command-line args passed (since <a href="http://stackoverflow.com/questions/895827/what-is-the-difference-between-tmain-and-main-in-c">everything gets passed in UTF-16</a>). It also breaks all the networking. <br />
int main(int argc, char* argv[])
{
    if (argc < 3)
    {
        printf("usage:  client SERVER_IP PORT\n");                
        return EXIT_ERROR;
    }
    
    int i_portNumber;
    int i_connectReturn, i_recvReturn, i_wsaReturn;
    char ac_incomingData[MSG_SIZE];
    SOCKET ui_socketDescriptor;
    sockaddr_in st_serverAddress;
    WSADATA st_wsaData;

    // Choose the latest (v 2.2) Winsock version, following
    // the sample code at http://msdn.microsoft.com/en-us/library/ms742213(v=vs.85).aspx.
    i_wsaReturn = WSAStartup(MAKEWORD(2, 2), &st_wsaData);
    if (i_wsaReturn < 0)
    {
        printf("Error invoking WSAStartup");
        return EXIT_ERROR;
    }
    // Check that we actually got v 2.2 of the protocol
    if ( (LOBYTE(st_wsaData.wVersion) != 2) || (HIBYTE(st_wsaData.wVersion) != 2) )
    {
        printf("System does not support requested Winsock version.");
        return EXIT_ERROR;
    }

    i_portNumber = atoi(argv[2]);
    printf("Parameters passed: address %s, port %s\n", argv[1], argv[2]);

    // Create a socket. Per <a href="http://msdn.microsoft.com/en-us/library/ms740506%28v=vs.85%29.aspx">socket docs</a>:<br />address family (af): AF_INET = IPv4<br />type: SOCK_STREAM = TCP/IP<br />protocol: IPPROTO_TCP = TCP/IP
    ui_socketDescriptor = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (ui_socketDescriptor == INVALID_SOCKET)
    {
        printf("Error creating the network socket");
        WSACleanup();
        return EXIT_ERROR;
    }

    // Connect to the server through this socket by setting up this <a href="http://msdn.microsoft.com/en-us/library/ms740496%28v=vs.85%29.aspx">struct</a>.<br />
    st_serverAddress.sin_family = AF_INET;
    // Use <a href="http://msdn.microsoft.com/en-us/library/ms738557%28v=VS.85%29.aspx">htons</a> to convert between byte orders.<br />
    st_serverAddress.sin_port = htons(i_portNumber);
    // Set the address to connect using using the <a href="http://msdn.microsoft.com/en-us/library/ms738571%28VS.85%29.aspx">struct</a> below.<br />Use <a href="http://msdn.microsoft.com/en-us/library/ms738563%28VS.85%29.aspx">inet_addr</a> to convert the address from text to a correct endian dword.<br />
    st_serverAddress.sin_addr.s_addr = inet_addr(argv[1]);
	if (st_serverAddress.sin_addr.s_addr == INADDR_NONE)
    {
        printf("Error interpreting IP address entered\n");
        closesocket(ui_socketDescriptor);
        WSACleanup();
        return EXIT_ERROR;
    }

    memset(&(st_serverAddress.sin_zero), 0, sizeof(st_serverAddress.sin_zero));
    printf("Connecting to address 0x%x, port 0x%x\n", st_serverAddress.sin_addr.s_addr, st_serverAddress.sin_port);
    i_connectReturn = connect(ui_socketDescriptor, \
                                (struct sockaddr*)&st_serverAddress, \
                                sizeof(st_serverAddress));
    if (i_connectReturn < 0)
    {
        printf("Error connecting to the server");
        WSASetLastError(WSAGetLastError());
        closesocket(ui_socketDescriptor);
        WSACleanup();
        return EXIT_ERROR;
    }

    printf("\nSending message: \"Hi\"\n");
    if (send(ui_socketDescriptor, "Hi", sizeof("Hi"), 0) < 0)
    {
        printf("Error sending message to server");
        closesocket(ui_socketDescriptor);
        WSACleanup();
        return EXIT_ERROR;
    }

    if (shutdown(ui_socketDescriptor, SD_SEND) < 0)
    {
        printf("Error upon halting sends");        
        closesocket(ui_socketDescriptor);
        WSACleanup();
        return EXIT_ERROR;
    }

    i_recvReturn = recv(ui_socketDescriptor, ac_incomingData, MSG_SIZE, 0);
    if (i_recvReturn < 0)
    {
        printf("ERROR receiving data from server");        
        closesocket(ui_socketDescriptor);
        WSACleanup();
        return EXIT_ERROR;
    }

    printf("\nReceived message: \"%s\"\n", ac_incomingData);

    closesocket(ui_socketDescriptor);
    WSACleanup();
    return EXIT_SUCCESS;
}
// 