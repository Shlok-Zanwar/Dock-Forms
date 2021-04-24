import smtplib
import random


def send_otp(email):
    my_email = "projectforms1@gmail.com"
    rec_email = email
    password = ""

    otp = random.randint(100000, 999999)
    print(otp)

    message = 'Your OTP for Sign-Up is '+str(otp)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    #server.connect("smtp.gmail.com", 587)
    #server.ehlo()
    server.starttls()
    print("done")
    server.ehlo()
    server.login(my_email, password)
    print("login done")

    server.sendmail(my_email, rec_email, message)
    server.quit()

    return otp
