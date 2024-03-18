import customtkinter as ctk


ctk.set_appearance_mode("pitch-black")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title('Truepeoplesearch Scraper')
root.geometry("500x500")


def start():
    spreadsheet_id = spreadsheet_id_entry.get()
    spreadsheet_name = spreadsheet_name_entry.get()
    leads_file_name = leads_file_name_entry.get()
    street_column = street_column_entry.get()
    zip_column = zip_column_entry.get()
    license_key = license_key_entry.get()

    print(f"Sheet ID: {spreadsheet_id}")
    print(f"Sheet Name: {spreadsheet_name}")
    print(f"Leads File: {leads_file_name}")
    print(f"Street Column: {street_column}")
    print(f"Zip Column: {zip_column}")
    print(f"License Key: {license_key}")


frame = ctk.CTkFrame(master=root)
frame.pack(pady=25, padx=50, fill="both", expand=True)

label = ctk.CTkLabel(master=frame, text="Settings", font=("Roboto", 24))
label.pack(pady=15, padx=15)

spreadsheet_id_entry = ctk.CTkEntry(master=frame, placeholder_text="Spreadsheet ID")
spreadsheet_id_entry.pack(pady=12, padx=10)

spreadsheet_name_entry = ctk.CTkEntry(master=frame, placeholder_text="Spreadsheet Name")
spreadsheet_name_entry.insert(0, "Date")
spreadsheet_name_entry.pack(pady=12, padx=10)

leads_file_name_entry = ctk.CTkEntry(master=frame, placeholder_text="CSV File Name")
leads_file_name_entry.pack(pady=12, padx=10)

street_column_entry = ctk.CTkEntry(master=frame, placeholder_text="Street Column")
street_column_entry.insert(0, "16")
street_column_entry.pack(pady=12, padx=10)

zip_column_entry = ctk.CTkEntry(master=frame, placeholder_text="Street Column")
zip_column_entry.insert(0, "20")
zip_column_entry.pack(pady=12, padx=10)

license_key_entry = ctk.CTkEntry(master=frame, placeholder_text="License Key", show="*")
license_key_entry.pack(pady=12, padx=10)

button_entry = ctk.CTkButton(master=frame, text="Start", command=start)
button_entry.pack(pady=12, padx=10)

root.mainloop()