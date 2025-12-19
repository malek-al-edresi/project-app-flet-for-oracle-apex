import flet as ft
import requests
import json
import os
from typing import Dict, Any

class PatientViewer:
    """Simple patient data viewer"""
    
    def __init__(self):
        self.api_url = os.getenv('API_URL', 'https://localhost:8443/ords/medical_sys_api')
        self.endpoint = f"{self.api_url}/basic_sec_api/basic_sec_view_r_profile_patient"
        
    def get_data(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data from API"""
        try:
            url = f"{self.endpoint}/{patient_id.strip()}"
            
            # Disable SSL warnings for development
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = requests.get(url, verify=False, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")

def main(page: ft.Page):
    # Page setup
    page.title = "Patient Data Viewer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Initialize viewer
    viewer = PatientViewer()
    
    # UI Elements
    patient_id_input = ft.TextField(
        label="Patient ID",
        hint_text="Enter patient ID...",
        value="1",
        width=200,
        text_size=16,
        border_radius=10
    )
    
    status_text = ft.Text("", size=14, color=ft.Colors.BLUE_700)
    loading = ft.ProgressRing(visible=False)
    data_container = ft.Column(spacing=10)
    
    def show_error(message: str):
        """Show error message"""
        page.snack_bar = ft.SnackBar(ft.Text(message, color=ft.Colors.WHITE), bgcolor=ft.Colors.RED)
        page.snack_bar.open = True
        page.update()
    
    def create_simple_row(label: str, value: str) -> ft.Row:
        """Create a simple data row"""
        return ft.Row([
            ft.Text(f"{label}:", 
                   weight=ft.FontWeight.BOLD, 
                   width=150,
                   color=ft.Colors.BLUE_800),
            ft.Text(value, size=14)
        ], spacing=10)
    
    def display_data(data: Dict[str, Any]):
        """Display patient data"""
        data_container.controls.clear()
        
        try:
            # Extract data from response
            items = []
            if isinstance(data, dict):
                if 'items' in data and data['items']:
                    items = data['items']
                elif 'data' in data and data['data']:
                    items = data['data']
                else:
                    items = [data]
            elif isinstance(data, list):
                items = data
            else:
                raise ValueError("Unexpected data format")
            
            if not items:
                data_container.controls.append(
                    ft.Text("No patient data found", size=18, color=ft.Colors.RED)
                )
                return
            
            patient = items[0]
            
            # Create cards with data
            cards = []
            
            # Personal Info
            personal_fields = []
            for field in ['full_name', 'patientid', 'dateofbirth', 'age', 'gender', 'maritalstatus']:
                if field in patient and patient[field]:
                    value = str(patient[field])
                    personal_fields.append(create_simple_row(field, value))
            
            if personal_fields:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Personal Information", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                *personal_fields
                            ], spacing=8),
                            padding=15
                        )
                    )
                )
            
            # Contact Info
            contact_fields = []
            for field in ['phone_primary', 'email', 'address', 'personalnumberid']:
                if field in patient and patient[field]:
                    value = str(patient[field])
                    contact_fields.append(create_simple_row(field, value))
            
            if contact_fields:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Contact Information", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                *contact_fields
                            ], spacing=8),
                            padding=15
                        )
                    )
                )
            
            # Medical Info
            medical_fields = []
            for field in ['bloodtype', 'allergies', 'chronicdiseases', 'currentmedications']:
                if field in patient and patient[field]:
                    value = str(patient[field])
                    medical_fields.append(create_simple_row(field, value))
            
            if medical_fields:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Medical Information", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                *medical_fields
                            ], spacing=8),
                            padding=15
                        )
                    )
                )
            
            # Emergency Contact
            emergency_fields = []
            for field in ['emergencycontactname', 'emergencycontactphone']:
                if field in patient and patient[field]:
                    value = str(patient[field])
                    emergency_fields.append(create_simple_row(field, value))
            
            if emergency_fields:
                cards.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Emergency Contact", size=18, weight=ft.FontWeight.BOLD),
                                ft.Divider(),
                                *emergency_fields
                            ], spacing=8),
                            padding=15
                        )
                    )
                )
            
            # Display all cards
            for card in cards:
                data_container.controls.append(card)
            
            # Show all fields in raw format (for debugging)
            if not cards:
                raw_data = ft.Column([
                    ft.Text("All available fields:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Divider()
                ])
                
                for key, value in patient.items():
                    if value:
                        raw_data.controls.append(
                            create_simple_row(key, str(value))
                        )
                
                data_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=raw_data,
                            padding=15
                        )
                    )
                )
                
        except Exception as e:
            show_error(f"Error displaying data: {str(e)}")
    
    def fetch_data(e):
        """Fetch and display data"""
        patient_id = patient_id_input.value.strip()
        if not patient_id:
            show_error("Please enter a patient ID")
            return
        
        try:
            # Show loading
            loading.visible = True
            status_text.value = f"Fetching data for patient {patient_id}..."
            page.update()
            
            # Get data
            data = viewer.get_data(patient_id)
            
            # Display data
            display_data(data)
            status_text.value = f"Successfully loaded data for patient {patient_id}"
            status_text.color = ft.Colors.GREEN
            
        except Exception as e:
            show_error(str(e))
            status_text.value = f"Error: {str(e)}"
            status_text.color = ft.Colors.RED
        finally:
            loading.visible = False
            page.update()
    
    def clear_data(e):
        """Clear displayed data"""
        data_container.controls.clear()
        patient_id_input.value = "1"
        status_text.value = ""
        page.update()
    
    # Header
    header = ft.Row([
        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE, size=30),
        ft.Text("Patient Data Viewer", size=24, weight=ft.FontWeight.BOLD)
    ], alignment=ft.MainAxisAlignment.CENTER)
    
    # Input Section
    input_section = ft.Row([
        patient_id_input,
        ft.ElevatedButton(
            "Fetch Data",
            on_click=fetch_data,
            icon=ft.Icons.SEARCH
        ),
        ft.OutlinedButton(
            "Clear",
            on_click=clear_data,
            icon=ft.Icons.CLEAR
        ),
        loading
    ], 
    alignment=ft.MainAxisAlignment.CENTER,
    spacing=20)
    
    # Main layout
    page.add(
        ft.Column([
            header,
            ft.Divider(),
            input_section,
            status_text,
            ft.Divider(),
            data_container
        ], 
        scroll=ft.ScrollMode.AUTO,
        expand=True)
    )

if __name__ == "__main__":
    print("=" * 50)
    print("Patient Data Viewer Application - Simplified Version")
    print("=" * 50)
    print("\nTo change the server URL:")
    print('export API_URL="https://yourserver:port/ords/path"')
    print("\nStarting application...")
    
    ft.app(target=main, view=ft.WEB_BROWSER)