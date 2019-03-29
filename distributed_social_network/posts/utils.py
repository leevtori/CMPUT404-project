from enum import Enum

content_type_str = {
    "MKD": "text/markdown",
    "TXT": "text/plain",
    "APP": "application/base64",
    "PNG": "image/png;base64",
    "JPG": "image/jpeg;base64"
    }


visibility_str = {
    "PUBL": "Public",
    "FOAF": "Friend of a Friend",
    "PRIV": "Private",
    "SERV": "Home Server Only",
    "FRND": "Friends Only"
}


class ContentType(Enum):
    # Choices for content-type
    MARKDOWN = "MKD"
    PLAIN = "TXT"
    APPLICATION = "APP"
    PNG = "PNG"
    JPEG = "JPG"

    @classmethod
    def get_choices(cls):
        return [(key, value) for key, value in content_type_str.items()]
        # return (
        #     (cls.MARKDOWN.value, "text/markdown"),
        #     (cls.PLAIN.value, "text/plain"),
        #     (cls.APPLICATION.value, "application/base64"),
        #     (cls.PNG.value, "imgage/png;base64"),
        #     (cls.JPEG.value, "image/jpeg;base64")
        # )

    def __str__(self):
        return self.value

    def get_readable_str(self):
        return content_type_str[self.value]


class Visibility(Enum):
    # Choices for visibility
    # ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
    #  for visibility PUBLIC means it is open to the wild web
    # FOAF means it is only visible to Friends of A Friend
    # If any of my friends are your friends I can see the post
    # FRIENDS means if we're direct friends I can see the post
    # PRIVATE means only you can see the post
    # SERVERONLY means only those on your server (your home server) can see the post
    # PRIVATE means only authors listed in "visibleTo" can see the post
    PUBLIC = "PUBL"
    FOAF = "FOAF"
    PRIVATE = "PRIV"
    SERVERONLY = "SERV"
    FRIENDSONLY = "FRND"

    @classmethod
    def get_choices(cls):
        return [(key, value) for key, value in visibility_str.items()]

    def __str__(self):
        return self.value

    def get_readable_str(self):
        return visibility_str[self.value]

