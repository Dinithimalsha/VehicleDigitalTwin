#pragma once

#include "CoreMinimal.h"
#include "../VehicleDigitalTwinPawn.h"
#include "DigitalTwinVehicle.generated.h"

class UWebSocketClient;

/**
 * Vehicle pawn that is controlled by digital twin telemetry.
 */
UCLASS()
class VEHICLEDIGITALTWIN_API ADigitalTwinVehicle : public AVehicleDigitalTwinPawn
{
	GENERATED_BODY()

public:
	ADigitalTwinVehicle();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
	virtual void Tick(float DeltaTime) override;

	UFUNCTION()
	void OnTelemetryReceived(const FString& JsonData);

	UFUNCTION()
	void OnConnected();

	UFUNCTION()
	void OnConnectionError();

	UFUNCTION(BlueprintCallable, Category = "DigitalTwin")
	void SetPlaybackMode(bool bEnablePlayback);

private:
	UPROPERTY()
	UWebSocketClient* WebSocketClient;

	// Telemetry data
	float CurrentSpeed;
	float CurrentRPM;
	int32 CurrentGear;
	float CurrentThrottle;
	float CurrentBrake;
	float CurrentSteering;
	float CurrentEngineTemp;
	
protected:
	// Tire Data (FL, FR, RL, RR)
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DigitalTwin")
	TArray<float> TireTemperatures;

	// Event to update visuals in BP (e.g. Material Parameters)
	UFUNCTION(BlueprintImplementableEvent, Category = "DigitalTwin")
	void UpdateTireVisuals(const TArray<float>& Temperatures);

	// Aero Data
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DigitalTwin")
	bool bDRSActive;

	// Event to update Aero visuals (e.g. Rear Wing Rotation)
	UFUNCTION(BlueprintImplementableEvent, Category = "DigitalTwin")
	void UpdateAeroVisuals(bool bIsDRSOpen);

private:

	UPROPERTY(EditAnywhere, Category = "UI")
	TSubclassOf<class UVehicleHUD> HUDWidgetClass;

	UPROPERTY()
	class UVehicleHUD* HUDWidget;
};
