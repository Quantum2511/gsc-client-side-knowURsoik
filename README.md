# KnowURSoil - Client Side Application

## Overview

KnowURSoil is a client-side application for a plant monitoring system. It is designed to run on a Raspberry Pi 4 and interfaces with various sensors to monitor soil conditions. The application provides features for user authentication and records environmental data to a PostgreSQL database.

## Features

- **User Authentication**: Secure sign-in to access the application.
- **Soil Data Recording**: Captures soil condition data and sends it to a database.
- **Environmental Monitoring**: Records temperature and humidity data.

## Hardware Requirements

- Raspberry Pi 4
- Color sensor with S0, S1, S2, S3, OUT pins
- DHT11 temperature and humidity sensor
- Necessary connecting wires

## Software Requirements

- Python 3.11
- Tkinter for GUI
- PostgreSQL
- Adafruit_DHT library
- RPi.GPIO library

## Installation

1. Clone the repository: git clone https://github.com/Quantum2511/gsc-client-side-knowURsoil.git
2. Install required packages:
pip install -r requirements.txt


## Sensor Connections

Connect the sensors to the Raspberry Pi GPIO pins as follows:

- **Color Sensor**:
- S0 -> GPIO 20
- S1 -> GPIO 21
- S2 -> GPIO 22
- S3 -> GPIO 23
- OUT -> GPIO 24
- **DHT11 Sensor**: Connect the data pin to GPIO 4 (D4)

## Configuration

1. Set up the PostgreSQL database and obtain the connection string.
2. Store the database connection string in a `.env` file with the key `DATABASE_URL`.

## Usage

Run the application using Python:


Follow the on-screen instructions to sign in and use the application.


## File Structure

- `gsc-client-side-soilReader.py`: Main Python script for reading soil sensor data.
- `.env`: Environment variables for database configuration.
- `requirements.txt`: Lists all Python dependencies.

## Contributing

Contributions to this project are welcome. Please follow the standard GitHub workflow:

1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Submit a pull request.

## License

[Specify the license, if applicable]

## Acknowledgments

- Google Solution Challenge
- Project contributors and maintainers

## License

[Specify the license, if applicable]

## Acknowledgments

- Raspberry Pi Foundation
- Project contributors and maintainers
