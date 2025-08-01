import datetime
import smtplib

from authentik_client.models.flow import Flow
from authentik_client.models.invitation import Invitation

from invite_tool.user import HomelabUser


class InviteEmail:
    def __init__(
        self,
        user: HomelabUser,
        fromAddress: str,
        invite: Invitation,
        flow: Flow,
        authURL: str,
    ):
        self.user = user
        # self.username = user.username
        # self.name = user.fullName()
        # self.toAddr = user.email
        self.fromAddr = fromAddress
        self.expires = invite.expires
        # self.pk = invite.pk
        # self.slug = flow.slug
        self.inviteLink = f"https://{authURL}/if/flow/{flow.slug}/?itoken={invite.pk}"

        self.message = f"""\
Subject: Welcome to das homelab!
To: {self.user.fullName()} <{self.user.email}>
From: Authentik on das homelab <{self.fromAddr}>
Date: {str(datetime.datetime.today())}
Category: Homelab invite

Welcome to "das homelab", Noah's server -- a.k.a. homelab -- running out of his dorm room! Below is the link to activate your new account... BUT, before you click it, please read the information below:

- The username you are given cannot be easily changed. 
- The email this was sent to will be set as the primary email on your account. All homelab-related notifications, such as shared file alerts or password reset emails, will be sent here. This can be changed in the user settings inside Authentik.


Also, take note of these important URLs:

- Homepage (home.noahsroberts.com) - where links to all the things in the homelab live, including some extras beyond those listed below. 
- Authentik (auth.noahsroberts.com) - the single sign-on system, prominently displaying the "das homelab" logo 
- Nextcloud (files.noahsroberts.com) - like Google Drive, but self-hosted and on steroids 
- BookStack (wiki.noahsroberts.com) - internal, user-facing wiki 
{self.plexInfo()}

So, what is this email? Well, it's an invite. You are by no means obligated to accept it, but it would make your friend pretty dang happy. You might find some cool stuff in there, too. And, if you decide to pass for now but change your mind later, just let Noah know and he'll send you another invite.


When you click the link below, it will automatically create a new user with the following information:
- Name: {self.user.fullName()} 
- Username: {self.user.username} 
- Email: {self.user.email} 
{self.adminInfo()}

===
Clicking the invite link below will walk you through a brief enrollment process before presenting you with your Authentik dashboard. 

Invite link: {self.inviteLink} 
Expires: {str(self.expires)} 
===


Happy Homelabbing!
"""

    def plexInfo(self):
        if "plexuser" in self.user.groups:
            return "- Plex (plex.noahsroberts.com or plex.tv) - self-hosted media server, supporting movies, TV, and music\n\nNote: You were added as a Plex user, but giving you access to the Plex server is not automatic. You will need to create a Plex account and let Noah know what what email you used to make it. Then he can send you an invite which will go to your email inbox. Once you accept it, you *should* have access to the Plex server. It may be worth doing this with Noah, just to make sure it actually works -- because sometimes it doesn't.\n"
        else:
            return ""

    def adminInfo(self):
        if "admin" in self.user.groups:
            return "\n\nAs you are an admin, please note the following information: \n- Please set up two-factor authentication as soon as possible. Information on how to do so is available here: https://wiki.noahsroberts.com/books/authentik/page/2fa-setup \n- Accessing some administrative areas, such as Proxmox and TrueNAS, require Twingate to connect, as they are too sensitive to expose to the Internet. \n- If you are trying to sign into Proxmox but it fails, let Noah know as soon as possible, as this likely means he hasn't set up your user in Proxmox yet.\n"
        else:
            return ""

    def mailtrapSend(self, apiKey: str):
        with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            server.starttls()
            server.login("api", apiKey)
            server.sendmail(self.fromAddr, self.user.email, self.message)

    def send(self, mailtrapApiKey: str):
        self.mailtrapSend(mailtrapApiKey)
        if "plexuser" in self.user.groups:
            print(
                f"You'll need to manually invite {self.user.first} to Plex once they create a Plex account."
            )
