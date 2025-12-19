## Brief Overview: Oracle APEX Integration

This Flet application provides a seamless interface for viewing patient data from Oracle APEX via ORDS REST APIs. It connects directly to your APEX RESTful Services endpoints and displays the data in an organized, user-friendly format.

## Screenshot

![Patient Data Viewer Application](./screenshot/return_Data.png)

### Key Integration Features:
- **Direct ORDS API Connection**: Connects to `ords/medical_sys_api/basic_sec_api/` endpoints
- **Flexible Response Handling**: Supports multiple JSON response formats from APEX
- **Environment-Based Configuration**: Easy API URL configuration via environment variables
- **SSL Support**: Handles self-signed certificates for development environments

### Integration Points:
1. **APEX REST Module**: Uses `basic_sec_api` module
2. **Resource Template**: Accesses `basic_sec_view_r_profile_patient/{patient_id}`
3. **Data Mapping**: Translates APEX table/view data to categorized UI cards
4. **Real-time Fetching**: Live data retrieval on patient ID input

### Quick Setup:
```bash
# Set your APEX ORDS endpoint
export API_URL="https://your-apex-server:port/ords/workspace"

# Run the application
python main.py
```