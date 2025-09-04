# 📇 Contact Manager Pro

A professional, secure, and user-friendly contact management application built with Python and Streamlit. This application allows users to manage their personal and professional contacts with ease, featuring a clean interface, robust validation, and secure user authentication.

---

## 🌟 Features

### 🔐 User Authentication
- Secure user registration and login system
- Account lockout after multiple failed attempts
- Session management for persistent login

### 📋 Contact Management
- **Add Contacts**: Store names, phone numbers, and email addresses
- **Edit Contacts**: Update existing contact information
- **Delete Contacts**: Remove contacts with confirmation
- **View Contacts**: Display all contacts in a sortable, paginated table
- **Search Contacts**: Find contacts by name, phone, or email

### 📊 Data Handling
- Input validation for names, phones, and emails
- Duplicate prevention for phone numbers and emails
- Export contacts to CSV or JSON format
- Responsive design with pagination for large contact lists

### 🎨 User Experience
- Clean, modern UI with custom CSS styling
- Interactive guidelines and help section
- Real-time feedback and error messages
- Quick stats and overview in sidebar

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.x
- **Database**: MySQL
- **Authentication**: Custom session-based authentication
- **Data Validation**: Regular expressions
- **Data Export**: Pandas for CSV, JSON module for JSON

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- MySQL Server
- pip (Python package manager)

### Steps

1. **Clone the repository** (if applicable):
   ```bash
   git clone <your-repository-url>
   cd contact-manager-pro
   ```

2. **Install required packages**:
   ```bash
   pip install streamlit mysql-connector-python pandas
   ```

3. **Set up MySQL database**:
   - Ensure MySQL server is running
   - Update database connection details in `database.py`:
     ```python
     # For local development
     host = "localhost"
     user = "root"  # Your MySQL username
     password = "system"  # Your MySQL password
     database = "vishal"  # Your database name
     ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the application**:
   - Open your web browser and go to `http://localhost:8501`

---

## 🚀 Usage

### Registration
1. Click on "Register New Account" in the login page
2. Choose a username (min. 3 characters) and password (min. 6 characters)
3. Login with your new credentials

### Managing Contacts
1. **Add Contact**: Navigate to "Add Contact", fill in the required fields (name and phone), and save
2. **View Contacts**: See all your contacts in a sortable table with pagination
3. **Edit Contact**: Select a contact to modify and update its information
4. **Search Contacts**: Use the search functionality to find specific contacts
5. **Delete Contact**: Select a contact and confirm deletion

### Data Export
- Use the export buttons in the "View Contacts" section to download your contacts as CSV or JSON files

---

## 🗂️ Project Structure

```
contact-manager-pro/
│
├── app.py                 # Main Streamlit application
├── database.py           # Database connection and setup
├── operations.py         # Core contact operations and authentication
├── README.md            # Project documentation (this file)
└── requirements.txt     # Python dependencies (to be created)
```

### Key Components

1. **app.py**: Main application file containing:
   - Streamlit UI configuration
   - Input validation functions
   - Login system
   - Contact management interface
   - Cache management

2. **database.py**: Handles:
   - MySQL database connection
   - Database and table creation
   - Connection management

3. **operations.py**: Contains:
   - User authentication (register/login)
   - CRUD operations for contacts
   - Search functionality
   - Duplicate checking

---

## 🔒 Security Features

- Password protection with attempt limiting
- Account lockout after 3 failed login attempts (1-minute lock)
- Input validation to prevent SQL injection and data corruption
- Session management for authenticated users
- Separate database tables for each user

---

## 📋 Validation Rules

### Username
- Minimum 3 characters
- Only letters, numbers, and underscores

### Password
- Minimum 6 characters

### Name
- 2-50 characters
- Only letters, spaces, apostrophes, and hyphens
- No consecutive special characters
- Cannot start or end with special characters

### Phone Number
- 10 digits (Indian format)
- Must start with 6-9
- Country code support (+91 or 91 prefix)

### Email
- Optional field
- Valid email format if provided
- Stored as NULL if empty

---

## 🎨 UI/UX Features

- Responsive design with custom CSS styling
- Professional color scheme and layout
- Intuitive navigation with sidebar menu
- Interactive forms with real-time validation
- Success/error messages with appropriate styling
- Pagination for large contact lists
- Export functionality with timestamped filenames

---

## 🔧 Customization

### Database Configuration
Modify the `database.py` file to change database connection settings:

```python
# For local development
host = "localhost"
user = "your_username"
password = "your_password"
database = "your_database_name"
```

### Styling
Customize the appearance by modifying the CSS in the `st.markdown()` section of `app.py`:

```python
st.markdown("""
    <style>
        /* Add your custom CSS here */
        .main {
            background-color: your_color;
        }
    </style>
""", unsafe_allow_html=True)
```

### Validation Rules
Adjust validation criteria by modifying the validation functions in `app.py`:
- `validate_username()`
- `validate_password()`
- `validate_name()`
- `validate_phone()`
- `validate_email()`

---

## 📝 Future Enhancements

Potential improvements for future versions:
- Contact categories/groups
- Profile pictures for contacts
- Birthday reminders
- Bulk import/export operations
- Cloud synchronization
- Advanced search filters
- Dark mode toggle
- Mobile app version

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

If you encounter any issues or have questions:
1. Check the guidelines section in the application
2. Ensure your database connection is properly configured
3. Verify all input validation requirements are met

For additional support, please contact the development team.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Database management with [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- Data manipulation with [Pandas](https://pandas.pydata.org/)

---

**Contact Manager Pro** - Organize your contacts with professionalism and ease! 📇✨
