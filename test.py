import customtkinter as ctk

# Function to be called when the submit button is clicked
def submit_action():
    spreadsheet_name = spreadsheet_name_entry.get()
    print("Spreadsheet Name:", spreadsheet_name)

# Create the main window
root = ctk.CTk()
root.title("Custom Tkinter GUI")

# Create a frame
frame = ctk.CTkFrame(master=root)
frame.pack()

# Create the CTkEntry widget with a default value
spreadsheet_name_entry = ctk.CTkEntry(master=frame, placeholder_text="Spreadsheet Name")
spreadsheet_name_entry.insert(0, "Default Value")  # Insert the default value
spreadsheet_name_entry.pack()

# Create the submit button
submit_button = ctk.CTkButton(master=frame, text="Submit", command=submit_action)
submit_button.pack()

# Add your GUI widgets and functionality here...

# Start the customtkinter event loop
root.mainloop()




LEADS_FILE_NAME = os.environ['LEADS_FILE_NAME']
STREET_COL = int(os.environ["STREET_COL"]) - 1
ZIP_COL = int(os.environ["ZIP_COL"]) - 1
STATE_COL = ZIP_COL - 1
CITY_COL = STATE_COL -1