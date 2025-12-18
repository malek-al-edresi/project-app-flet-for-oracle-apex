import flet as ft
import requests
import json

def main(page: ft.Page):
    # Configure page
    page.title = "Patient Profile Viewer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Disable SSL warnings for localhost
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        pass

    # State variables
    patient_id = ft.Ref[ft.TextField]()
    response_text = ft.Ref[ft.Text]()
    data_container = ft.Ref[ft.Column]()
    loading_indicator = ft.Ref[ft.ProgressRing]()

    def fetch_patient_data(e):
        """Fetch patient data from API"""
        try:
            # Show loading indicator
            loading_indicator.current.visible = True
            page.update()
            
            pid = patient_id.current.value.strip()
            if not pid:
                pid = "1"
            
            # API endpoint
            url = f"https://localhost:8443/ords/medical_sys_api/basic_sec_api/basic_sec_view_r_profile_patient/{pid}"
            
            # Make request with timeout
            response = requests.get(url, verify=False, timeout=10)
            
            # Hide loading indicator
            loading_indicator.current.visible = False
            
            if response.status_code == 200:
                data = response.json()
                display_patient_data(data)
                response_text.current.value = f"✅ Success! Status: {response.status_code}"
                response_text.current.color = ft.colors.GREEN
            else:
                response_text.current.value = f"❌ Error! Status: {response.status_code}"
                response_text.current.color = ft.colors.RED
                show_error(f"Failed to fetch data. Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            loading_indicator.current.visible = False
            response_text.current.value = "❌ Connection Error"
            response_text.current.color = ft.colors.RED
            show_error("Cannot connect to server. Make sure:\n1. The server is running on https://localhost:8443\n2. The ORDS service is active")
        except requests.exceptions.Timeout:
            loading_indicator.current.visible = False
            response_text.current.value = "❌ Timeout Error"
            response_text.current.color = ft.colors.RED
            show_error("Request timed out. Check your connection.")
        except json.JSONDecodeError:
            loading_indicator.current.visible = False
            response_text.current.value = "❌ Invalid JSON Response"
            response_text.current.color = ft.colors.RED
            show_error("Server returned invalid JSON. Check if the endpoint is correct.")
        except Exception as ex:
            loading_indicator.current.visible = False
            response_text.current.value = f"❌ Error: {str(ex)[:50]}..."
            response_text.current.color = ft.colors.RED
            show_error(f"An error occurred: {str(ex)}")
        
        page.update()

    def show_error(message):
        """Show error dialog"""
        def close_dialog(e):
            error_dialog.open = False
            page.update()
        
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error", color=ft.colors.RED),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)]
        )
        page.dialog = error_dialog
        error_dialog.open = True

    def display_patient_data(data):
        """Display patient data in the UI"""
        # Clear previous data
        data_container.current.controls.clear()
        
        if 'items' in data and len(data['items']) > 0:
            patient = data['items'][0]
            
            # Create data cards
            cards = []
            
            # Personal Information Card
            personal_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.PERSON, color=ft.colors.BLUE),
                            title=ft.Text("Personal Information", weight=ft.FontWeight.BOLD, size=16),
                        ),
                        ft.Divider(),
                        create_data_row("Full Name", patient.get('full_name', 'N/A')),
                        create_data_row("Patient ID", patient.get('patientid', 'N/A')),
                        create_data_row("Date of Birth", format_date(patient.get('dateofbirth'))),
                        create_data_row("Age", str(patient.get('age', 'N/A'))),
                        create_data_row("Gender", patient.get('gender', 'N/A')),
                        create_data_row("Marital Status", patient.get('maritalstatus', 'N/A')),
                    ]),
                    padding=15,
                ),
                elevation=3
            )
            cards.append(personal_info)
            
            # Contact Information Card
            contact_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.CONTACT_PHONE, color=ft.colors.GREEN),
                            title=ft.Text("Contact Information", weight=ft.FontWeight.BOLD, size=16),
                        ),
                        ft.Divider(),
                        create_data_row("Email", patient.get('email', 'N/A')),
                        create_data_row("Phone", patient.get('phone_primary', 'N/A')),
                        create_data_row("Address", patient.get('address', 'N/A')),
                        create_data_row("Personal Number ID", patient.get('personalnumberid', 'N/A')),
                    ]),
                    padding=15,
                ),
                elevation=3
            )
            cards.append(contact_info)
            
            # Medical Information Card
            medical_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.HEALTH_AND_SAFETY, color=ft.colors.RED),
                            title=ft.Text("Medical Information", weight=ft.FontWeight.BOLD, size=16),
                        ),
                        ft.Divider(),
                        create_data_row("Blood Type", patient.get('bloodtype', 'N/A')),
                        create_data_row("Allergies", format_text(patient.get('allergies'))),
                        create_data_row("Chronic Diseases", format_text(patient.get('chronicdiseases'))),
                        create_data_row("Current Medications", format_text(patient.get('currentmedications'))),
                        create_data_row("Medical History", format_text(patient.get('medicalhistory'))),
                        create_data_row("Previous Surgeries", format_text(patient.get('previoussurgeries'))),
                    ]),
                    padding=15,
                ),
                elevation=3
            )
            cards.append(medical_info)
            
            # Emergency Contact Card
            emergency_info = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.EMERGENCY, color=ft.colors.ORANGE),
                            title=ft.Text("Emergency Contact", weight=ft.FontWeight.BOLD, size=16),
                        ),
                        ft.Divider(),
                        create_data_row("Contact Name", patient.get('emergencycontactname', 'N/A')),
                        create_data_row("Contact Phone", patient.get('emergencycontactphone', 'N/A')),
                    ]),
                    padding=15,
                ),
                elevation=3
            )
            cards.append(emergency_info)
            
            # Add all cards to container
            for card in cards:
                data_container.current.controls.append(card)
                
        else:
            data_container.current.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WARNING, color=ft.colors.ORANGE, size=40),
                        ft.Text("No patient data found", size=18, color=ft.colors.RED)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    padding=20
                )
            )

    def create_data_row(label, value):
        """Create a formatted row for data display"""
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{label}:", width=200, weight=ft.FontWeight.W_500, color=ft.colors.BLUE_GREY_700),
                ft.Text(value if value and value != "string" else "N/A", 
                       width=400,
                       selectable=True),
            ], 
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=10),
            padding=ft.padding.only(bottom=8)
        )

    def format_date(date_str):
        """Format date string"""
        if not date_str or date_str == "string":
            return "N/A"
        return date_str

    def format_text(text):
        """Format text fields"""
        if not text or text == "string":
            return "N/A"
        # Add line breaks for long text
        if len(text) > 100:
            return text[:100] + "..."
        return text

    def clear_data(e):
        """Clear displayed data"""
        data_container.current.controls.clear()
        response_text.current.value = ""
        loading_indicator.current.visible = False
        page.update()

    def show_about(e):
        """Show about dialog"""
        def close_dialog(e):
            about_dialog.open = False
            page.update()
        
        about_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("About Patient Profile Viewer"),
            content=ft.Column([
                ft.Text("Medical System API Client", weight=ft.FontWeight.BOLD),
                ft.Text("Version 1.0"),
                ft.Text("Fetches patient data from ORDS API"),
                ft.Text("\nAPI Endpoint:"),
                ft.Text("https://localhost:8443/ords/medical_sys_api/", size=12),
            ], tight=True, spacing=10),
            actions=[ft.TextButton("Close", on_click=close_dialog)]
        )
        page.dialog = about_dialog
        about_dialog.open = True
        page.update()

    # Header
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.MEDICAL_SERVICES, color=ft.colors.BLUE, size=40),
            ft.Column([
                ft.Text("Patient Profile Viewer", 
                       size=28, 
                       weight=ft.FontWeight.BOLD,
                       color=ft.colors.BLUE_800),
                ft.Text("Medical System API Client",
                       size=14,
                       color=ft.colors.GREY_600),
            ]),
            ft.Container(width=100),  # Spacer
            ft.IconButton(
                icon=ft.icons.INFO,
                on_click=show_about,
                tooltip="About"
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER),
        margin=ft.margin.only(bottom=30)
    )

    # Input Section
    input_section = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Enter Patient ID", size=16, weight=ft.FontWeight.W_500),
                ft.TextField(
                    ref=patient_id,
                    label="Patient ID",
                    value="1",
                    width=250,
                    text_size=14,
                    content_padding=10,
                    border_color=ft.colors.BLUE_400,
                ),
                ft.Row([
                    ft.ElevatedButton(
                        "Fetch Patient Data",
                        icon=ft.icons.DOWNLOAD,
                        on_click=fetch_patient_data,
                        style=ft.ButtonStyle(
                            padding=20,
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_600
                        )
                    ),
                    ft.OutlinedButton(
                        "Clear",
                        icon=ft.icons.CLEAR,
                        on_click=clear_data,
                        style=ft.ButtonStyle(padding=20)
                    ),
                    ft.Container(
                        content=ft.ProgressRing(ref=loading_indicator, width=20, height=20, visible=False),
                        padding=10
                    )
                ], 
                spacing=20, 
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15),
            padding=20,
        ),
        elevation=5,
        width=500
    )

    # Status Section
    status_section = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.STATUS, color=ft.colors.BLUE_GREY),
            ft.Text(ref=response_text, size=14),
        ], spacing=10),
        margin=ft.margin.only(top=10, bottom=10)
    )

    # Data Display Section
    data_section = ft.Container(
        content=ft.Column(
            ref=data_container,
            spacing=15,
            width=900
        ),
        margin=ft.margin.only(top=20)
    )

    # Instructions
    instructions = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.INFO, color=ft.colors.BLUE_500),
                    ft.Text("Instructions", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=10),
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=14, color=ft.colors.GREEN),
                    ft.Text("Enter Patient ID (default is 1)", size=12),
                ], spacing=5),
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=14, color=ft.colors.GREEN),
                    ft.Text("Click 'Fetch Patient Data' to retrieve information", size=12),
                ], spacing=5),
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=14, color=ft.colors.GREEN),
                    ft.Text("Make sure ORDS server is running on https://localhost:8443", size=12),
                ], spacing=5),
            ], spacing=8),
            padding=15,
        ),
        color=ft.colors.BLUE_50,
        elevation=2,
        width=500
    )

    # Add all components to page
    page.add(
        header,
        input_section,
        instructions,
        status_section,
        data_section
    )

    # Auto-fetch data for patient 1 on startup (optional)
    # Uncomment the line below if you want auto-fetch on startup
    # fetch_patient_data(None)

if __name__ == "__main__":
    # Run the app
    ft.app(target=main)