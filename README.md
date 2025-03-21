# Contact Manager - Simple Django Web Application

A user-friendly web application for managing contacts and exporting them as VCF files (which can be imported into your phone's contact list).

## Features

- Add, edit, and delete contacts
- Search through contacts in real-time
- Export contacts as VCF file
- Responsive design (works on mobile devices)
- Modern and intuitive interface

## Step-by-Step Installation Guide for Beginners

### 1. Install Required Software

First, you need to install some software on your computer:

#### For Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
   - Click the big yellow "Download Python" button
   - Make sure to check "Add Python to PATH" during installation
2. Download Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/)
   - This will be your text editor
   - Just click the big blue "Download" button for Windows

#### For Mac:
1. Install Python from [python.org](https://www.python.org/downloads/)
   - Click the yellow "Download Python" button
2. Download Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/)
   - Click the blue "Download" button for Mac

### 2. Set Up the Project

1. Create a new folder on your computer for the project
2. Open Command Prompt (Windows) or Terminal (Mac)
   - Windows: Press Windows key + R, type "cmd", press Enter
   - Mac: Press Command + Space, type "terminal", press Enter

3. Navigate to your project folder (replace `path/to/your/folder` with your actual folder path):
```bash
cd path/to/your/folder
```

4. Create a virtual environment:
```bash
python -m venv env
```

5. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Mac: `source env/bin/activate`

6. Install Django:
```bash
pip install django
```

### 3. Create and Set Up the Django Project

1. Create a new Django project:
```bash
django-admin startproject kmt_tools
cd kmt_tools
```

2. Create a new app:
```bash
python manage.py startapp contacts
```

3. Copy the code files from this repository into their respective locations:
   - Copy `models.py` content to `contacts/models.py`
   - Copy `views.py` content to `contacts/views.py`
   - Copy `urls.py` content to `contacts/urls.py`
   - Create a `templates` folder in your `contacts` app and copy the template files there

4. Add 'contacts' to INSTALLED_APPS in `kmt_tools/settings.py`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'contacts',  # Add this line
]
```

5. Set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create an admin user:
```bash
python manage.py createsuperuser
```
Follow the prompts to create your username and password

### 4. Running the Application

1. Start the development server:
```bash
python manage.py runserver
```

2. Open your web browser and go to:
   - Main application: `http://127.0.0.1:8000`
   - Admin interface: `http://127.0.0.1:8000/admin`

## How to Use the Application

1. **Adding a Contact:**
   - Click the "Add Contact" button
   - Fill in the contact details
   - Click "Save Contact"

2. **Editing a Contact:**
   - Click the "Edit" button next to any contact
   - Modify the details
   - Click "Save Contact"

3. **Deleting a Contact:**
   - Click the "Delete" button next to any contact
   - Confirm the deletion

4. **Searching Contacts:**
   - Type in the search box to filter contacts
   - Results update in real-time

5. **Exporting Contacts:**
   - Click the "Export VCF" button
   - Save the file
   - Import this file into your phone's contacts app

## Common Issues and Solutions

1. **"Python is not recognized":**
   - Reinstall Python and make sure to check "Add Python to PATH"

2. **"Port already in use":**
   - Close any other running servers
   - Or use a different port: `python manage.py runserver 8001`

3. **Database errors:**
   - Delete the db.sqlite3 file
   - Run `python manage.py migrate` again

## Need Help?

If you encounter any issues or need assistance, feel free to contact the developer:

- WhatsApp: +2348141941192
- Email: brandnova89@gmail.com

## Tips for Non-Technical Users

- Always activate your virtual environment before running any commands
- Keep the server running while using the application
- Make sure you're in the correct folder when running commands
- If something doesn't work, try refreshing your browser
- Save any changes to your code files before testing them

## Backing Up Your Contacts

- Regularly export your contacts as VCF file
- Keep your database file (db.sqlite3) backed up
- Export your contacts before making any major changes

Remember: If you're new to this and feeling overwhelmed, don't hesitate to reach out for help using the contact information above. The application is designed to be user-friendly, but the setup process might need some guidance for beginners.