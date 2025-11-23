#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "VehicleHUD.generated.h"

/**
 * HUD widget to display vehicle telemetry.
 * Uses meta=(BindWidget) to link directly to UMG widgets without Blueprint graph logic.
 */
UCLASS()
class VEHICLEDIGITALTWIN_API UVehicleHUD : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Telemetry")
	void UpdateTelemetryData(float Speed, float RPM, int32 Gear, float Throttle, float Brake, float Temp, bool IsAnomaly);

protected:
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	// Target values for interpolation
	float TargetSpeed;
	float TargetRPM;
	int32 TargetGear; // Added for consistency
	float TargetThrottle;
	float TargetBrake;
	float TargetTemp;

	// Current displayed values
	float DisplayedSpeed;
	float DisplayedRPM;
	int32 DisplayedGear; // Added for consistency
	float DisplayedThrottle;
	float DisplayedBrake;
	float DisplayedTemp;

	// These names MUST match the widget names in the UMG Designer
	UPROPERTY(meta = (BindWidget))
	UTextBlock* SpeedText;

	UPROPERTY(meta = (BindWidget))
	UTextBlock* RPMText;

	UPROPERTY(meta = (BindWidget))
	UTextBlock* GearText;

	UPROPERTY(meta = (BindWidget))
	UProgressBar* ThrottleBar;

	UPROPERTY(meta = (BindWidget))
	UProgressBar* BrakeBar;

	UPROPERTY(meta = (BindWidget))
	UTextBlock* TempText;

	UPROPERTY(meta = (BindWidget))
	UTextBlock* AnomalyWarningText;
};
