#include "WebSocketClient.h"
#include "WebSocketsModule.h"
#include "IWebSocket.h"

UWebSocketClient::UWebSocketClient()
{
}

UWebSocketClient::~UWebSocketClient()
{
	if (WebSocket.IsValid() && WebSocket->IsConnected())
	{
		WebSocket->Close();
	}
}

void UWebSocketClient::Connect(const FString& ServerUrl)
{
	if (!FModuleManager::Get().IsModuleLoaded("WebSockets"))
	{
		FModuleManager::Get().LoadModule("WebSockets");
	}

	WebSocket = FWebSocketsModule::Get().CreateWebSocket(ServerUrl);

	// Use WeakPtr to prevent crash if this object is destroyed before callback fires
	TWeakObjectPtr<UWebSocketClient> WeakThis(this);

	WebSocket->OnConnected().AddLambda([WeakThis]()
	{
		if (UWebSocketClient* StrongThis = WeakThis.Get())
		{
			if (StrongThis->OnConnected.IsBound())
			{
				StrongThis->OnConnected.Broadcast();
			}
		}
	});

	WebSocket->OnConnectionError().AddLambda([WeakThis](const FString& Error)
	{
		if (UWebSocketClient* StrongThis = WeakThis.Get())
		{
			if (StrongThis->OnConnectionError.IsBound())
			{
				StrongThis->OnConnectionError.Broadcast();
			}
		}
	});

	WebSocket->OnMessage().AddLambda([WeakThis](const FString& Message)
	{
		if (UWebSocketClient* StrongThis = WeakThis.Get())
		{
			if (StrongThis->OnTelemetryReceived.IsBound())
			{
				StrongThis->OnTelemetryReceived.Broadcast(Message);
			}
		}
	});

	WebSocket->Connect();
}

void UWebSocketClient::Send(const FString& Message)
{
	if (WebSocket.IsValid() && WebSocket->IsConnected())
	{
		WebSocket->Send(Message);
	}
}

void UWebSocketClient::Close()
{
	if (WebSocket.IsValid() && WebSocket->IsConnected())
	{
		WebSocket->Close();
	}
}
