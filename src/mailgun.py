import requests

MAILGUN = dict({
    'API' : 'https://api.mailgun.net/v2',
    'API_KEY':'key-368lolg8r2boq0c8ne79rvjwxbz8z7m7',
    'PUBLIC_KEY':'pubkey-7rqbqc89aoxxxjorzec9e75ozq88aqc8',
    'URL':'bluerover.mailgun.org'
})

def send_email(email,subject,message):
    return requests.post(
        "https://api.mailgun.net/v2/samples.mailgun.org/messages",
        auth=("api", MAILGUN['API_KEY']),
        data={"from": ("Notification <demo@%s>"% MAILGUN['URL']),
              "to": [email],
              "subject": subject,
              "text": message})