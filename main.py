import flet as ft
import requests
import json
from typing import Dict, Any, Optional
import os

class PatientProfileViewer:
    """Professional patient profile viewer with secure API integration"""
    
    def __init__(self):
        self.api_base_url = os.getenv('MEDICAL_API_URL', 'https://localhost:8443/ords/medical_sys_api')
        self.api_endpoint = f"{self.api_base_url}/basic_sec_api/basic_sec_view_r_profile_patient"
        self.timeout = 30
        
    def get_ssl_verification(self) -> bool:
        """Get SSL verification setting from environment"""
        return os.getenv('SSL_VERIFY', 'true').lower() != 'false'
    
    def validate_patient_id(self, patient_id: str) -> bool:
        """Validate patient ID format"""
        if not patient_id or not patient_id.strip():
            return False
        # Basic validation: alphanumeric and reasonable length
        clean_id = patient_id.strip()
        return clean_id.isalnum() and 1 <= len(clean_id) <= 20
    
    def make_secure_request(self, patient_id: str) -> Optional[Dict[Any, Any]]:
        """Make secure API request with proper error handling"""
        try:
            # Validate input
            if not self.validate_patient_id(patient_id):
                raise ValueError("Invalid patient ID format")
            
            url = f"{self.api_endpoint}/{patient_id.strip()}"
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'PatientProfileViewer/1.0'
            }
            
            # Get authentication if configured
            auth = self._get_auth_credentials()
            
            # Make request
            response = requests.get(
                url,
                headers=headers,
                auth=auth,
                verify=self.get_ssl_verification(),
                timeout=self.timeout
            )
            
            # Check response status
            response.raise_for_status()
            
            # Validate JSON response
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON response from server")
                
        except requests.exceptions.HTTPError as e:
            raise ConnectionError(f"HTTP Error: {e.response.status_code} - {e.response.reason}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Unable to connect to server. Please check server status and network connection.")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")
    
    def _get_auth_credentials(self):
        """Get authentication credentials from environment variables"""
        username = os.getenv('API_USERNAME')
        password = os.getenv('API_PASSWORD')
        
        if username and password:
            return (username, password)
        return None


def main(page: ft.Page):
    # Initialize viewer
    viewer = PatientProfileViewer()
    
    # Configure page
    page.title = "Patient Profile Viewer - Secure Medical System"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 1000
    page.window_height = 800
    page.window_resizable = True
    
    # Disable SSL warnings only when explicitly disabled
    if not viewer.get_ssl_verification():
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            pass

    # State management
    patient_id_field = ft.TextField(
        label="Patient ID",
        hint_text="Enter patient identifier...",
        value="1",
        width=250,
        text_size=14,
        content_padding=10,
        border_radius=8,
        filled=True,
        bgcolor=ft.colors.WHITE
    )
    
    status_text = ft.Text("", size=14)
    loading_indicator = ft.ProgressRing(visible=False)
    
    data_container = ft.Column(
        spacing=15,
        width=900,
        alignment=ft.MainAxisAlignment.START
    )

    def show_message(title: str, message: str, error: bool = False):
        """Show user-friendly message dialog"""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=ft.colors.ERROR if error else ft.colors.GREEN),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def update_status(message: str, error: bool = False, success: bool = False):
        """Update status text with appropriate styling"""
        status_text.value = message
        if success:
            status_text.color = ft.colors.GREEN
        elif error:
            status_text.color = ft.colors.RED
        else:
            status_text.color = ft.colors.BLUE_GREY
        page.update()

    def format_field_value(value: Any) -> str:
        """Safely format field values for display"""
        if value is None or value == "" or value == "string":
            return "N/A"
        return str(value).strip()

    def format_date(date_str: str) -> str:
        """Format date strings safely"""
        if not date_str or date_str == "string":
            return "N/A"
        return date_str

    def create_data_card(title: str, icon: str, items: list) -> ft.Card:
        """Create a standardized data card"""
        content_rows = [
            ft.ListTile(
                leading=ft.Icon(icon, color=ft.colors.BLUE),
                title=ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
            ),
            ft.Divider(thickness=1)
        ]
        
        content_rows.extend(items)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(content_rows),
                padding=15,
            ),
            elevation=2,
            shadow_color=ft.colors.GREY_300
        )

    def create_data_row(label: str, value: str, width: int = 400) -> ft.Container:
        """Create a standardized data display row"""
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{label}:", 
                       width=180, 
                       weight=ft.FontWeight.W_500, 
                       color=ft.colors.BLUE_GREY_700,
                       text_align=ft.TextAlign.RIGHT),
                ft.SelectableText(
                    value=value,
                    width=width,
                    style=page.theme.text_style_headline_small
                ),
            ], 
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=10),
            padding=ft.padding.only(bottom=8)
        )

    def display_patient_data(data: Dict[str, Any]):
        """Display patient data in organized cards"""
        try:
            # Clear existing data
            data_container.controls.clear()
            
            # Validate response structure
            if not isinstance(data, dict):
                raise ValueError("Invalid response format")
            
            items = data.get('items', [])
            if not items or not isinstance(items, list):
                data_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.WARNING, color=ft.colors.ORANGE, size=40),
                            ft.Text("No patient data available", size=18, color=ft.colors.RED)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
                return
            
            patient = items[0]  # Take first patient record
            
            # Create organized cards
            cards = []
            
            # Personal Information
            personal_items = [
                create_data_row("Full Name", format_field_value(patient.get('full_name'))),
                create_data_row("Patient ID", format_field_value(patient.get('patientid'))),
                create_data_row("Date of Birth", format_date(patient.get('dateofbirth'))),
                create_data_row("Age", format_field_value(patient.get('age'))),
                create_data_row("Gender", format_field_value(patient.get('gender'))),
                create_data_row("Marital Status", format_field_value(patient.get('maritalstatus')))
            ]
            cards.append(create_data_card("Personal Information", ft.icons.PERSON, personal_items))
            
            # Contact Information
            contact_items = [
                create_data_row("Email", format_field_value(patient.get('email'))),
                create_data_row("Primary Phone", format_field_value(patient.get('phone_primary'))),
                create_data_row("Address", format_field_value(patient.get('address'))),
                create_data_row("ID Number", format_field_value(patient.get('personalnumberid')))
            ]
            cards.append(create_data_card("Contact Information", ft.icons.CONTACT_PHONE, contact_items))
            
            # Medical Information
            medical_items = [
                create_data_row("Blood Type", format_field_value(patient.get('bloodtype'))),
                create_data_row("Allergies", format_field_value(patient.get('allergies'))),
                create_data_row("Chronic Diseases", format_field_value(patient.get('chronicdiseases'))),
                create_data_row("Current Medications", format_field_value(patient.get('currentmedications'))),
                create_data_row("Medical History", format_field_value(patient.get('medicalhistory'))),
                create_data_row("Previous Surgeries", format_field_value(patient.get('previoussurgeries')))
            ]
            cards.append(create_data_card("Medical Information", ft.icons.HEALTH_AND_SAFETY, medical_items))
            
            # Emergency Contact
            emergency_items = [
                create_data_row("Emergency Contact", format_field_value(patient.get('emergencycontactname'))),
                create_data_row("Emergency Phone", format_field_value(patient.get('emergencycontactphone')))
            ]
            cards.append(create_data_card("Emergency Contact", ft.icons.EMERGENCY, emergency_items))
            
            # Add all cards to container
            data_container.controls.extend(cards)
            
        except Exception as e:
            show_message("Data Error", f"Error displaying patient data: {str(e)}", error=True)

    def fetch_patient_data(e):
        """Fetch and display patient data"""
        try:
            # Validate input
            patient_id = patient_id_field.value
            if not patient_id or not patient_id.strip():
                update_status("Please enter a valid patient ID", error=True)
                return
            
            # Show loading state
            loading_indicator.visible = True
            update_status("Fetching patient data...")
            page.update()
            
            # Fetch data
            data = viewer.make_secure_request(patient_id)
            
            # Update UI with success
            display_patient_data(data)
            update_status(f"Successfully loaded patient data for ID: {patient_id}", success=True)
            
        except ValueError as ve:
            update_status(f"Input Error: {str(ve)}", error=True)
        except ConnectionError as ce:
            update_status(f"Connection Error: {str(ce)}", error=True)
        except TimeoutError as te:
            update_status(f"Timeout: {str(te)}", error=True)
        except RuntimeError as re:
            update_status(f"Runtime Error: {str(re)}", error=True)
        except Exception as ex:
            update_status(f"Unexpected Error: {str(ex)}", error=True)
        finally:
            # Always hide loading indicator
            loading_indicator.visible = False
            page.update()

    def clear_display(e):
        """Clear displayed data and reset form"""
        data_container.controls.clear()
        patient_id_field.value = "1"
        status_text.value = ""
        status_text.color = ft.colors.BLUE_GREY
        page.update()

    def show_about_dialog(e):
        """Show application information"""
        def close_dialog(e):
            about_dlg.open = False
            page.update()
        
        about_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("About Patient Profile Viewer"),
            content=ft.Column([
                ft.Text("Secure Medical System Client", weight=ft.FontWeight.BOLD),
                ft.Text("Version 1.0 Professional Edition"),
                ft.Text("Built with security and reliability in mind."),
                ft.Divider(),
                ft.Text("API Configuration:", weight=ft.FontWeight.BOLD),
                ft.Text(f"Base URL: {viewer.api_base_url}"),
                ft.Text("Authentication: Environment-based"),
                ft.Text("SSL Verification: " + ("Enabled" if viewer.get_ssl_verification() else "Disabled"))
            ], tight=True, spacing=10),
            actions=[ft.TextButton("Close", on_click=close_dialog)]
        )
        page.dialog = about_dlg
        about_dlg.open = True
        page.update()

    # Create UI components
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.MEDICAL_INFORMATION, color=ft.colors.BLUE, size=40),
            ft.Column([
                ft.Text("Patient Profile Viewer", 
                       size=28, 
                       weight=ft.FontWeight.BOLD,
                       color=ft.colors.BLUE_800),
                ft.Text("Secure Medical System Client",
                       size=14,
                       color=ft.colors.GREY_600),
            ], spacing=2),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.icons.INFO_OUTLINE,
                on_click=show_about_dialog,
                tooltip="About Application",
                icon_size=24
            )
        ],
        alignment=ft.MainAxisAlignment.START),
        margin=ft.margin.only(bottom=30)
    )

    input_section = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Patient Identification", size=16, weight=ft.FontWeight.W_500),
                patient_id_field,
                ft.Row([
                    ft.FilledButton(
                        "Fetch Patient Data",
                        icon=ft.icons.DOWNLOAD,
                        on_click=fetch_patient_data,
                        style=ft.ButtonStyle(
                            padding=ft.Padding(20, 12, 20, 12),
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE_600
                        )
                    ),
                    ft.OutlinedButton(
                        "Clear",
                        icon=ft.icons.CLEAR,
                        on_click=clear_display,
                        style=ft.ButtonStyle(
                            padding=ft.Padding(20, 12, 20, 12)
                        )
                    ),
                    ft.Container(
                        content=loading_indicator,
                        padding=10
                    )
                ], 
                spacing=15, 
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15),
            padding=20,
        ),
        elevation=3,
        width=500
    )

    status_section = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=ft.colors.BLUE_GREY),
            status_text
        ], spacing=10),
        margin=ft.margin.only(top=10, bottom=10)
    )

    instructions = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.INFO, color=ft.colors.BLUE_500),
                    ft.Text("Usage Instructions", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Divider(height=1),
                ft.Text("• Enter a valid patient ID in the field above", size=12),
                ft.Text("• Click 'Fetch Patient Data' to retrieve patient information", size=12),
                ft.Text("• Use 'Clear' to reset the display", size=12),
                ft.Text("• Ensure your API server is accessible and properly configured", size=12),
            ], spacing=8),
            padding=15,
        ),
        color=ft.colors.BLUE_50,
        elevation=1,
        width=500
    )

    # Main layout
    main_column = ft.Column(
        controls=[
            header,
            input_section,
            instructions,
            status_section,
            ft.Divider(thickness=1),
            data_container
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    page.add(main_column)


if __name__ == "__main__":
    ft.app(target=main)