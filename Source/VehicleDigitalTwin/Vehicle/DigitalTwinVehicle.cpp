#include "DigitalTwinVehicle.h"
#include "../Network/WebSocketClient.h"
#include "../UI/VehicleHUD.h"
#include "Json.h"
#include "JsonUtilities.h"
#include "ChaosWheeledVehicleMovementComponent.h"

ADigitalTwinVehicle::ADigitalTwinVehicle()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ADigitalTwinVehicle::BeginPlay()
{
	Super::BeginPlay();

	WebSocketClient = NewObject<UWebSocketClient>(this);
	WebSocketClient->OnConnected.AddDynamic(this, &ADigitalTwinVehicle::OnConnected);
	WebSocketClient->OnConnectionError.AddDynamic(this, &ADigitalTwinVehicle::OnConnectionError);
	WebSocketClient->OnTelemetryReceived.AddDynamic(this, &ADigitalTwinVehicle::OnTelemetryReceived);

	// Connect to localhost by default
	WebSocketClient->Connect("ws://localhost:8765");

	// --- DIGITAL TWIN SETUP ---
	
	// 1. HUD Setup
	if (HUDWidgetClass)
	{
		HUDWidget = CreateWidget<UVehicleHUD>(GetWorld(), HUDWidgetClass);
		if (HUDWidget)
		{
			HUDWidget->AddToViewport();
			UE_LOG(LogTemp, Log, TEXT("HUD Widget created and added to viewport."));
		}
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("HUDWidgetClass is not set in the Blueprint! Please assign WBP_VehicleHUD."));
	}
}

void ADigitalTwinVehicle::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (WebSocketClient)
	{
		WebSocketClient->Close();
	}
	Super::EndPlay(EndPlayReason);
}

void ADigitalTwinVehicle::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Here we could interpolate values or apply them to the vehicle movement component
	// For visualization, we might just want to override the display values
	// But to make wheels spin, we might need to fake the input or directly set wheel rotation if possible
	
	// Example: Apply throttle to vehicle movement to make it move (if we want physics simulation based on telemetry)
	// Or just set the visual state.
	
	// For now, let's just log the data to screen for verification
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(1, 0.0f, FColor::Green, FString::Printf(TEXT("Speed: %.1f km/h | RPM: %.0f | Gear: %d"), CurrentSpeed, CurrentRPM, CurrentGear));
		GEngine->AddOnScreenDebugMessage(2, 0.0f, FColor::Yellow, FString::Printf(TEXT("Throttle: %.2f | Brake: %.2f | Temp: %.1f"), CurrentThrottle, CurrentBrake, CurrentEngineTemp));
		
		if (!GetVehicleMovementComponent())
		{
			GEngine->AddOnScreenDebugMessage(3, 0.0f, FColor::Red, TEXT("ERROR: VehicleMovementComponent is MISSING!"));
		}
	}
}

void ADigitalTwinVehicle::OnConnected()
{
	UE_LOG(LogTemp, Log, TEXT("Connected to Telemetry Server"));
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 10.0f, FColor::Green, TEXT("SUCCESS: Connected to Python Telemetry Server!"));
	}
}

void ADigitalTwinVehicle::OnConnectionError()
{
	UE_LOG(LogTemp, Error, TEXT("Failed to connect to Telemetry Server"));
}

void ADigitalTwinVehicle::OnTelemetryReceived(const FString& JsonData)
{
	// DEBUG: Print raw JSON to screen to verify data arrival
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(10, 0.0f, FColor::Cyan, FString::Printf(TEXT("RX: %s"), *JsonData));
	}

	TSharedPtr<FJsonObject> JsonObject;
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonData);

	if (FJsonSerializer::Deserialize(Reader, JsonObject))
	{
		CurrentSpeed = JsonObject->GetNumberField(TEXT("speed_kmh"));
		CurrentRPM = JsonObject->GetNumberField(TEXT("rpm"));
		CurrentGear = JsonObject->GetIntegerField(TEXT("gear"));
		CurrentThrottle = JsonObject->GetNumberField(TEXT("throttle"));
		CurrentBrake = JsonObject->GetNumberField(TEXT("brake"));
		CurrentSteering = JsonObject->GetNumberField(TEXT("steering"));
		CurrentEngineTemp = JsonObject->GetNumberField(TEXT("engine_temp"));
		bool bIsAnomaly = JsonObject->GetBoolField(TEXT("is_anomaly"));

		// Parse Tire Data (Nested Array)
		const TArray<TSharedPtr<FJsonValue>>* TiresArray;
		if (JsonObject->TryGetArrayField(TEXT("tires"), TiresArray))
		{
			TireTemperatures.Empty();
			for (const TSharedPtr<FJsonValue>& TireVal : *TiresArray)
			{
				const TSharedPtr<FJsonObject> TireObj = TireVal->AsObject();
				if (TireObj.IsValid())
				{
					float Temp = TireObj->GetNumberField(TEXT("temp"));
					TireTemperatures.Add(Temp);
				}
			}
			
			// Trigger Visual Update
			UpdateTireVisuals(TireTemperatures);
		}

		// Parse Aero Data
		const TSharedPtr<FJsonObject>* AeroObj;
		if (JsonObject->TryGetObjectField(TEXT("aero"), AeroObj))
		{
			bDRSActive = (*AeroObj)->GetBoolField(TEXT("drs"));
			UpdateAeroVisuals(bDRSActive);
		}

		if (HUDWidget)
		{
			HUDWidget->UpdateTelemetryData(CurrentSpeed, CurrentRPM, CurrentGear, CurrentThrottle, CurrentBrake, CurrentEngineTemp, bIsAnomaly);
		}

		// --- DIGITAL TWIN PHYSICS CONTROL ---
		// We use a control loop to make the vehicle match the telemetry speed.
		// This preserves physics (suspension, wheel rotation) while tracking the data.
		
		// --- DIGITAL TWIN PHYSICS CONTROL (FORCE BASED) ---
		// We apply a physical force to push the car to the target speed.
		// This bypasses the Engine/Transmission simulation (which can stall or be in wrong gear),
		// but still respects gravity and collisions for smooth movement.

		if (GetVehicleMovementComponent())
		{
			// Ensure brakes are off unless we want to stop
			GetVehicleMovementComponent()->SetHandbrakeInput(false);
			GetVehicleMovementComponent()->SetBrakeInput(0.0f);
			
			// Force Internal Gear (Fix for HUD showing 'N' if bound to component)
			GetVehicleMovementComponent()->SetTargetGear(CurrentGear, true);
			
			// Visuals: Set Steering just for the animation of wheels
			GetVehicleMovementComponent()->SetSteeringInput(CurrentSteering);
			
			// --- KINEMATIC CONTROL (The "Digital Twin" Way) ---
			// We force the vehicle to move at the exact speed from the telemetry.
			// This ignores engine power, friction, and gear ratios in Unreal,
			// ensuring the visual matches the data 1:1.
			
			if (UPrimitiveComponent* VehicleMesh = GetMesh())
			{
				// Convert km/h to cm/s (Unreal Units)
				float TargetSpeedCmS = CurrentSpeed * 100000.0f / 3600.0f; 
				
				// Get current forward direction
				FVector ForwardDir = GetActorForwardVector();
				
				// Calculate Target Velocity Vector
				// We preserve the current Z velocity (gravity/falling) to keep it grounded
				FVector CurrentVelocity = VehicleMesh->GetPhysicsLinearVelocity();
				FVector TargetVelocity = ForwardDir * TargetSpeedCmS;
				TargetVelocity.Z = CurrentVelocity.Z; 
				
				// Apply Velocity Directly
				VehicleMesh->SetPhysicsLinearVelocity(TargetVelocity);

				// Debug
				if (GEngine)
				{
					GEngine->AddOnScreenDebugMessage(5, 0.0f, FColor::Magenta, 
						FString::Printf(TEXT("KINEMATIC: Target Speed: %.1f km/h"), CurrentSpeed));
				}
			}
		}
		else
		{
			UE_LOG(LogTemp, Error, TEXT("VehicleMovementComponent is NULL!"));
		}
	}
}

void ADigitalTwinVehicle::SetPlaybackMode(bool bEnablePlayback)
{
	if (WebSocketClient)
	{
		FString Command = bEnablePlayback ? TEXT("{\"command\": \"start_playback\"}") : TEXT("{\"command\": \"start_live\"}");
		WebSocketClient->Send(Command);
	}
}
