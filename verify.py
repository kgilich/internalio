def verify_mail(email):
    if not "@decathlon.com" in email:
        return "chyba"
    else:
        return "ok"