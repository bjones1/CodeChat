// camerasock.cpp : Defines the entry point for the console application.
//*******************************************************
// Process:     UDP/TCP Client
// Author:      Jacob Bowen
// Description: This process sends either a TCP or UDP 
//              message to a server based on the 
//              command-line arguments that it is given.
//              It then waits for a response.
//*******************************************************/

#include "stdafx.h"
#include <winsock2.h>
#include <conio.h>
#include <iostream>
#include <string>

using namespace std;

#define EXIT_SUCCESS 0
#define EXIT_ERROR   1
#define TCP_PROTOCOL 6
#define UDP_PROTOCOL 17
#define TCP          1
#define UDP          2
#define MSG_SIZE     7

int _tmain(int argc, char* argv[])
{
	if(argc < 3)
    {
        printf("usage:  client SERVER_IP PROTOCOL\
                \n\twhere the PROTOCOL is 1 for TCP and 2 for UDP\n");
                
        return EXIT_ERROR;
    }
    
    int i_protocol, i_portNumber, i_sinSize;
    int i_connectReturn, i_recvReturn, i_wsaReturn;
    char ac_incomingData[MSG_SIZE];
	SOCKET ui_socketDescriptor;
    sockaddr_in st_serverAddress;
	WSADATA st_wsaData;

	i_wsaReturn = WSAStartup(0x101, &st_wsaData);
	if(i_wsaReturn < 0)
	{
		printf("Error invoking WSAStartup");

		return EXIT_ERROR;
	}

    cout << "Enter port number: ";
	cin >> i_portNumber;
	cout << endl;

    i_protocol = atoi(argv[2]);

    if(i_protocol == TCP)
    {
        ui_socketDescriptor = socket(AF_INET, SOCK_STREAM, TCP_PROTOCOL);
        if(ui_socketDescriptor < 0)
        {
            printf("Error creating the network socket");
        
            return EXIT_ERROR;
        }
    
        st_serverAddress.sin_family = AF_INET;
        st_serverAddress.sin_port = htons(i_portNumber);
        st_serverAddress.sin_addr.s_addr = inet_addr(argv[1]);
        memset(&(st_serverAddress.sin_zero), '\0', 8);
    
        i_connectReturn = connect(ui_socketDescriptor, \
                                    (struct sockaddr*)&st_serverAddress, \
                                    sizeof(st_serverAddress));
        if(i_connectReturn < 0)
        {
            printf("Error connecting to the server @ %S:%d", argv[1], i_portNumber);

			closesocket(ui_socketDescriptor);
            return EXIT_ERROR;
        }
    
        printf("\nSending message: \"Hi\"\n");
        if(send(ui_socketDescriptor, "Hi", sizeof("Hi"), 0) < 0)
        {
            printf("Error sending message to server");
        
			closesocket(ui_socketDescriptor);
            return EXIT_ERROR;
        }
    
        if(shutdown(ui_socketDescriptor, SD_SEND) < 0)
        {
            printf("Error upon halting sends");
        
			closesocket(ui_socketDescriptor);
            return EXIT_ERROR;
        }
    
        i_recvReturn = recv(ui_socketDescriptor, ac_incomingData, MSG_SIZE, 0);
        if(i_recvReturn < 0)
        {
            printf("ERROR receiving data from server");
        
			closesocket(ui_socketDescriptor);
            return EXIT_ERROR;
        }
    
        printf("\nReceived message: \"%s\"\n", ac_incomingData);
    
        closesocket(ui_socketDescriptor);
        return EXIT_SUCCESS;
		WSACleanup();

    }
    else
    {
        if(i_protocol == UDP)
        {
            ui_socketDescriptor = socket(AF_INET, SOCK_DGRAM, UDP_PROTOCOL);
            if(ui_socketDescriptor < 0)
            {
                printf("Error creating the network socket");
        
                return EXIT_ERROR;
            }
    
            st_serverAddress.sin_family = AF_INET;
            st_serverAddress.sin_port = htons(i_portNumber);
            st_serverAddress.sin_addr.s_addr = inet_addr(argv[1]);
            memset(&(st_serverAddress.sin_zero), '\0', 8);
    
            printf("\nSending message: \"Hi\"\n");
            if(sendto(ui_socketDescriptor, "Hi", sizeof("Hi"), 0, \
                              (struct sockaddr*)&st_serverAddress, \
                              sizeof(st_serverAddress)) < 0)
            {
                printf("Error sending message to server");
        
                return EXIT_ERROR;
            }
    
            i_recvReturn = recvfrom(ui_socketDescriptor, ac_incomingData, \
                                    MSG_SIZE, 0, \
                                    (struct sockaddr*)&st_serverAddress, \
                                    &i_sinSize);
            if(i_recvReturn < 0)
            {
                printf("ERROR receiving data from server");
        
                return EXIT_ERROR;
            }
    
            printf("\nReceived message: \"%s\"\n", ac_incomingData);
    
            closesocket(ui_socketDescriptor);
            return EXIT_SUCCESS;
            WSACleanup();
        }
        else
        {
            printf("Invalid protocol number!\n\
                    usage:  client SERVER_IP SERVER_PORT PROTOCOL\
                    \n\twhere the PROTOCOL is 1 for TCP and 2 for UDP\n");
                    
            return EXIT_ERROR;
        }
    }
}

