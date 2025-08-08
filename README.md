![Desk Reservation App short Demo](static/images/for_git.gif)
Desk Reservation App
====================

Overview
--------
This is a **Desk Reservation Application** built using **Python** and **Flask**. The app allows users to register, log in, and reserve desks in an office space. The application features **secure login** with **password hashing**, and **email-based registration** restricted to permitted users.

Features
--------
- **User Registration & Login**:
  - Registration is allowed only for users whose emails are in the `permitted_user_emails.txt` file (not included in the GitHub repository for security).
  - Passwords are securely hashed before storing.
  
- **Desk Reservation**:
  - After logging in, users can view available desks, with details and images for each.
  - Users can hover over a desk to see the number of days it is reserved for.
  - Once a desk is clicked, its details and availability are displayed.
  - **One reservation per user**: Each user can only have one active reservation at a time.
  
- **Admin Access**:
  - Only the admin can modify the `permitted_user_emails.txt` file, granting or revoking registration privileges.
  
- **Reservation Statistics**:
  - Users can see the number of days they've spent in the office and their total number of days over time.

- **Reservation Notifications**:
  - Upon successful reservation, users receive a confirmation email with reservation details.
  
- **Additional Features**:
  - Desks are marked as **reserved** with unavailable dates.
  - The reservation system checks for overlapping reservations.
  - The interface displays the current date and time for convenience.

Technologies Used
----------------
- **Flask**: Web framework for Python
- **Flask-Login**: For user authentication
- **Flask-SQLAlchemy**: For database management
- **Werkzeug**: For password hashing
- **Flask-Bootstrap**: For responsive design
- **Flask-CKEditor**: For rich text editing (if needed)
- **Flask-Mail**: For sending email notifications
- **SQLAlchemy**: ORM for database interaction
- **SQLite**: Database for storing user and reservation data
