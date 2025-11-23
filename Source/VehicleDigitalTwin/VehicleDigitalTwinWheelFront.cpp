// Copyright Epic Games, Inc. All Rights Reserved.

#include "VehicleDigitalTwinWheelFront.h"
#include "UObject/ConstructorHelpers.h"

UVehicleDigitalTwinWheelFront::UVehicleDigitalTwinWheelFront()
{
	AxleType = EAxleType::Front;
	bAffectedBySteering = true;
	MaxSteerAngle = 40.f;
}