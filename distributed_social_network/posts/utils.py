from enum import Enum


class ContentType(Enum):
    # Choices for content-type
    MARKDOWN = "MKD"
    PLAIN = "TXT"
    APPLICATION = "APP"
    PNG = "PNG"
    JPEG = "JPG"

    @classmethod
    def get_choices(cls):
        return (
            (cls.MARKDOWN.value, "text/markdown"),
            (cls.PLAIN.value, "text/plain"),
            (cls.APPLICATION.value, "application/base64"),
            (cls.PNG.value, "imgage/png;base64"),
            (cls.JPEG.value, "image/jpeg;base64")
        )


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

    @classmethod
    def get_choices(cls):

        return (
            (cls.PUBLIC.value, "Public"),
            (cls.FOAF.value, "Friend of a Friend"),
            (cls.PRIVATE.value, "Private"),
            (cls.SERVERONLY.value, "Home Server Only")
        )
