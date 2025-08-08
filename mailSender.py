import os
import smtplib
from datetime import datetime

class SendEmail:
    def __init__(self):
        self.connection = smtplib.SMTP('smtp.gmail.com', 587)
        self.connection.starttls()
        self.connection.login(user=os.environ.get("MY_EMAIL"), password=os.environ.get("PASS"))

    def send_email(self, user_email, message, user_name, desk_nr, start_date, end_date):

        date_diff = (end_date - start_date).days

        if date_diff >= 1:
            reservation_message = f"You are reserving desk number {desk_nr} from {start_date} to {end_date}."
        else:
            reservation_message = f"You are reserving desk number {desk_nr} for {start_date}."

        email_body = f"Subject: Reservation Confirmation\n\nHi {user_name},\n\n{reservation_message}\n\n{message}\n\nHave a nice day!"
        self.connection.sendmail(from_addr=os.environ.get("MY_EMAIL"), to_addrs=user_email, msg=email_body)
        self.connection.quit()