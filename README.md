# Hospital Management System

A comprehensive Hospital Management System built with Python that provides a complete solution for managing hospital operations including patient records, staff management, appointment scheduling, billing, and reporting.

## 🏥 Features

### Patient Management
- Add, update, delete, and view patient records
- Search patients by name or contact information
- Track medical history and patient demographics
- Patient activity tracking

### Staff Management
- Manage doctors, nurses, and administrative staff
- Role-based staff organization
- Specialization tracking for medical staff
- Staff performance metrics

### Appointment Management
- Schedule appointments with conflict detection
- Update and cancel appointments
- View daily and filtered appointments
- Doctor availability management
- 30-minute buffer between appointments

### Billing Management
- Generate bills with predefined service pricing
- Record payments and track outstanding dues
- Multiple payment statuses (paid, unpaid, partial)
- Patient billing history
- Revenue tracking

### Reporting System
- Daily activity reports
- Monthly performance reports
- Patient summary and demographics
- Financial reports with date ranges
- Custom report generation

### System Features
- JSON-based data persistence
- Comprehensive error handling and logging
- Data integrity validation
- Modern CLI interface with table formatting
- Input validation and sanitization

## 📁 Project Structure

```
hospital-management-system/
│
├── README.md                    # Project documentation
├── config.py                    # Configuration and constants
├── models.py                    # Data model definitions
├── database.py                  # JSON file operations
├── utils.py                     # Utility functions and helpers
├── patient_management.py        # Patient CRUD operations
├── staff_management.py          # Staff CRUD operations
├── appointment_management.py     # Appointment scheduling
├── billing_management.py        # Billing and payments
├── reports.py                   # Report generation
├── main.py                      # Main application entry point
│
├── data/                        # Data storage directory
│   ├── patients.json           # Patient records
│   ├── staff.json              # Staff records
│   ├── appointments.json       # Appointment records
│   └── billing.json            # Billing records
│
└── logs/                        # Application logs
    └── hospital.log            # System log file
```

## 🚀 Installation and Setup

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

### Installation Steps

1. **Clone or download the project files**
   ```bash
   # If using git
   git clone <repository-url>
   cd hospital-management-system
   
   # Or download and extract the files to a directory
   ```

2. **Verify Python installation**
   ```bash
   python --version
   # or
   python3 --version
   ```

3. **Run the application**
   ```bash
   python main.py
   # or
   python3 main.py
   ```

## 💻 Usage

### Starting the Application

```bash
python main.py
```

### Demo Mode
To run with sample data for testing:
```bash
python main.py --demo
```

### Main Menu Navigation

The application provides an intuitive menu-driven interface:

1. **Patient Management** - Manage patient records
2. **Staff Management** - Manage hospital staff
3. **Appointment Management** - Schedule and manage appointments
4. **Billing Management** - Handle billing and payments
5. **Reports** - Generate various reports
6. **System Information** - View system statistics
7. **Exit** - Safely exit the application

### Key Operations

#### Adding a Patient
1. Select "Patient Management" from main menu
2. Choose "Add New Patient"
3. Enter patient details (name, age, gender, contact, medical history)
4. System generates unique patient ID

#### Scheduling an Appointment
1. Select "Appointment Management"
2. Choose "Schedule New Appointment"
3. Select patient and doctor from available lists
4. Enter date and time (system checks for conflicts)
5. Add optional notes

#### Generating a Bill
1. Select "Billing Management"
2. Choose "Generate New Bill"
3. Select patient
4. Add services from predefined list or custom services
5. System calculates total amount

#### Generating Reports
1. Select "Reports" from main menu
2. Choose report type (Daily, Monthly, Financial, etc.)
3. Enter date ranges or filters as needed
4. View formatted report output

## 🔧 Configuration

### Service Pricing
Edit the `SERVICE_PRICES` dictionary in `billing_management.py` to customize service costs:

```python
SERVICE_PRICES = {
    'consultation': 100.0,
    'blood_test': 50.0,
    'x_ray': 150.0,
    # Add more services as needed
}
```

### File Paths
Modify paths in `config.py` if needed:

```python
DATABASE_PATH = "data/"
LOG_PATH = "logs/"
```

## 📊 Data Management

### Data Storage
- All data is stored in JSON format for easy backup and portability
- Automatic backup creation before data modifications
- Data integrity validation on startup

### Data Files
- `patients.json` - Patient records with medical history
- `staff.json` - Staff information and roles
- `appointments.json` - Appointment scheduling data
- `billing.json` - Billing and payment records

### Backup and Recovery
- Automatic `.backup` files created before modifications
- Manual backup: Copy the entire `data/` directory
- Recovery: Replace corrupted files with `.backup` versions

## 🛡️ Security Features

- Input validation and sanitization
- Phone number format validation
- Date and time format validation
- Confirmation prompts for destructive operations
- Comprehensive error logging

## 📈 Reporting Capabilities

### Available Reports
1. **Daily Report** - Daily activities and statistics
2. **Monthly Report** - Monthly performance metrics
3. **Patient Summary** - Demographics and patient statistics
4. **Financial Report** - Revenue and payment analysis
5. **Custom Reports** - User-defined criteria

### Report Features
- Tabular data presentation
- Date range filtering
- Status-based filtering
- Revenue calculations
- Performance metrics

## 🔍 Troubleshooting

### Common Issues

**Application won't start:**
- Check Python version (3.7+ required)
- Ensure all files are in the same directory
- Check file permissions

**Data not saving:**
- Verify write permissions in application directory
- Check available disk space
- Review error logs in `logs/hospital.log`

**Import errors:**
- Ensure all Python files are in the same directory
- Check for typos in file names
- Verify Python path configuration

### Error Logging
- All errors are logged to `logs/hospital.log`
- Check this file for detailed error information
- Log entries include timestamps and error context

## 🔄 System Requirements

### Minimum Requirements
- Python 3.7+
- 50MB free disk space
- Terminal/Command prompt access

### Recommended Requirements
- Python 3.8+
- 100MB free disk space
- Modern terminal with Unicode support

## 🚀 Future Enhancements

### Planned Features
- Database integration (SQLite/PostgreSQL)
- Web-based interface
- Multi-user support with authentication
- Advanced reporting with charts
- Email notifications
- Backup automation
- Data export/import functionality

### Extensibility
The modular design allows easy addition of new features:
- Add new management modules
- Extend reporting capabilities
- Integrate with external systems
- Add new data validation rules

## 📝 Development

### Code Structure
- **Modular Design** - Each functionality in separate files
- **Error Handling** - Comprehensive try-catch blocks
- **Logging** - Detailed logging for debugging
- **Validation** - Input validation throughout
- **Documentation** - Inline comments and docstrings

### Adding New Features
1. Create new module file (e.g., `inventory_management.py`)
2. Add menu option in `main.py`
3. Update imports and navigation
4. Add corresponding data file in `config.py`
5. Test thoroughly

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review error logs
3. Verify system requirements
4. Test with demo mode

## 📄 License

This project is open source and available under standard terms.

## 🙏 Acknowledgments

Built with Python standard library for maximum compatibility and minimal dependencies.

---

**Hospital Management System v1.0.0**  
*A comprehensive solution for modern healthcare management*
