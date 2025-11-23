#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "IWebSocket.h"
#include "WebSocketClient.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTelemetryReceived, const FString&, JsonData);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnConnected);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnConnectionError);

/**
 * Handles WebSocket connection to the Python telemetry server.
 */
UCLASS(Blueprintable)
class VEHICLEDIGITALTWIN_API UWebSocketClient : public UObject
{
	GENERATED_BODY()

public:
	UWebSocketClient();
	virtual ~UWebSocketClient();

	UFUNCTION(BlueprintCallable, Category = "Networking")
	void Connect(const FString& ServerUrl);

	UFUNCTION(BlueprintCallable, Category = "Networking")
	void Send(const FString& Message);

	UFUNCTION(BlueprintCallable, Category = "Networking")
	void Close();

	UPROPERTY(BlueprintAssignable, Category = "Networking")
	FOnTelemetryReceived OnTelemetryReceived;

	UPROPERTY(BlueprintAssignable, Category = "Networking")
	FOnConnected OnConnected;

	UPROPERTY(BlueprintAssignable, Category = "Networking")
	FOnConnectionError OnConnectionError;

private:
	TSharedPtr<IWebSocket> WebSocket;
};
