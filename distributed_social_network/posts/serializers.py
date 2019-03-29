import io

from requests.auth import HTTPBasicAuth
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from posts.models import Post, Categories, Comment
from users.models import User
import requests

visilibityDict = {
    "public": "PUBL",
    'friend of a friend': "FOAF",
    'private': "PRIV",
    'friends': 'FRND'
}
contentTypeDict={
    "text/markdown":"MKD",
    "text/plain":"TXT",
    "application/base64":"APP",
    "image/png;base64":"PNG",
    "image/jpeg;base64":"JPG"
}

def requestPosts(node, ending, current_id):
    try:
        a = requests.get(node.hostname+node.prefix+ending, headers={"X-User":str(current_id)}, auth=HTTPBasicAuth(node.send_username,node.send_password))
        if a.status_code!=200:
            print('pepega')
            a = requests.get(node.hostname + node.prefix + ending, headers={"X-AUTHOR-ID": str(current_id)},
                             auth=HTTPBasicAuth(node.send_username, node.send_password))

        if a.status_code==200:
            print('200')
            stream = io.BytesIO(a.content)
            data = JSONParser().parse(stream)
            l = posts_request_deserializer(data=data)
            l.is_valid()
            for i in l.validated_data['posts']:
                post = post_deserializer_no_comment(data=i)
                if post.is_valid():
                    new_post = post.create(post.validated_data)
                    if new_post!=None:
                        if new_post.origin=='':
                            new_post.origin = node.hostname+node.prefix+ 'posts/'+ str(new_post.id)
                        if new_post.source=='':
                            new_post.source = node.hostname+node.prefix+ 'posts/'+ str(new_post.id)
                        new_post.author.host=node
                        new_post.author.save()
                        new_post.save()
                        print('saved new post id :'+str(new_post.id))
                    else:
                        print('passed')
                        pass
                else:
                    print(post.errors)
            return True
    except Exception as e:
        print(e)

def requestSinglePost(link, current_id, node):
    try:
        print('getting:'+link)
        a = requests.get(link, headers={"X-User":str(current_id)}, auth=HTTPBasicAuth(node.send_username,node.send_password))
        if a.status_code!=200:
            print(a.status_code)
            a = requests.get(link, headers={"X-AUTHOR-ID":str(current_id)},auth=HTTPBasicAuth(node.send_username, node.send_password))
        if a.status_code==200:
            print('200')
            stream = io.BytesIO(a.content)
            data = JSONParser().parse(stream)
            l = posts_request_deserializer(data=data)
            l.is_valid()
            for i in l.validated_data['posts']:
        #assumes we have the post alrdy
                post = post_detail_deserializer(data=i)
                if post.is_valid():
                    post.create(post.validated_data)
            return True
    except Exception as e:
        print('ERROR :',e)




# for multiple posts that you don't need the comments
class posts_request_deserializer(serializers.Serializer):
    posts = serializers.ListField()



class post_detail_deserializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    source = serializers.CharField(required=False, default='')
    description = serializers.CharField()
    contentType = serializers.CharField()
    content = serializers.CharField()
    categories = serializers.ListField(required=False, default=[])
    published = serializers.DateTimeField()
    visibility = serializers.CharField()
    visibleTo = serializers.ListField(required=False, default=[])
    unlisted = serializers.BooleanField(required=False, default=False),
    comments = serializers.ListField()

    def create(self,validated_data):
        print(validated_data)
        existing_post=Post.objects.filter(id=validated_data['id'])
        existing_post.update(title=validated_data['title'],
                             content_type=contentTypeDict[validated_data['contentType']],
                             description=validated_data['description'],
                             content=validated_data['content'],)
                             #unlisted=validated_data['unlisted'])
        for comment in validated_data['comments']:
            a=comment_deserializer(data=comment)
            if a.is_valid():
                the_comment=a.create(a.validated_data,existing_post)
                if the_comment:
                    the_comment.save()
            else:
                print(a.errors)
        return True



class comment_deserializer(serializers.Serializer):
    contentType=serializers.CharField()
    comment=serializers.CharField()
    id=serializers.UUIDField()
    published=serializers.DateTimeField()
    author= serializers.DictField()

    def create(self,validated_data, comment_post):
        usr=user_deserializer(data=validated_data['author'])
        if usr.is_valid():
            comment_usr=usr.create(usr.validated_data)
            try:
                existing_comment=Comment.objects.get(id=validated_data['id'])
                return None
            except:
                return Comment.objects.create(
                    id=validated_data['id'],
                    comment=validated_data['comment'],
                    content_type=contentTypeDict[validated_data['contentType'].lower()],
                    author=comment_usr,
                    published=validated_data['published'],
                    post=comment_post[0]
            )



# for single post with no comments
class post_deserializer_no_comment(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    source = serializers.CharField(required=False, default='')
    description = serializers.CharField()
    contentType = serializers.CharField()
    author = serializers.DictField()
    content = serializers.CharField()
    categories = serializers.ListField(required=False, default=[])
    published = serializers.DateTimeField()
    visibility = serializers.CharField()
    visibleTo = serializers.ListField(required=False, default=[])
    unlisted = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        usr = user_deserializer(data=validated_data['author'])

        if usr.is_valid():
            post_usr = usr.create(usr.validated_data)

            tags = validated_data['categories']

        #implement later, working on public stuff rn
            visibleList = []
            for ids in validated_data['visibleTo']:
            # asssuming that either we have the user in here or we dont care, since its guaranteed to be not our user
                u = User.objects.get(id=ids)
                if u:
                    visibleList.append(u)
            categories = []
            for tag in tags:
                if Categories.objects.filter(name=tag).count() == 0:
                    a=Categories.objects.create(name=tag)
                    a.save()
                categories.append(tag)

            try:
                existing_post=Post.objects.get(id=validated_data['id'])
                return None
            except:
                print(validated_data['visibility'])
                print(validated_data['contentType'])
                return Post.objects.create(
                id=validated_data['id'],
                title=validated_data['title'],
                source=validated_data['source'],
                description=validated_data['description'],
                content_type=contentTypeDict[validated_data['contentType'].lower()],
                author=post_usr,
                content=validated_data['content'],
                published=validated_data['published'],
                visibility=visilibityDict[validated_data['visibility'].lower()],
                #visible_to=visibleList,
                unlisted=validated_data['unlisted']
            )
        else:
            print(usr.errors)


# TODO make changes to this
class user_deserializer(serializers.Serializer):
    id = serializers.CharField()
    # i dont know do we even have an email field?
    # email = serializers.EmailField()
    #bio = serializers.CharField()
    host = serializers.CharField()
    #firstName = serializers.CharField()
    #lastName = serializers.CharField()
    displayName = serializers.CharField()
    url = serializers.CharField()
    github = serializers.CharField(allow_null=True)

    def create(self, validated_data):
        url_with_id=validated_data['id'].split('/')
        id=url_with_id[-1]
        try:
            usr = User.objects.get(id=id)
            return usr
        except:
            url_with_id = validated_data['id'].split('/')
            id = url_with_id[-1]
            print('created user'+id)
            # also host doesnt have to be our node, can be just random
            # mention this tmr
            usr = User.objects.create(
                username = validated_data['displayName'],
                id=id,
                #bio=validated_data['bio'],
                display_name=validated_data['displayName'],
                local=False
                #host=validated_data['host'],
            )
            usr.set_unusable_password()
            usr.save()
            return usr