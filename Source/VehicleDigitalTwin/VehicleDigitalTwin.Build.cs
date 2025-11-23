// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class VehicleDigitalTwin : ModuleRules
{
	public VehicleDigitalTwin(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "ChaosVehicles", "PhysicsCore", "WebSockets", "Json", "JsonUtilities", "UMG" });
	}
}
