# Telepresence and Interactive Game Project for People with Multiple Sclerosis

## 1. Project Objective

This project aims to develop a telepresence system and an interactive game controlled through gestures, designed for people with multiple sclerosis — a condition that can cause motor difficulties, reduced coordination, and limited mobility.

The telepresence system allows these individuals to “be present” remotely within the facility, moving a robot and observing the environment via video without needing to move physically.

## 2. Main Technologies and Components

### 2.1 Programming Language

The system is developed in **Python**, a widely used programming language for robotics and computer vision due to its simplicity and availability of useful libraries.

### 2.2 AlphaBot Robot

The AlphaBot robot is a mobile platform compatible with:

- Raspberry Pi  
- Arduino  

It can be programmed and controlled via Raspberry Pi, Arduino, or both in integrated mode.

### 2.3 AlphaBot Features

AlphaBot offers:

- Interfaces for Raspberry Pi and Arduino  
- Motors for movement  
- Ports for additional sensors (e.g., obstacle or line tracking sensors)  
- Remote control via Wi-Fi, Bluetooth, or Infrared  

### 2.4 Integrated Hardware Modules

- GPIO interfaces for Raspberry Pi/Arduino  
- Motor driver based on L298P chip  
- Battery and voltage regulator  
- Sensor modules (infrared, ultrasonic, line tracking)  

## 3. Control System and Game Description

### 3.1 Gesture-Based Telepresence

User interaction with the robot occurs through:

- A camera connected to the system  
- Hand gesture recognition using software libraries  

The robot moves and interacts according to the detected gestures, making the experience accessible even to those unable to use traditional devices like keyboards or joysticks.

### 3.2 Interactive Game

The proposed game involves collecting balls displayed on the screen:

- Right hand highlighted in red  
- Left hand highlighted in blue  
- The player must close the hand over the corresponding colored ball  

The system uses **pygame** and hand tracking techniques to provide natural and intuitive interaction.

## 4. Development Environment and Required Libraries

### 4.1 Python Installation

1. Download Python from [python.org](https://www.python.org)  
2. During installation, check “Add Python to PATH”  
3. Verify installation in the Command Prompt with:
```bash
python --version
