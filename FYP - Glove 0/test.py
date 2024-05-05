import pandas as pd
import numpy as np
import serial
import serial.tools.list_ports
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib

def select_com_port():
    ports = serial.tools.list_ports.comports()
    print("Available COM Ports:")
    for port in ports:
        print(port)
    com_port = input("Select COM Port for Arduino (e.g., COM5): ")
    for port in ports:
        if com_port in port.device:
            print(f"Selected port: {port.device}")
            return port.device
    print("Invalid selection or port not available.")
    exit()

def main():
    serial_port = select_com_port()
    ser = serial.Serial(serial_port, 9600)

    # Load the scaler and model
    scaler = joblib.load('scaler.pkl')
    model = joblib.load('model.pkl')

    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                # Process the incoming data
                data_array = np.array([float(val) for val in line.split(',') if val])
                # Ensure the array is reshaped correctly and wrapped into a DataFrame with correct column names
                data_df = pd.DataFrame(data_array.reshape(1, -1), columns=scaler.feature_names_in_)
                # Scale the data using the previously fitted scaler
                scaled_data = scaler.transform(data_df)
                # Predict using the SVM model
                prediction = model.predict(scaled_data)
                print("Predicted Label:", prediction)
            except ValueError as e:
                print("Invalid data received:", e)

if __name__ == "__main__":
    main()
