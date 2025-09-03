import streamlit as st
from datetime import datetime,timedelta
import json
import os
import time as t1
import re
import pandas as pd
from operations import ContactOperations

# Page config with improved theme
st.set_page_config(
    page_title="Professional Contact Manager",
    page_icon="📇",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'account_locked' not in st.session_state:
    st.session_state.account_locked = False
if 'lock_time' not in st.session_state:
    st.session_state.lock_time = None

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .sidebar .sidebar-content {
            background-color: #343a40;
            color: white;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        .stSelectbox>div>div>select {
            border-radius: 8px;
        }
        .header {
            color: #4a4a4a;
        }
        .success-message {
            color: #28a745;
            font-weight: 500;
        }
        .error-message {
            color: #dc3545;
            font-weight: 500;
        }
        .guideline-box {
            background-color:#121212;
            border-left: 4px solid #007bff;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        .pagination-info {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize database operations
if 'db_ops' not in st.session_state:
    st.session_state.db_ops = ContactOperations()

# Validation functions
def validate_username(username):
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

def validate_name(name):
    pattern = re.compile(r"^[A-Za-z\s\'-]{2,50}$")
    
    if not bool(pattern.match(name)):
        return False, "Name can only contain letters,spaces."
    
    # Check for consecutive special characters
    if re.search(r"[\s\'-]{2,}", name):
        return False, "Name cannot have consecutive spaces, apostrophes or hyphens"
    
    # Check if name starts or ends with special character
    if name.startswith(("'", "-", " ")) or name.endswith(("'", "-", " ")):
        return False, "Name cannot start or end with a space, apostrophe or hyphen"
    
    # Check minimum length after trimming (at least 2 letters)
    letters_only = re.sub(r"[^A-Za-z]", "", name)
    if len(letters_only) < 2:
        return False, "Name must contain at least 2 letters"
    
    return True, ""

def validate_phone(phone):
    # Remove any spaces, dashes, or parentheses that users might enter
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it starts with a country code like +91 and remove it
    if cleaned_phone.startswith('+91') and len(cleaned_phone) > 3:
        cleaned_phone = cleaned_phone[3:]  # Remove the +91 prefix
    
    # Check if it starts with 91 (without +) and remove it
    if cleaned_phone.startswith('91') and len(cleaned_phone) > 2:
        cleaned_phone = cleaned_phone[2:]  # Remove the 91 prefix
    
    # Validate that it's exactly 10 digits
    pattern = re.compile(r"^[6-9][0-9]{9}$")  # Indian mobile numbers start with 6-9
    
    if not cleaned_phone:
        return False, "Phone number cannot be empty"
    
    if not bool(pattern.match(cleaned_phone)):
        return False, "Please enter a valid 10-digit phone number (should start with 6-9)"
    
    return True, ""

def validate_email(email):
    # Check if email is empty, None, or just whitespace
    if not email or not email.strip():
        return True, "NULL"  # Indicates empty email should be stored as NULL
    
    # Clean the email by stripping whitespace
    cleaned_email = email.strip()
    
    # Validate email pattern if provided
    pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not bool(pattern.match(cleaned_email)):
        return False, "Please enter a valid email address"
    
    return True, "VALID"  # Indicates valid email provided

# Cache management functions
def initialize_contacts():
    """Initialize contacts in session state if not already present"""
    if 'contacts' not in st.session_state:
        st.session_state.contacts = []
    if 'contacts_loaded' not in st.session_state:
        st.session_state.contacts_loaded = False

def refresh_contacts():
    """Force refresh contacts from database"""
    st.session_state.contacts = st.session_state.db_ops.get_contacts(st.session_state.current_user)
    st.session_state.contacts_loaded = True

def get_contacts_cached():
    """Get contacts from cache or database if not loaded"""
    initialize_contacts()
    
    if not st.session_state.contacts_loaded or not st.session_state.contacts:
        refresh_contacts()
    
    return st.session_state.contacts

def invalidate_contacts_cache():
    """Mark contacts cache as invalid (to be refreshed on next access)"""
    st.session_state.contacts_loaded = False

# Export functions
def export_contacts_csv():
    contacts = get_contacts_cached()
    if contacts:
        df = pd.DataFrame(contacts)
        # Convert datetime objects to strings for CSV export
        if 'date_added' in df.columns:
            df['date_added'] = df['date_added'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if x else '')
        csv = df.to_csv(index=False)
        return csv
    return None

def export_contacts_json():
    contacts = get_contacts_cached()
    if contacts:
        # Convert datetime objects to strings for JSON serialization
        export_data = []
        for contact in contacts:
            contact_copy = contact.copy()
            if contact_copy.get('date_added'):
                contact_copy['date_added'] = contact_copy['date_added'].strftime('%Y-%m-%d %H:%M:%S')
            export_data.append(contact_copy)
        return json.dumps(export_data, indent=2)
    return None

# Login system
def login_page():
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 40px auto 0 auto;
            background: #fff;
            padding: 2.5rem 2rem 2rem 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.10);
        }
        .timer-warning {
            background-color: #fff3cd;
            color: #856404;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ffeaa7;
            margin-bottom: 20px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Check if account is locked and show timer if needed
    if st.session_state.account_locked:
        remaining_time = st.session_state.lock_time - datetime.now()
        if remaining_time.total_seconds() > 0:
            minutes, seconds = divmod(int(remaining_time.total_seconds()), 60)
            
            # Display lock message and timer
            st.markdown(f"""
                <div class="timer-warning">
                    <h4>🔒 Account Locked</h4>
                    <p>Too many failed attempts. Please try again After:</p>
                    <h3>{minutes:02d}:{seconds:02d}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Update the timer every second
            t1.sleep(1)
            st.rerun()
        else:
            # Lock period has ended
            st.session_state.account_locked = False
            st.session_state.login_attempts = 0
            st.session_state.lock_time = None
            st.rerun()
    
    # Start container
    container = st.container()
    with container:
        st.title("🔐 Contact Manager Pro - Login")
        st.markdown("---")
        
        # Show remaining attempts warning if any failed attempts
        if st.session_state.login_attempts > 0:
            remaining_attempts = 2 - st.session_state.login_attempts
            st.warning(f"⚠️ Access denied.. {remaining_attempts} attempt remaining, your account will be automatically locked for security protection.")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("Login"):
                if not username and not password:
                    st.error("Please enter both username and password")
                elif not username:
                    st.error("Please enter your username")
                elif not password:
                    st.error("Please enter your password")
                elif st.session_state.db_ops.authenticate_user(username, password):
                    # Successful login - reset attempt counter
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.login_attempts = 0
                    invalidate_contacts_cache()  # Reset cache for new user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    # Failed login - increment attempt counter
                    st.session_state.login_attempts += 1
                    
                    # Check if account should be locked
                    if st.session_state.login_attempts >= 3:
                        st.session_state.account_locked = True
                        st.session_state.lock_time = datetime.now() + timedelta(minutes=1)  # Lock for 2 minutes
                        st.error("Too many failed attempts! Account locked for 1 minutes.")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        st.markdown("---")
        st.markdown("Don't have an account? Register below:")
        
        if st.session_state.get("registration_success"):
            st.success("Registration successful! Please login.")
            st.session_state.registration_success = False
        
        with st.expander("Register New Account"):
            with st.form("register_form"):
                new_username = st.text_input("New Username", placeholder="Choose a username (min. 3 chars)")
                new_password = st.text_input("New Password", type="password", placeholder="Choose a password (min. 6 chars)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                
                if st.form_submit_button("Register"):
                    # Validate inputs
                    username_valid, username_msg = validate_username(new_username)
                    password_valid, password_msg = validate_password(new_password)
                    
                    if not username_valid:
                        st.error(username_msg)
                    elif not password_valid:
                        st.error(password_msg)
                    elif new_password != confirm_password:
                        st.error("Passwords don't match")
                    else:
                        success, message = st.session_state.db_ops.register_user(new_username, new_password)
                        if success:
                            st.session_state.registration_success = True
                            st.rerun()
                        else:
                            st.error(message)
    
    # Apply the container styling
    st.markdown(
        f"""
        <script>
            var container = window.parent.document.querySelector('.stContainer');
            container.classList.add('login-container');
        </script>
        """,
        unsafe_allow_html=True
    )

# Display contacts in table view with sorting and pagination
def display_contacts_table():
    contacts = get_contacts_cached()
    
    if contacts:
        # Sorting options
        sort_option = st.selectbox(
            "Sort by", 
            ["Name (A-Z)", "Name (Z-A)", "Date Added (Newest)", "Date Added (Oldest)"],
            key="sort_option"
        )
        
        # Apply sorting
        if sort_option == "Name (A-Z)":
            sorted_contacts = sorted(contacts, key=lambda x: x["name"].lower())
        elif sort_option == "Name (Z-A)":
            sorted_contacts = sorted(contacts, key=lambda x: x["name"].lower(), reverse=True)
        elif sort_option == "Date Added (Newest)":
            sorted_contacts = sorted(contacts, key=lambda x: x["date_added"], reverse=True)
        elif sort_option == "Date Added (Oldest)":
            sorted_contacts = sorted(contacts, key=lambda x: x["date_added"])
        else:
            sorted_contacts = contacts
        
        # Pagination
        items_per_page = 10
        total_pages = max(1, (len(sorted_contacts) + items_per_page - 1) // items_per_page)
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, key="page_input")
        
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(sorted_contacts))
        
        # Display pagination info
        st.markdown(f'<div class="pagination-info">Showing {start_idx + 1}-{end_idx} of {len(sorted_contacts)} contacts</div>', unsafe_allow_html=True)
        
        # Convert to list of dictionaries for display
        display_data = []
        for contact in sorted_contacts[start_idx:end_idx]:
            display_data.append({
                "id": contact["id"],
                "name": contact["name"],
                "phone": contact["phone"],
                "email": contact["email"],
                "date_added": contact["date_added"].strftime("%Y-%m-%d %H:%M") if contact["date_added"] else ""
            })
        
        st.dataframe(
            display_data,
            column_config={
                "id": {"label": "ID", "width": "small"},
                "name": {"label": "Name", "width": "medium"},
                "phone": {"label": "Phone", "width": "medium"},
                "email": {"label": "Email", "width": "large"},
                "date_added": {"label": "Date Added", "width": "medium"}
            },
            use_container_width=True,
            hide_index=True,
            height=min(40 * len(display_data) + 40, 500)
        )
        
        # Export buttons
        col1, col2 = st.columns(2)
        with col1:
            csv_data = export_contacts_csv()
            if csv_data:
                st.download_button(
                    label="Export as CSV",
                    data=csv_data,
                    file_name=f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col2:
            json_data = export_contacts_json()
            if json_data:
                st.download_button(
                    label="Export as JSON",
                    data=json_data,
                    file_name=f"contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.warning("No contacts found. Add your first contact!")

# Guidelines page
def show_guidelines():
    st.subheader("📖 How to Use Contact Manager Pro")
    
    st.markdown("""
    <div class="guideline-box">
    <h4>Getting Started</h4>
    <p>Welcome to Contact Manager Pro! This application helps you manage your contacts efficiently.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Contacts", expanded=True):
        st.markdown("""
        - Navigate to the **View Contacts** section to see all your saved contacts
        - Use the sorting dropdown to organize contacts by name or date
        - Use pagination to navigate through large contact lists
        - Export your contacts as CSV or JSON for backup
        """)
    
    with st.expander("Add New Contacts"):
        st.markdown("""
        - Go to the **Add Contact** section to create new entries
        - Name and Phone fields are required
        - Email is optional but recommended for complete contact information
        - Phone numbers are validated for correct format
        - Click "Save Contact" to add to your database
        """)
    
    with st.expander("Edit Existing Contacts"):
        st.markdown("""
        - Select **Edit Contact** from the sidebar
        - Choose the contact you want to modify from the dropdown
        - Update any of the fields as needed
        - Click "Update Contact" to save your changes
        """)
    
    with st.expander("Search Functionality"):
        st.markdown("""
        - Use the **Search Contacts** feature to find specific contacts
        - Search by name, phone number, or email address
        - Results will appear instantly as you type
        """)
    
    with st.expander("Delete Contacts"):
        st.markdown("""
        - Select **Delete Contact** from the sidebar
        - Choose the contact you want to remove
        - Confirm deletion - this action cannot be undone
        - The contact will be permanently removed from your database
        """)
    
    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.info("""
    - Your data is automatically saved and synchronized across sessions
    - Use descriptive names to make contacts easier to find later
    - Regularly update contact information to keep your database current
    - Export your contacts regularly for backup purposes
    - Use categories to organize your contacts (coming in future versions)
    """)

# Main app function
def contact_manager():
    # Sidebar with user info and actions
    with st.sidebar:
        st.title(f"👋 Welcome, {st.session_state.current_user}")
        st.markdown("---")
        # Action selector
        action = st.radio(
            "Actions",
            ["View Contacts", "Add Contact", "Edit Contact", "Search Contacts", "Delete Contact"],
            index=0
        )
        st.markdown("---")
        # Quick stats
        st.markdown("### Quick Stats")
        contacts = get_contacts_cached()
        st.markdown(f"📇 **Total Contacts:** {len(contacts)}")
        if contacts:
            last_added = max(contacts, key=lambda x: x['date_added'])
            st.markdown(f"🕒 **Last Added:** {last_added['name']}")
        st.markdown("---")
        
        # Guidelines button
        if st.button("📖 Guidelines", use_container_width=True):
            st.session_state.show_guidelines = True
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.contacts = []
            st.session_state.contacts_loaded = False
            st.session_state.show_guidelines = False
            st.rerun()

    # Main content area
    st.title("📇 Contact Manager Pro")
    st.markdown("---")

    # Check if we should show guidelines
    if st.session_state.get('show_guidelines', False):
        show_guidelines()
        if st.button("Back to Main"):
            st.session_state.show_guidelines = False
            st.rerun()
        return

    # View Contacts
    if action == "View Contacts":
        st.subheader("All Contacts")
        display_contacts_table()

    # Delete Contact
    elif action == "Delete Contact":
        contacts = get_contacts_cached()
        if contacts:
            st.subheader("Delete a Contact")
            contact_options = {f"{c['name']} ({c['phone']})": c['id'] for c in contacts}
            selected = st.selectbox("Select contact to delete", list(contact_options.keys()))
            
            # Add confirmation for deletion
            if st.checkbox("Confirm deletion", key="delete_confirm"):
                if st.button("Delete Contact", key="delete_contact_btn"):
                    contact_id = contact_options[selected]
                    success, message = st.session_state.db_ops.delete_contact(st.session_state.current_user, contact_id)
                    if success:
                        st.success(message)
                        invalidate_contacts_cache()  # Mark cache as invalid
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Please check the confirmation box to delete the contact")
        else:
            st.warning("No contacts to delete.")

    # Add Contact
    elif action == "Add Contact":
            st.subheader("Add New Contact")
    
            # Initialize form data in session state if not exists
            if 'add_form_data' not in st.session_state:
                st.session_state.add_form_data = {'name': '', 'phone': '', 'email': ''}
    
            with st.form("add_form"):
                cols = st.columns(2)
                with cols[0]:
                    name = st.text_input("Name*", placeholder="Enter The Name", 
                                value=st.session_state.add_form_data['name'])
                with cols[1]:
                    phone = st.text_input("Phone*", placeholder="Enter The Phone No", 
                                 value=st.session_state.add_form_data['phone'])
                email = st.text_input("Email", placeholder="Enter The Email", 
                             value=st.session_state.add_form_data['email'])
        
                submitted = st.form_submit_button("💾 Save Contact", use_container_width=True)
        
                if submitted:
            # Store form data in session state to preserve values if validation fails
                    st.session_state.add_form_data = {'name': name, 'phone': phone, 'email': email}
            
                # Validate inputs
                    name_valid, name_msg = validate_name(name)
                    phone_valid, phone_msg = validate_phone(phone)
                    email_valid, email_msg = validate_email(email)
            
                    validation_passed = True
            
                    if not name:
                        st.error("Name is required!")
                        validation_passed = False
                
                    if not phone:
                        st.error("Phone is required!")
                        validation_passed = False

                    elif not name_valid:
                        st.error(name_msg)
                        validation_passed = False

                    elif not phone_valid:
                        st.error(phone_msg)
                        validation_passed = False
                
                    if email and not email_valid:
                        st.error(email_msg)
                        validation_passed = False
            
                    # Only proceed if all validations pass
                    if validation_passed:
                        try:
                            success, message = st.session_state.db_ops.add_contact(
                                st.session_state.current_user, name, phone, email
                                 )
                            if success:
                                st.success(message)
                                invalidate_contacts_cache()  # Mark cache as invalid
                                # Clear form data after successful submission
                                st.session_state.add_form_data = {'name': '', 'phone': '', 'email': ''}
                                # Rerun to refresh the form with empty values
                                st.rerun()
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {str(e)}")

    # Edit Contact
    elif action == "Edit Contact":
        contacts = get_contacts_cached()
        if contacts:
            st.subheader("Edit Contact")
            contact_options = {f"{c['name']} ({c['phone']})": c for c in contacts}
            selected = st.selectbox("Select contact to edit", list(contact_options.keys()))
        
            contact = contact_options[selected]
        
            # Initialize edit form data in session state if not exists or if contact changed
            if ('edit_form_data' not in st.session_state or 
                st.session_state.get('last_edited_contact') != contact["id"]):
                st.session_state.edit_form_data = {
                    'name': contact["name"],
                    'phone': contact["phone"],
                    'email': contact["email"] if contact["email"] else ""
                }
                st.session_state.last_edited_contact = contact["id"]
        
            with st.form("edit_form"):
                cols = st.columns(2)
                with cols[0]:
                    new_name = st.text_input("Name*", value=st.session_state.edit_form_data['name'])
                with cols[1]:
                    new_phone = st.text_input("Phone*", value=st.session_state.edit_form_data['phone'])
                new_email = st.text_input("Email", value=st.session_state.edit_form_data['email'])
            
                submitted = st.form_submit_button("🔄 Update Contact", use_container_width=True)
            
            if submitted:
                # Store form data in session state to preserve values if validation fails
                st.session_state.edit_form_data = {
                    'name': new_name,
                    'phone': new_phone,
                    'email': new_email
                }
                
                # Validate inputs
                phone_valid, phone_msg = validate_phone(new_phone)
                email_valid, email_msg = validate_email(new_email)
                
                validation_passed = True
                
                if not new_name:
                    st.error("Name is required!")
                    validation_passed = False
                    
                if not new_phone:
                    st.error("Phone is required!")
                    validation_passed = False
                elif not phone_valid:
                    st.error(phone_msg)
                    validation_passed = False
                    
                if new_email and not email_valid:
                    st.error(email_msg)
                    validation_passed = False
                
                # Only proceed if all validations pass
                if validation_passed:
                    try:
                        success, message = st.session_state.db_ops.update_contact(
                            st.session_state.current_user, contact["id"], new_name, new_phone, new_email
                        )
                        if success:
                            st.success(message)
                            invalidate_contacts_cache()  # Mark cache as invalid
                            # Clear the edit form data to force refresh on next edit
                            if 'edit_form_data' in st.session_state:
                                del st.session_state.edit_form_data
                            if 'last_edited_contact' in st.session_state:
                                del st.session_state.last_edited_contact
                            st.rerun()
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
        else:
            st.warning("No contacts available to edit")

    # Search Contacts
    elif action == "Search Contacts":
        st.subheader("Search Contacts")
        search_by = st.radio("Search by", ["All fields", "Name only", "Phone only", "Email only"], horizontal=True)
        search_term = st.text_input("Enter search term", "")
        
        if search_term:
            # Always search directly in database for accurate results
            results = st.session_state.db_ops.search_contacts(st.session_state.current_user, search_term)
            
            # Filter results based on search_by selection
            if search_by == "Name only":
                results = [r for r in results if search_term.lower() in r["name"].lower()]
            elif search_by == "Phone only":
                results = [r for r in results if search_term in r["phone"]]
            elif search_by == "Email only":
                results = [r for r in results if r["email"] and search_term.lower() in r["email"].lower()]
            
            if results:
                st.success(f"Found {len(results)} matching contacts")
                # Convert to list of dictionaries for display
                display_data = []
                for contact in results:
                    display_data.append({
                        "id": contact["id"],
                        "name": contact["name"],
                        "phone": contact["phone"],
                        "email": contact["email"],
                        "date_added": contact["date_added"].strftime("%Y-%m-%d %H:%M") if contact["date_added"] else ""
                    })
                
                st.dataframe(
                    display_data,
                    column_config={
                        "id": {"label": "ID", "width": "small"},
                        "name": {"label": "Name", "width": "medium"},
                        "phone": {"label": "Phone", "width": "medium"},
                        "email": {"label": "Email", "width": "large"},
                        "date_added": {"label": "Date Added", "width": "medium"}
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No contacts found matching your search")
        else:
            st.info("Enter a search term to find contacts")

# App flow control
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login_page()
else:
    contact_manager()