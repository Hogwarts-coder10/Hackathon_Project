import flet as ft
import json
import logging
import os
from datetime import datetime
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    # Page setup
    page.title = "Advanced Carbon Footprint Calculator"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 700
    page.window_min_width = 600
    page.window_min_height = 500
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_900

    # Custom theme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.TEAL_700,
            on_primary=ft.Colors.WHITE,
            secondary=ft.Colors.AMBER_700,
            background=ft.Colors.GREY_900
        )
    )

    # Header
    header = ft.Row([
        ft.Icon(ft.Icons.ECO, color=ft.Colors.TEAL_400, size=40),
        ft.Text("Carbon Footprint Calculator", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.IconButton(ft.Icons.INFO, tooltip="About", on_click=lambda e: show_about_dialog(page))
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Input creation function
    def create_input(label, hint, units, tooltip):
        return ft.Column([
            ft.Text(label, color=ft.Colors.GREY_300),
            ft.TextField(
                width=250,
                hint_text=hint,
                keyboard_type=ft.KeyboardType.NUMBER,
                suffix_text=units,
                border_color=ft.Colors.TEAL_200,
                text_style=ft.TextStyle(color=ft.Colors.WHITE),
                hint_style=ft.TextStyle(color=ft.Colors.GREY_500),
                tooltip=tooltip,
                border_radius=8
            )
        ], spacing=8)

    # Inputs
    inputs = {
        "electricity": create_input("Monthly Electricity Usage", "Enter kWh", "kWh", "Avg US: 900 kWh/month"),
        "gas": create_input("Monthly Natural Gas Usage", "Enter therms", "therms", "Avg US: 50 therms/month"),
        "water": create_input("Monthly Water Usage", "Enter liters", "liters", "Avg: 300 liters/day"),
        "kilometers": create_input("Monthly Kilometers Driven", "Enter km", "km", "Avg US: 1,600 km/month"),
        "flights": create_input("Number of Flights per Year", "Enter flights", "flights", "Avg US: 2 flights/year"),
        "food": create_input("Monthly Meat Consumption", "Enter kg", "kg", "Avg US: 7 kg/month")
    }

    # Unit toggle
    unit_switch = ft.Switch(label="Use Imperial Units", value=False, on_change=lambda e: toggle_units(e))

    # UI elements
    result_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.TEAL_400)
    individual_results = ft.Column(spacing=10, visible=False)
    progress_bar = ft.ProgressBar(width=600, value=0, color=ft.Colors.TEAL_600, bgcolor=ft.Colors.GREY_800)
    chart_container = ft.Container(
        width=600, 
        height=400, 
        bgcolor=ft.Colors.GREY_800,  # Fixed from GREY_50 to match dark theme
        border_radius=10,
        alignment=ft.alignment.center
    )
    chart_type_dropdown = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option("Pie", "Pie Chart"),
            ft.dropdown.Option("Bar", "Bar Chart")
        ],
        value="Pie",
        label="Chart Type",
        bgcolor=ft.Colors.GREY_800,
        text_style=ft.TextStyle(color=ft.Colors.WHITE)
    )

    # Conversion factors
    conversion_factors = {
        "metric": {"electricity": 0.92, "gas": 5.3, "water": 0.00007, "kilometers": 0.245, "flights": 900, "food": 2.5},
        "imperial": {"electricity": 0.42, "gas": 5.3, "water": 0.00026, "kilometers": 0.394, "flights": 900, "food": 1.13}
    }

    # Calculate footprint
    def calculate_footprint(e):
        try:
            values = [float(inputs[key].controls[1].value or 0) for key in inputs]
            if any(val < 0 for val in values):
                show_snack_bar(page, "Please enter non-negative values", ft.Colors.RED_700)
                return

            unit_system = "imperial" if unit_switch.value else "metric"
            factors = conversion_factors[unit_system]
            categories = ["Electricity", "Gas", "Water", "Driving", "Flights", "Food"]
            footprints = [values[i] * factors[list(inputs.keys())[i]] for i in range(len(values))]
            total_footprint = sum(footprints)

            unit_label = "lbs CO2/month" if unit_switch.value else "kg CO2/month"
            result_text.value = f"Total Carbon Footprint: {total_footprint:.2f} {unit_label}"
            individual_results.controls = [
                ft.Text(f"{cat}: {val:.2f} {unit_label}", color=ft.Colors.GREY_300)
                for cat, val in zip(categories, footprints)
            ]
            individual_results.visible = True
            progress_bar.value = min(total_footprint / (11000 if unit_switch.value else 5000), 1.0)

            # Generate native Flet chart
            colors = [
                ft.Colors.TEAL_400,
                ft.Colors.RED_400,
                ft.Colors.BLUE_400,
                ft.Colors.YELLOW_400,
                ft.Colors.PURPLE_400,
                ft.Colors.ORANGE_400
            ]
            if chart_type_dropdown.value == "Pie":
                chart_container.content = ft.PieChart(
                    sections=[
                        ft.PieChartSection(
                            value=max(val, 0.001),  # Ensure non-zero for visibility
                            title=f"{cat}\n{val:.1f}",
                            color=color,
                            radius=150
                        ) for val, cat, color in zip(footprints, categories, colors)
                    ],
                    sections_space=2,
                    center_space_radius=40
                )
            else:
                chart_container.content = ft.BarChart(
                    bar_groups=[
                        ft.BarChartGroup(
                            x=i,
                            bar_rods=[ft.BarChartRod(from_y=0, to_y=val, width=40, color=color)]
                        ) for i, (val, color) in enumerate(zip(footprints, colors))
                    ],
                    bottom_axis=ft.ChartAxis(
                        labels=[ft.ChartAxisLabel(value=i, label=ft.Text(cat)) for i, cat in enumerate(categories)],
                        labels_size=40
                    ),
                    left_axis=ft.ChartAxis(labels_size=40),
                    tooltip_bgcolor=ft.Colors.GREY_800
                )

            page.update()
            logger.info("Calculation completed")
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            show_snack_bar(page, "Please enter valid numbers", ft.Colors.RED_700)
        except Exception as e:
            logger.error(f"Calculation error: {str(e)}")
            show_snack_bar(page, f"Error: {str(e)}", ft.Colors.RED_700)

    # Toggle units
    def toggle_units(e):
        units = {
            "metric": {"electricity": "kWh", "gas": "therms", "water": "liters", "kilometers": "km", "flights": "flights", "food": "kg"},
            "imperial": {"electricity": "kWh", "gas": "therms", "water": "gallons", "kilometers": "miles", "flights": "flights", "food": "lbs"}
        }
        unit_system = "imperial" if e.control.value else "metric"
        for key, input_field in inputs.items():
            input_field.controls[1].suffix_text = units[unit_system][key]
        calculate_footprint(None)  # Recalculate with new units
        page.update()

    # Save data
    def save_data(e):
        try:
            data = {key: input_field.controls[1].value for key, input_field in inputs.items()}
            data["unit_system"] = "imperial" if unit_switch.value else "metric"
            data["timestamp"] = datetime.now().isoformat()
            with open("footprint_data.json", "w") as f:
                json.dump(data, f, indent=2)
            show_snack_bar(page, "Data saved successfully!", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Save error: {str(e)}")
            show_snack_bar(page, "Error saving data", ft.Colors.RED_700)

    # Load data
    def load_data(e):
        try:
            with open("footprint_data.json", "r") as f:
                data = json.load(f)
            for key, input_field in inputs.items():
                input_field.controls[1].value = data.get(key, "")
            unit_switch.value = data.get("unit_system", "metric") == "imperial"
            toggle_units(ft.ControlEvent(control=unit_switch, data=unit_switch.value))
            calculate_footprint(None)
            show_snack_bar(page, f"Data loaded from {data.get('timestamp', 'unknown time')}", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Load error: {str(e)}")
            show_snack_bar(page, "No saved data found", ft.Colors.RED_700)

    # Export to CSV
    def export_csv(e):
        try:
            values = [float(inputs[key].controls[1].value or 0) for key in inputs]
            unit_system = "imperial" if unit_switch.value else "metric"
            factors = conversion_factors[unit_system]
            categories = ["Electricity", "Gas", "Water", "Driving", "Flights", "Food"]
            footprints = [values[i] * factors[list(inputs.keys())[i]] for i in range(len(values))]
            total_footprint = sum(footprints)

            filename = f"carbon_footprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", f"CO2 ({'lbs' if unit_switch.value else 'kg'})"])
                for cat, val in zip(categories, footprints):
                    writer.writerow([cat, f"{val:.2f}"])
                writer.writerow(["Total", f"{total_footprint:.2f}"])
            show_snack_bar(page, f"Exported to {filename}", ft.Colors.GREEN_700)
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            show_snack_bar(page, "Error exporting data", ft.Colors.RED_700)

    # Reset form
    def reset_form(e):
        for input_field in inputs.values():
            input_field.controls[1].value = ""
        result_text.value = ""
        individual_results.controls = []
        individual_results.visible = False
        progress_bar.value = 0
        chart_container.content = None
        page.update()

    # Helper functions
    def show_snack_bar(page, message, color):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def show_about_dialog(page):
        dlg = ft.AlertDialog(
            title=ft.Text("About"),
            content=ft.Text(
                "Advanced Carbon Footprint Calculator\nVersion 2.0\nCreated with Flet",
                color=ft.Colors.GREY_300
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: close_dialog(page))],
            bgcolor=ft.Colors.GREY_800
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def close_dialog(page):
        page.dialog.open = False
        page.update()

    # Buttons
    buttons = ft.Row([
        ft.ElevatedButton("Calculate", on_click=calculate_footprint, bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE),
        ft.ElevatedButton("Reset", on_click=reset_form, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
        ft.ElevatedButton("Save", on_click=save_data, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
        ft.ElevatedButton("Load", on_click=load_data, bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
        ft.ElevatedButton("Export CSV", on_click=export_csv, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    # Layout
    input_grid = ft.Column([
        ft.Row([inputs["electricity"], inputs["gas"]], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([inputs["water"], inputs["kilometers"]], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([inputs["flights"], inputs["food"]], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=20)

    settings_row = ft.Row([unit_switch, chart_type_dropdown], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

    page.add(
        header,
        ft.Divider(color=ft.Colors.GREY_700),
        settings_row,
        ft.Container(input_grid, padding=20, bgcolor=ft.Colors.GREY_800, border_radius=10),
        buttons,
        ft.Container(result_text, padding=10, alignment=ft.alignment.center),
        ft.Container(individual_results, padding=10, bgcolor=ft.Colors.GREY_800, border_radius=10),
        ft.Container(progress_bar, padding=10),
        ft.Container(chart_container, alignment=ft.alignment.center, padding=10)
    )
    logger.info("Page setup complete")

if __name__ == "__main__":
    try:
        logger.info("Starting desktop application")
        ft.app(target=main)  # Run as desktop app
        logger.info("Application launched successfully")
    except Exception as e:
        logger.error(f"Failed to launch: {str(e)}")
        raise

# Padding for future enhancements
"""
# Potential Future Enhancements:
# - Add real-time input validation
# - Implement user profiles with login
# - Add historical data tracking
# - Include carbon offset suggestions
# - Add regional emission factor adjustments
# - Implement chart animations
# - Add export to PDF
# - Include comparison with global averages
# - Add multilingual support
# - Implement theme switching
"""