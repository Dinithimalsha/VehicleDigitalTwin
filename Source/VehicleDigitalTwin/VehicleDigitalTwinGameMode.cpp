// Copyright Epic Games, Inc. All Rights Reserved.

#include "VehicleDigitalTwinGameMode.h"
#include "VehicleDigitalTwinPlayerController.h"

AVehicleDigitalTwinGameMode::AVehicleDigitalTwinGameMode()
{
	PlayerControllerClass = AVehicleDigitalTwinPlayerController::StaticClass();
}
