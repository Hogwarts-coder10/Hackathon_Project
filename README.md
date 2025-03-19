# Hackathon Project
The Advanced Carbon Footprint Calculator is a desktop application built with Python and Flet that allows users to estimate their carbon footprint based on everyday activities such as electricity, natural gas, water, driving, air travel, and meat consumption. It provides a visual breakdown of emissions through pie or bar charts and supports both metric and imperial units.

Features
Input Categories: Calculate emissions from electricity (kWh), gas (therms), water (liters/gallons), driving (km/miles), flights (per year), and food (kg/lbs).
Unit Toggle: Switch between metric (kg CO2e) and imperial (lbs CO2e) units.
Visualization: View your carbon footprint breakdown with a Pie Chart or Bar Chart.
Progress Bar: See your total footprint relative to a reference value (5000 kg or 11000 lbs per month).
Data Persistence: Save your inputs to a JSON file and load them later.
Dark Theme: Modern, user-friendly interface with a customizable dark theme.
Error Handling: Input validation and clear error messages for usability.
Prerequisites
Python: Version 3.8 or higher.
Flet: Version 0.25.0 or higher (uses Colors and Icons enums).


Usage
Launch the App: Run the script to open the desktop application.
Enter Data: Fill in your monthly usage for electricity, gas, water, driving, flights (yearly), and food.
Select Units: Toggle the "Use Imperial Units" switch to switch between metric and imperial systems.
Calculate: Click "Calculate" to see your total carbon footprint and a breakdown by category.
Visualize: Use the "Chart Type" dropdown to switch between Pie and Bar charts.
Save/Load: Save your inputs with "Save" and retrieve them with "Load".
Reset: Clear all inputs and results with "Reset".
About: Click the info icon in the header for version and creator details.
How It Works
The calculator multiplies your inputs by emission factors to estimate CO2e emissions:

Electricity: 0.92 kg/kWh or 0.42 lbs/kWh
Gas: 5.3 kg/therm (both systems)
Water: 0.00007 kg/liter or 0.00026 lbs/gallon
Driving: 0.245 kg/km or 0.394 lbs/mile
Flights: 900 kg/flight (yearly impact)
Food: 2.5 kg/kg or 1.13 lbs/lb
The total footprint is displayed in kg or lbs per month, with flights contributing as an annualized value. Note: Some factors (e.g., electricity in imperial) may need adjustment for accuracy (see Limitations).

File Structure
carbon_calculator.py: Main application script.
footprint_data.json: Generated file for saving user inputs (created on first save).
Limitations
Emission Factors: Simplified averages; may not reflect regional variations (e.g., cleaner energy grids).
Flights: Annual input is summed directly into monthly total without normalization (may overestimate monthly impact).
Accuracy: Factors like 0.42 lbs/kWh for electricity seem low (typical US value ~1-2 lbs/kWh); verify against local data.
Static Factors: No option to customize factors without code modification.
Future Enhancements
Real-time input validation.
Historical data tracking.
Carbon offset suggestions (e.g., trees to plant).
Regional emission factor adjustments.
Export to PDF.
Multilingual support.
Light/dark theme switching.
Troubleshooting
"No saved data found": Ensure footprint_data.json exists in the app directory or save data first.
Invalid input errors: Enter only numeric values in the fields.
App not launching: Verify Flet is installed (pip show flet) and Python version is 3.8+.
Contributing:

Feel free to fork the repository, make improvements, and submit pull requests. Suggestions for emission factor updates or new features are welcome!
