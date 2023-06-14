# Sriram_CoWIN
This is my CoWin Application to book covid vaccination slots made using Mongo Atlas for backend database connectivity.

# How to run this Application:

Within src, run the following commands:
    pip3 install -r requirements.txt
    python3 flaskapp.py

A host link will be displayed in the command prompt
copy and use the link to run the application in web.
    

# User_Guidelines

Any user can sign up by providing the necessary details and login with their own username and password.
After logging in provide your location preference in the search box.
Vaccine centres in your search locations will be displayed .
Dosage details and available slots will also be displayed to the user.
This application is built in such a way that only 10 will be available for users per day in each centres.
Once a slot is booked, a success notification will be shown to the user.
User can proceed for log out.

# Admin_Guidelines:

Admin will only have the authority to add or remove vaccination centres.
For Admin, the admin credentials will be:

username: admin
password: qwertyuiop

log in with these credentials.
Once logged in, change the source link form http://127.0.0.1:5000/Home to http://127.0.0.1:5000/admin
/admin will take you to the admin page where new centres can be added.
Already existing centres can also be removed from the choices only by the admin.
Once done admin can log out from the application.
