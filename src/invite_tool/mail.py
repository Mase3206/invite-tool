class Email:
    """
    Email object that checks for validity of given email when initalized.
    """

    def __init__(self, email: str):
        a = email.split("@")[0]
        b = email.split("@")[1]
        self.prefix = a
        self.domain = b.split(".")[0]
        self.tld = b.split(".")[1]

        if self.domain == "localhost":
            self.addr = f"{self.prefix}@localhost"

        else:
            self.addr = f"{self.prefix}@{self.domain}.{self.tld}"

    def __str__(self) -> str:
        return self.addr

    def __repr__(self) -> str:
        return f"pre={self.prefix}, domain={self.domain}, tld={self.tld}"
