// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "VehicleDigitalTwinPawn.h"
#include "VehicleDigitalTwinSportsCar.generated.h"

/**
 *  Sports car wheeled vehicle implementation
 */
UCLASS(abstract)
class VEHICLEDIGITALTWIN_API AVehicleDigitalTwinSportsCar : public AVehicleDigitalTwinPawn
{
	GENERATED_BODY()
	
public:

	AVehicleDigitalTwinSportsCar();
};
