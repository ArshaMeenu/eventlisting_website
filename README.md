# Website for Event Listing : 


# The features consist of: 
      1.Admin should be able to add events from django default admin
      2.List the events with pagination, 10 per page.
      3.By default sort the events by date
      4.Filter events by:- Date range(from date and to date) and Categories.
      5.Search event by keyword.
      6.User registration and login
      7.Registered users can Like or dislike an event(Use Ajax for this)
      8.Users can pay a fixed amount and book a paid event(Prefer to use stripe as the payment gateway).Send an email notification once booked
      9.Profile:
        a. Edit profile
        b. Set profile pic
        c. View bookings - past and future bookings


# Overview of the steps involved: -
      1. Firstly, use the django-admin startproject command to create a project ‘listevents’.
      2. Then, use the django-admin start-app command to create an app - ‘events’ -  inside the project.
      3. Keep all the html templates in the templates folder and static files like images,css or js, in static folder.
      4. Run the python manage.py migrate command to apply all the Django built in migrations.
      5. Create a superuser with an username (admin), email(****n@gmail.com) and password(********).
      6. Create a Custom user model for the project.
      7. Start making the urls for the project.
      8. Payment using stripe is taken over.
