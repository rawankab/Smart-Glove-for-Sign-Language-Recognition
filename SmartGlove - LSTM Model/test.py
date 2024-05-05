
# import pandas as pd
# import serial
# import serial.tools.list_ports
# from tensorflow.keras.models import load_model
# import numpy as np
# import time
# import pyttsx3

# # Initialize the text-to-speech engine
# engine = pyttsx3.init()

# # Define column names at the top of your script
# column_names = ['angle1', 'angle2', 'angle3', 'angle4', 'angle5', 'rolldeg', 'pitchdeg', 'anglegx', 'anglegy', 'anglegz']

# def select_com_port():
#     ports = serial.tools.list_ports.comports()
#     print("Available COM Ports:")
#     for port in ports:
#         print(port)
#     com_port = input("Select COM Port for Arduino (e.g., COM5): ")
#     for port in ports:
#         if com_port in port.device:
#             print(f"Selected port: {port.device}")
#             return port.device
#     print("Invalid selection or port not available.")
#     exit()

# def main():
#     serial_port = select_com_port()
#     ser = serial.Serial(serial_port, 9600)
#     model = load_model('model.h5')  # Make sure to provide the correct path to your model file
#     time.sleep(2)  # Initial delay to stabilize connection

#     label_map = {0: 'Hello', 1: 'See you later', 2: 'Please', 3: 'Yes', 4: 'No', 5: 'Same'}

#     while True:
#         print("Start performing the movement now!")
#         start_time = time.time()
#         data_buffer = []  # Buffer to hold incoming data

#         while time.time() - start_time < 3:  # Collect data for exactly 3 seconds
#             line = ser.readline().decode('utf-8').strip()
#             data_list = line.split(',')

#             if len(data_list) == len(column_names):
#                 data_point = list(map(float, data_list))
#                 data_buffer.append(data_point)
#                 print(data_point)

#         if len(data_buffer) >= 68:  # Check if enough data was collected
#             df = pd.DataFrame(data_buffer[:68], columns=column_names)
#             prediction = model.predict(df.values[None, :, :])
#             predicted_index = np.argmax(prediction)
#             predicted_label = label_map[predicted_index]  # Get the label from the map
#             print(f"Predicted label: {predicted_label}")
#             engine.say(predicted_label)  # Say the predicted label
#             engine.runAndWait()
#         else:
#             print("Not enough data collected, movement may need to be faster or more pronounced.")

#         print("Waiting 5 seconds before next movement...")
#         time.sleep(5)  # Wait for 5 seconds before prompting the next movement

# if __name__ == "__main__":
#     main()

import pandas as pd
import serial
import serial.tools.list_ports
from tensorflow.keras.models import load_model
import numpy as np
import time
import pyttsx3
from tensorflow.keras.layers import Layer
import tensorflow.keras.backend as K



# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Define column names at the top of your script
column_names = ['angle1', 'angle2', 'angle3', 'angle4', 'angle5', 'rolldeg', 'pitchdeg', 'anglegx', 'anglegy', 'anglegz']
class FeatureWeightingLayer(Layer):
    def __init__(self, scaling_factors, **kwargs):
        super(FeatureWeightingLayer, self).__init__(**kwargs)
        self.scaling_factors = K.variable(scaling_factors, name='scaling_factors')

    def call(self, inputs):
        return inputs * self.scaling_factors

    def get_config(self):
        config = super(FeatureWeightingLayer, self).get_config()
        config.update({'scaling_factors': self.scaling_factors.numpy()})
        return config

def select_com_port():
    ports = serial.tools.list_ports.comports()
    print("Available COM Ports:")
    for port in ports:
        print(f"{port.device} - {port.description}")
    com_port = input("Select COM Port for Arduino (e.g., COM5): ")
    for port in ports:
        if com_port in port.device:
            print(f"Selected port: {port.device}")
            return port.device
    print("Invalid selection or port not available.")
    return None

def main():
    serial_port = select_com_port()
    if serial_port is None:
        return  # Exit if no valid port is selected

    ser = serial.Serial(serial_port, 9600, timeout=1)
    custom_objects = {'FeatureWeightingLayer': FeatureWeightingLayer}
    model = load_model('model.h5', custom_objects=custom_objects)  # Now includes custom layer
    time.sleep(2)  # Initial delay to stabilize connection

    # Reverse mapping: index to label
    label_map = {0: 'Same', 1: 'How are you', 2: 'No', 3: 'Hello', 4: 'Yes'}

    while True:
        try:
            print("Start performing the movement now!")
            start_time = time.time()
            data_buffer = []  # Buffer to hold incoming data

            while time.time() - start_time < 3:  # Collect data for exactly 3 seconds
                line = ser.readline().decode('utf-8').strip()
                if line:
                    data_list = line.split(',')
                    if len(data_list) == len(column_names):
                        data_point = list(map(float, data_list))
                        data_buffer.append(data_point)
                        print(data_point)

            if len(data_buffer) >= 68:  # Check if enough data was collected
                df = pd.DataFrame(data_buffer[:68], columns=column_names)
                prediction = model.predict(np.expand_dims(df, axis=0))
                predicted_index = np.argmax(prediction)
                predicted_label = label_map.get(predicted_index, "Unknown")  # Get the label from the map
                print(f"Predicted label: {predicted_label}")
                engine.say(predicted_label)  # Say the predicted label
                engine.runAndWait()
            else:
                print("Not enough data collected, movement may need to be faster or more pronounced.")

            print("Waiting 5 seconds before next movement...")
            time.sleep(5)  # Wait for 5 seconds before prompting the next movement

        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Break the loop in case of error

if __name__ == "__main__":
    main()
