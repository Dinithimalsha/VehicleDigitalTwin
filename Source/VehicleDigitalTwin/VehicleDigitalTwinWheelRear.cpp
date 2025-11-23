// Copyright Epic Games, Inc. All Rights Reserved.

#include "VehicleDigitalTwinWheelRear.h"
#include "UObject/ConstructorHelpers.h"

UVehicleDigitalTwinWheelRear::UVehicleDigitalTwinWheelRear()
{
	AxleType = EAxleType::Rear;
	bAffectedByHandbrake = true;
	bAffectedByEngine = true;
}