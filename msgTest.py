import smtplib


class TestEmail:
	def __init__(self, sender, receiver) -> None:
		self.fromAddr = sender
		self.toAddr = receiver

		self.message = f"""\
Subject: Hi Mailtrap
To: {self.toAddr}
From: {self.fromAddr}

This is a test e-mail message.
		"""

		print(self.fromAddr, self.toAddr, self.message)

sender = "Private Person <mailtrap@noahsroberts.com>"
receiver = "A Test User <noah10838@gmail.com>"
message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

t = TestEmail(sender, receiver)

with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
	server.starttls()
	server.login("api", "b0c082fbf8d9f9f6b1182cdd067f3248")
	server.sendmail(t.fromAddr, t.toAddr, t.message)