# # First, ensure you have installed pyserial with: pip install pyserial
# import serial
# import serial.tools.list_ports
# import time

# # Function to list available COM ports and allow the user to select one
# def select_com_port():
#     ports = serial.tools.list_ports.comports()
#     available_ports = []

#     print("Available COM Ports:")
#     for port in ports:
#         available_ports.append(str(port))
#         print(str(port))
    
#     com_port = input("Select COM Port for Arduino (e.g., COM5): ")
#     selected_port = None

#     for port in available_ports:
#         if port.startswith(com_port):
#             selected_port = com_port
#             print(f"Selected port: {selected_port}")
#             return selected_port
    
#     if not selected_port:
#         print("Invalid selection or port not available.")
#         exit()

# # Setup for data collection
# output_csv_file = 'sensor_data_with_labels.csv'
# header = [
#     'flex1', 'flex2', 'flex3', 'flex4', 'flex5',
#     'rolldeg', 'pitchdeg', 'headingDegrees',
#     'label'  # For the gesture label
# ]
# labels = {
#     1: 'Hello',
#     2: 'Me',
#     3: 'Father',
#     4: 'Mother',
#     5: 'Yes',
#     6: 'No',
#     # Add more labels as needed
# }
# samples_per_label = 200
# delay_between_samples = 0.01  # Seconds

# # Function to collect data for a specific label
# def collect_data(serial_port, label):
#     with serial.Serial(serial_port, 9600) as ser, open(output_csv_file, 'a') as file:
#         print(f"Collecting {samples_per_label} samples for {labels[label]}. Ready? Go!")
#         for _ in range(samples_per_label):
#             try:
#                 line = ser.readline().decode('utf-8').rstrip()
#                 data_with_label = f"{line},{labels[label]}"
#                 print(data_with_label)
#                 file.write(data_with_label + '\n')
#                 time.sleep(delay_between_samples)  # Delay to allow time for hand gesture
#             except KeyboardInterrupt:
#                 print(f"Stopped collecting data for {labels[label]}.")
#                 break

# def main():
#     serial_port = select_com_port()  # User selects the COM port

#     # Write the CSV header
#     with open(output_csv_file, 'w') as file:
#         file.write(','.join(header) + '\n')

#     # Main loop to choose which label to collect data for
#     while True:
#         print("Select a label to collect data for:")
#         for key, value in labels.items():
#             print(f"{key}: {value}")
#         print("0: Exit")

#         choice = input("Enter your choice: ")

#         if choice.isdigit():
#             choice = int(choice)
#             if choice == 0:
#                 break
#             elif choice in labels:
#                 collect_data(serial_port, choice)
#             else:
#                 print("Invalid choice. Please try again.")
#         else:
#             print("Please enter a number.")

# if __name__ == "__main__":
#     main()

import serial
import serial.tools.list_ports
import time

def select_com_port():
    ports = serial.tools.list_ports.comports()
    available_ports = []

    print("Available COM Ports:")
    for port in ports:
        available_ports.append(str(port))
        print(str(port))
    
    com_port = input("Select COM Port for Arduino (e.g., COM5): ")
    selected_port = None

    for port in available_ports:
        if port.startswith(com_port):
            selected_port = com_port
            print(f"Selected port: {selected_port}")
            return selected_port
    
    if not selected_port:
        print("Invalid selection or port not available.")
        exit()

# Set the filename for saving sensor data
output_csv_file = 'dynamic_sensor_data_with_labels.csv'

header = [
    'angle1', 'angle2', 'angle3', 'angle4', 'angle5',
    'rolldeg', 'pitchdeg', 'anglegx', 'anglegy', 'anglegz',
    'label'
]

labels = {
    1: 'Hello',
    2: 'Same',
    3: 'Yes',
    4: 'No',
    5: 'See you later',
    6: 'Please',
    7: 'Thank you',
    8: 'How are you',
    # Add more labels as needed
}

gesture_duration = 2  # seconds, adjust as necessary for the length of the gesture

def collect_gesture_data(serial_port, label):
    with serial.Serial(serial_port, 9600, timeout=1) as ser, open(output_csv_file, 'a') as file:
        for _ in range(80):  # Loop to collect 100 samples for each movement
            print(f"Get ready to perform {labels[label]} gesture in 3 seconds...")
            time.sleep(3)  # Give time to get ready
            print(f"Performing {labels[label]} now.")

            # Mark the start of the gesture
            start_marker = "Start," + f"{labels[label]}"
            file.write(start_marker + '\n')

            start_time = time.time()
            while (time.time() - start_time) < gesture_duration:
                line = ser.readline().decode('utf-8').rstrip()
                if line:
                    data_with_label = f"{line},{labels[label]}"
                    print(data_with_label)  # Optional: Print data to console for verification
                    file.write(data_with_label + '\n')

            # Mark the end of the gesture
            end_marker = "End," + f"{labels[label]}"
            file.write(end_marker + '\n')

            print(f"Finished collecting data for {labels[label]} gesture.")

def main():
    serial_port = select_com_port()

    # Write the CSV header if file does not exist
    try:
        with open(output_csv_file, 'x') as file:
            file.write(','.join(header) + '\n')
    except FileExistsError:
        print("Header already exists. Continuing to append data...")

    while True:
        print("Select a label to collect data for:")
        for key, value in labels.items():
            print(f"{key}: {value}")
        print("0: Exit")

        choice = input("Enter your choice: ")

        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                break
            elif choice in labels:
                collect_gesture_data(serial_port, choice)
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Please enter a number.")


if __name__ == "__main__":
    main()
