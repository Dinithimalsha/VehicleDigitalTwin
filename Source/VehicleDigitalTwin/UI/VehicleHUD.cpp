#include "VehicleHUD.h"

void UVehicleHUD::UpdateTelemetryData(float Speed, float RPM, int32 Gear, float Throttle, float Brake, float Temp, bool IsAnomaly)
{
	// Just update targets here. The visual update happens in NativeTick for smoothness.
	TargetSpeed = Speed;
	TargetRPM = RPM;
	TargetGear = Gear;
	TargetThrottle = Throttle;
	TargetBrake = Brake;
	TargetTemp = Temp;

	// Instant update for critical warnings
	if (AnomalyWarningText)
	{
		if (IsAnomaly)
		{
			AnomalyWarningText->SetVisibility(ESlateVisibility::Visible);
			AnomalyWarningText->SetText(FText::FromString(TEXT("WARNING: ENGINE OVERHEAT")));
			AnomalyWarningText->SetColorAndOpacity(FLinearColor::Red);
		}
		else
		{
			AnomalyWarningText->SetVisibility(ESlateVisibility::Hidden);
		}
	}
}

void UVehicleHUD::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	// Smooth interpolation (InterpSpeed = 10.0f gives a snappy but smooth feel)
	DisplayedSpeed = FMath::FInterpTo(DisplayedSpeed, TargetSpeed, InDeltaTime, 10.0f);
	DisplayedRPM = FMath::FInterpTo(DisplayedRPM, TargetRPM, InDeltaTime, 10.0f);
	DisplayedThrottle = FMath::FInterpTo(DisplayedThrottle, TargetThrottle, InDeltaTime, 15.0f);
	DisplayedBrake = FMath::FInterpTo(DisplayedBrake, TargetBrake, InDeltaTime, 15.0f);
	DisplayedTemp = FMath::FInterpTo(DisplayedTemp, TargetTemp, InDeltaTime, 2.0f); // Temp changes slowly

	// Update Widgets
	if (SpeedText)
	{
		SpeedText->SetText(FText::FromString(FString::Printf(TEXT("%.0f"), DisplayedSpeed)));
	}

	if (RPMText)
	{
		RPMText->SetText(FText::FromString(FString::Printf(TEXT("%.0f"), DisplayedRPM)));
		
		// Dynamic Color: White -> Yellow -> Red based on RPM
		FLinearColor RPMColor = FLinearColor::White;
		if (DisplayedRPM > 6000.0f) RPMColor = FLinearColor::Yellow;
		if (DisplayedRPM > 7500.0f) RPMColor = FLinearColor::Red;
		RPMText->SetColorAndOpacity(RPMColor);
	}

	// Gear Update with Diagnostics
	if (GearText)
	{
		// Only update if changed to avoid text rebuilding every frame
		if (DisplayedGear != TargetGear)
		{
			DisplayedGear = TargetGear;
			GearText->SetText(FText::FromString(FString::Printf(TEXT("%d"), DisplayedGear)));
		}
	}
	else
	{
		// Diagnostic Log (Throttled)
		static double LastLogTime = 0.0;
		double CurrentTime = FPlatformTime::Seconds();
		if (CurrentTime - LastLogTime > 5.0) // Log every 5 seconds
		{
			UE_LOG(LogTemp, Error, TEXT("HUD ERROR: 'GearText' widget is NULL! Please rename your Text Block in UMG to 'GearText' (Case Sensitive)."));
			LastLogTime = CurrentTime;
		}
	}

	if (ThrottleBar)
	{
		ThrottleBar->SetPercent(DisplayedThrottle);
		// Dynamic Color: Green intensity
		ThrottleBar->SetFillColorAndOpacity(FLinearColor(0.0f, 1.0f, 0.0f, 0.5f + (DisplayedThrottle * 0.5f)));
	}

	if (BrakeBar)
	{
		BrakeBar->SetPercent(DisplayedBrake);
		// Dynamic Color: Red intensity
		BrakeBar->SetFillColorAndOpacity(FLinearColor(1.0f, 0.0f, 0.0f, 0.5f + (DisplayedBrake * 0.5f)));
	}

	if (TempText)
	{
		TempText->SetText(FText::FromString(FString::Printf(TEXT("%.1f °C"), DisplayedTemp)));
		// Dynamic Color: Blue -> Green -> Red
		FLinearColor TempColor = FLinearColor::Green;
		if (DisplayedTemp < 50.0f) TempColor = FLinearColor::Blue;
		if (DisplayedTemp > 100.0f) TempColor = FLinearColor::Red;
		TempText->SetColorAndOpacity(TempColor);
	}
}
