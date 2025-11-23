# Vehicle Digital Twin

A real-time vehicle simulation and visualization system that combines a Python-based physics engine with an Unreal Engine 5.4 frontend. This project creates a digital twin of a Formula 1-style racing vehicle with advanced telemetry, tire physics, aerodynamics, and real-time data streaming.

## 🚗 Overview

Vehicle Digital Twin is a comprehensive simulation platform that demonstrates:
- **Real-time telemetry generation** using advanced physics models
- **WebSocket-based communication** between backend and frontend
- **3D visualization** in Unreal Engine with live data updates
- **Data persistence** for playback and analysis
- **Advanced vehicle physics** including tire thermodynamics, wear modeling, and aerodynamics

## ✨ Features

### Physics Engine
- **Advanced Tire Model**: Simulates tire thermodynamics, wear, and grip with multiple compound types (SOFT, MEDIUM, HARD)
- **Aerodynamics Model**: Drag and downforce calculations with DRS (Drag Reduction System) support
- **Realistic Vehicle Dynamics**: F1-style physics with gear shifting, engine temperature, and anomaly detection
- **State Machine**: Simulates realistic driving scenarios (acceleration, braking, cornering)

### Backend Services
- **WebSocket Server**: Real-time telemetry streaming at 60 FPS
- **Telemetry Logger**: SQLite-based data persistence for playback
- **Live/Playback Modes**: Switch between real-time simulation and recorded data playback
- **RESTful API**: Command interface for mode switching

### Unreal Engine Integration
- **WebSocket Client**: Native C++ WebSocket integration for real-time data reception
- **Digital Twin Vehicle**: Vehicle pawn controlled by telemetry data
- **HUD System**: Real-time telemetry display with smooth interpolation
- **Visual Feedback**: Tire temperature visualization and DRS state indicators

## 🏗️ Architecture

```
┌─────────────────────┐
│  Unreal Engine 5.4  │
│   (Frontend/UI)     │
│                     │
│  - WebSocket Client │
│  - Vehicle Pawn     │
│  - HUD Widget       │
└──────────┬──────────┘
           │ WebSocket (ws://localhost:8765)
           │
┌──────────▼──────────┐
│  Python Backend     │
│                     │
│  - Physics Engine   │
│  - Telemetry Gen    │
│  - WebSocket Server │
│  - Data Logger      │
└─────────────────────┘
           │
           ▼
    ┌─────────────┐
    │ SQLite DB   │
    │ (telemetry) │
    └─────────────┘
```

## 📋 Prerequisites

### For Backend
- **Python 3.8+**
- **pip** (Python package manager)

### For Frontend
- **Unreal Engine 5.4** (or compatible version)
- **Visual Studio 2022** (or compatible C++ compiler)
- **Windows 10/11** (for Windows development)

## 🚀 Installation

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. **Open the project in Unreal Engine:**
   - Launch Unreal Engine 5.4
   - Open `VehicleDigitalTwin.uproject`
   - Allow the engine to compile C++ modules (first launch may take time)

2. **Verify plugins:**
   - The project uses the following plugins (should auto-enable):
     - `ChaosVehiclesPlugin` - Vehicle physics
     - `RawInput` - Input handling
     - `ModelingToolsEditorMode` - Editor tools

3. **Build the project:**
   - Right-click `VehicleDigitalTwin.uproject` → Generate Visual Studio project files
   - Open `VehicleDigitalTwin.sln` in Visual Studio
   - Build the solution (Build → Build Solution)

## 🎮 Usage

### Starting the Backend Server

1. **Activate the virtual environment** (if not already active):
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   ```

2. **Start the WebSocket server:**
   ```bash
   python server.py
   ```

   You should see:
   ```
   INFO:TelemetryServer:Starting telemetry broadcast loop...
   INFO:TelemetryServer:WebSocket server started on ws://localhost:8765
   ```

### Running the Unreal Engine Frontend

1. **Launch Unreal Engine** and open the project
2. **Open the main level** (or create a new level with the Digital Twin Vehicle)
3. **Place the Digital Twin Vehicle** in the level:
   - In the Content Browser, navigate to `Content/DigitalTwin/`
   - Drag `BP_DigitalTwinVehicle` into the level
4. **Press Play** to start the simulation

The vehicle will automatically connect to the WebSocket server and begin receiving telemetry data.

### Switching Between Live and Playback Modes

The backend supports two modes:

- **Live Mode**: Generates real-time telemetry using the physics engine
- **Playback Mode**: Replays previously recorded telemetry data

To switch modes, send a WebSocket message:
```json
{"command": "start_playback"}  // Switch to playback
{"command": "start_live"}       // Switch to live
```

## 📁 Project Structure

```
VehicleDigitalTwin/
├── backend/                    # Python backend services
│   ├── server.py              # WebSocket server and main entry point
│   ├── physics_engine.py      # Tire and aerodynamics models
│   ├── telemetry_generator.py  # Vehicle simulation and telemetry generation
│   ├── telemetry_logger.py    # SQLite database logging
│   ├── requirements.txt       # Python dependencies
│   ├── test_client.py         # WebSocket client test script
│   ├── test_physics.py        # Physics engine unit tests
│   └── telemetry.db           # SQLite database (auto-generated)
│
├── Source/                     # C++ source code
│   └── VehicleDigitalTwin/
│       ├── Network/
│       │   ├── WebSocketClient.h/cpp    # WebSocket client implementation
│       ├── Vehicle/
│       │   ├── DigitalTwinVehicle.h/cpp # Main vehicle pawn
│       ├── UI/
│       │   ├── VehicleHUD.h/cpp        # HUD widget
│       └── ...
│
├── Content/                    # Unreal Engine assets
│   ├── DigitalTwin/
│   │   ├── BP_DigitalTwinVehicle.uasset
│   │   └── WBP_VehicleHUD.uasset
│   └── ...
│
└── VehicleDigitalTwin.uproject # Unreal Engine project file
```

## 🔧 Technical Details

### Telemetry Data Format

The backend sends JSON telemetry data at 60 FPS with the following structure:

```json
{
  "timestamp": 1234567890.123,
  "speed_kmh": 250.5,
  "rpm": 11500,
  "gear": 7,
  "throttle": 0.95,
  "brake": 0.0,
  "steering": 0.0,
  "engine_temp": 105.3,
  "is_anomaly": false,
  "tires": [
    {
      "compound": "SOFT",
      "temp": 95.2,
      "wear": 12.5,
      "grip": 1.15
    },
    // ... (FL, FR, RL, RR)
  ],
  "aero": {
    "drs": true,
    "drag": 6500,
    "downforce": 12000
  }
}
```

### Physics Models

#### Tire Model
- **Thermodynamics**: Simulates heating from friction and flexing, cooling from convection
- **Wear**: Accumulates based on load, slip ratio, and temperature
- **Grip**: Calculated from temperature curve and wear factor
- **Compounds**: SOFT (high grip, fast wear), MEDIUM (balanced), HARD (low grip, slow wear)

#### Aerodynamics Model
- **Drag**: Calculated using `F_drag = 0.5 * ρ * A * Cd * v²`
- **Downforce**: Calculated using `F_downforce = 0.5 * ρ * A * Cl * v²`
- **DRS**: Reduces drag by 30% when active (requires DRS zone and <1s gap)

### WebSocket Protocol

- **Server URL**: `ws://localhost:8765`
- **Message Format**: JSON
- **Update Rate**: 60 FPS (16.67ms intervals)
- **Commands**: 
  - `{"command": "start_playback"}` - Switch to playback mode
  - `{"command": "start_live"}` - Switch to live mode

## 🧪 Testing

### Backend Tests

Run the physics engine unit tests:
```bash
cd backend
python test_physics.py
```

Test the WebSocket connection:
```bash
python test_client.py
```

### Integration Testing

1. Start the backend server
2. Run the test client in a separate terminal
3. Verify telemetry data is received correctly

## 🎯 Future Enhancements

Potential improvements and features:

- [ ] Multi-vehicle support
- [ ] Real-time track mapping
- [ ] Advanced anomaly detection and alerting
- [ ] Machine learning integration for predictive maintenance
- [ ] Cloud deployment options
- [ ] RESTful API for historical data queries
- [ ] Web-based dashboard
- [ ] Mobile app for remote monitoring
- [ ] Integration with real vehicle sensors
- [ ] Advanced visualization (heat maps, trajectory analysis)

## 🤝 Contributing

This is a demonstration project. Contributions, suggestions, and improvements are welcome!

## 📝 License

[Specify your license here]

## 🙏 Acknowledgments

- Unreal Engine 5.4 for the visualization platform
- Python WebSocket libraries for real-time communication
- Formula 1 physics principles for realistic simulation

## 📞 Support

For issues, questions, or contributions, please [create an issue](link-to-issues) or contact the project maintainers.

---

**Note**: This project is designed for educational and demonstration purposes. The physics models are simplified representations of real-world systems.

