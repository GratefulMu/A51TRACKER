import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading
import csv

# Define the boundaries of the Nevada National Security Site (NNSS)
NNSS_BOUNDARIES = {
    "min_lat": 36.5,
    "max_lat": 37.5,
    "min_lon": -116.5,
    "max_lon": -115.5
}

# Sample ICAO codes for demonstration purposes
SAMPLE_ICAO_CODES = ["45211e", "a12345", "b67890"]

class ADSBMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADSB Monitor")

        # API Endpoint Entry
        self.api_frame = tk.Frame(root)
        self.api_frame.pack(pady=10)

        self.api_label = tk.Label(self.api_frame, text="API Base URL:")
        self.api_label.grid(row=0, column=0)
        self.api_entry = tk.Entry(self.api_frame, width=50)
        self.api_entry.grid(row=0, column=1)
        self.api_entry.insert(0, "https://api.airplanes.live/v2/icao/")  # Default value, change if needed

        # Connectivity Status Display
        self.status_label = tk.Label(root, text="Status: Unknown", fg="black")
        self.status_label.pack()

        # Boundaries Entries
        self.boundaries_frame = tk.Frame(root)
        self.boundaries_frame.pack(pady=10)

        self.min_lat_label = tk.Label(self.boundaries_frame, text="Min Latitude:")
        self.min_lat_label.grid(row=0, column=0)
        self.min_lat_entry = tk.Entry(self.boundaries_frame, width=10)
        self.min_lat_entry.grid(row=0, column=1)
        self.min_lat_entry.insert(0, str(NNSS_BOUNDARIES["min_lat"]))

        self.max_lat_label = tk.Label(self.boundaries_frame, text="Max Latitude:")
        self.max_lat_label.grid(row=0, column=2)
        self.max_lat_entry = tk.Entry(self.boundaries_frame, width=10)
        self.max_lat_entry.grid(row=0, column=3)
        self.max_lat_entry.insert(0, str(NNSS_BOUNDARIES["max_lat"]))

        self.min_lon_label = tk.Label(self.boundaries_frame, text="Min Longitude:")
        self.min_lon_label.grid(row=1, column=0)
        self.min_lon_entry = tk.Entry(self.boundaries_frame, width=10)
        self.min_lon_entry.grid(row=1, column=1)
        self.min_lon_entry.insert(0, str(NNSS_BOUNDARIES["min_lon"]))

        self.max_lon_label = tk.Label(self.boundaries_frame, text="Max Longitude:")
        self.max_lon_label.grid(row=1, column=2)
        self.max_lon_entry = tk.Entry(self.boundaries_frame, width=10)
        self.max_lon_entry.grid(row=1, column=3)
        self.max_lon_entry.insert(0, str(NNSS_BOUNDARIES["max_lon"]))

        # Start Button
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        # Log Display
        self.log_text = tk.Text(root, height=15, width=80)
        self.log_text.pack(pady=10)

        self.monitoring = False

    def fetch_aircraft_details(self, icao):
        url = f"{self.api_entry.get()}{icao}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            self.status_label.config(text="Status: Connected", fg="green")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except requests.exceptions.JSONDecodeError as json_err:
            print(f"JSON decode error occurred: {json_err}")
        self.status_label.config(text="Status: Disconnected", fg="red")
        return None

    def is_within_boundaries(self, lat, lon):
        return (self.boundaries['min_lat'] <= lat <= self.boundaries['max_lat'] and
                self.boundaries['min_lon'] <= lon <= self.boundaries['max_lon'])

    def log_aircraft_entry(self, aircraft):
        log_entry = f"{time.ctime()} - ICAO: {aircraft['hex']} - Callsign: {aircraft.get('flight', 'N/A')} - Lat: {aircraft['lat']} - Lon: {aircraft['lon']}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

        # Write the entry to a CSV file
        with open('aircraft_log.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.ctime(), aircraft['hex'], aircraft.get('flight', 'N/A'), aircraft['lat'], aircraft['lon']])

    def monitor_airspace(self):
        print("Monitoring process has started.")
        self.seen_aircraft = set()

        # Create CSV file and write header if it doesn't exist
        with open('aircraft_log.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'ICAO', 'Callsign', 'Latitude', 'Longitude'])

        while self.monitoring:
            for icao in SAMPLE_ICAO_CODES:  # Use sample ICAO codes
                details = self.fetch_aircraft_details(icao)
                if details:
                    lat = details.get('lat', None)
                    lon = details.get('lon', None)
                    if lat and lon and self.is_within_boundaries(lat, lon):
                        if icao not in self.seen_aircraft:
                            self.log_aircraft_entry(details)
                            self.seen_aircraft.add(icao)
            time.sleep(60)  # Wait for a minute before fetching data again

    def start_monitoring(self):
        self.boundaries = {
            "min_lat": float(self.min_lat_entry.get()),
            "max_lat": float(self.max_lat_entry.get()),
            "min_lon": float(self.min_lon_entry.get()),
            "max_lon": float(self.max_lon_entry.get())
        }
        self.monitoring = True
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.monitor_airspace).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ADSBMonitorApp(root)
    root.mainloop()