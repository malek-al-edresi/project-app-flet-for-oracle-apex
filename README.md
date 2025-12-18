# Patient Profile Viewer - Flet App for Oracle APEX

A desktop application built with Python and Flet to fetch and display patient data from an Oracle APEX ORDS API endpoint.

## Features

- **Clean UI**: Modern card-based interface with organized patient information
- **Real-time Data Fetching**: Retrieve patient data from ORDS API by ID
- **Error Handling**: Comprehensive error messages for connection issues
- **Responsive Design**: Adjusts to different screen sizes
- **Patient Categories**: Data organized into personal, contact, medical, and emergency sections

## Prerequisites

- Ubuntu 22.04 or higher (with Python 3.12+)
- Oracle APEX ORDS server running on `https://localhost:8443`
- Python 3.12 or higher

## Installation

### 1. Clone or Download the Project
```bash
git clone <your-repository-url>
cd project-app-flet-for-oracle-apex
```

### 2. Set Up Virtual Environment
Ubuntu 23.10+ requires virtual environments for Python packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install flet requests
```

### 3. Run the Application
```bash
python3 main.py
```

## Project Structure

```
project-app-flet-for-oracle-apex/
├── main.py              # Main application file
├── README.md           # This documentation
└── venv/               # Virtual environment (created during setup)
```

## API Configuration

The app connects to the following ORDS API endpoint:
```
https://localhost:8443/ords/medical_sys_api/basic_sec_api/basic_sec_view_r_profile_patient/{patient_id}
```

### Expected API Response Format
```json
{
  "items": [
    {
      "address": "string",
      "age": 0,
      "allergies": "string",
      "bloodtype": "string",
      "chronicdiseases": "string",
      "count_invoiceid": 0,
      "currentmedications": "string",
      "dateofbirth": "string",
      "email": "string",
      "emergencycontactname": "string",
      "emergencycontactphone": "string",
      "full_name": "string",
      "gender": "string",
      "maritalstatus": "string",
      "medicalhistory": "string",
      "patientid": "string",
      "personalhobbytypeid": "string",
      "personalnumberid": "string",
      "phone_primary": "string",
      "photo_patient": "string",
      "previoussurgeries": "string"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'flet'"**
   - Solution: Make sure you're in the virtual environment (`source venv/bin/activate`) and packages are installed

2. **"externally-managed-environment" Error**
   - Solution: Always use a virtual environment on Ubuntu 23.10+

3. **Connection Errors**
   - Verify ORDS server is running on `https://localhost:8443`
   - Check if the API endpoint is accessible in your browser
   - Disable SSL verification (already handled in code for development)

4. **JSON Decode Errors**
   - Verify the API is returning valid JSON
   - Check API endpoint format

### Development Notes

- **SSL Verification**: Disabled for localhost development (self-signed certificates)
- **Virtual Environment**: Required due to Ubuntu's Python package management restrictions
- **Dependencies**: Flet (UI framework) and Requests (HTTP client)

## Usage Guide

1. **Start the Application**: Run `python3 main.py` in the virtual environment
2. **Enter Patient ID**: Default is "1", enter any valid patient ID
3. **Fetch Data**: Click "Fetch Patient Data" button
4. **View Results**: Patient information displayed in categorized cards
5. **Clear Display**: Use "Clear" button to reset the interface

## Screenshot

```
┌─────────────────────────────────────────────────────┐
│              Patient Profile Viewer                 │
│              Medical System API Client              │
├─────────────────────────────────────────────────────┤
│ [Enter Patient ID] [1]                              │
│ [Fetch Patient Data]       [Clear]                  │
├─────────────────────────────────────────────────────┤
│ Personal Information                                 │
│ • Full Name: John Doe                               │
│ • Patient ID: P12345                                │
│ • Date of Birth: 1985-03-15                         │
│ • Age: 39                                           │
│ • Gender: Male                                      │
│ • Marital Status: Married                           │
├─────────────────────────────────────────────────────┤
│ Contact Information                                 │
│ • Email: john.doe@email.com                         │
│ • Phone: +1234567890                                │
│ • Address: 123 Main St, City, Country               │
│ • Personal Number ID: ID789012                      │
└─────────────────────────────────────────────────────┘
```

## Technical Details

- **Framework**: Flet (Python UI framework)
- **HTTP Client**: Requests library
- **Python Version**: 3.12+
- **Platform**: Cross-platform (Windows, macOS, Linux)

## License

This project is for educational/demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify ORDS server is running
3. Ensure you're using the virtual environment
4. Test the API endpoint directly in a browser

---
