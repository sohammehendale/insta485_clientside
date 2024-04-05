"""REST API for posts."""
from audioop import reverse
import insta485
import hashlib
import flask


def http_authentication(username, password):
    """Authenticate through HTTP."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password " "FROM users " "WHERE username=?", (username,)
    )
    p = cur.fetchall()
    # username doesn't exist (query is empty)
    if len(p) == 0:
        return False
    hashed_password = p[0]["password"]
    db_password_split = hashed_password.split("$")
    salt = db_password_split[1]
    salted_password = salt + password
    algorithm = "sha512"
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(salted_password.encode("utf-8"))
    input_password = hash_obj.hexdigest()
    return True if (db_password_split[2] == input_password) else False


@insta485.app.route("/api/v1/")
def get_index():
    """Hardcoded api routes."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }
    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/", methods=["GET"])
def get_api_posts():
    """Return api for given route."""
    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return (
                flask.jsonify({"message": "Forbidden", "status_code": 403}),
                403,
            )
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return (
            flask.jsonify({"message": "Forbidden", "status_code": 403}),
            403,
        )
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?", (logname,)
    )
    following_list = []
    f = cur.fetchall()
    for user in f:
        following_list.append(user["username2"])
    following_list.append(logname)
    print(following_list)

    # cur = connection.execute(
    #     "SELECT postid FROM posts WHERE owner",
    #     "IN (SELECT username2 from following
    # WHERE username1 = ? OR owner = ?)",
    #     (logname, logname)
    # )
    # print(cur.fetchall())
    postid_lte = flask.request.args.get("postid_lte", type=int)
    page = flask.request.args.get("page", default=0, type=int)
    size = flask.request.args.get("size", default=10, type=int)
    if size < 0 or page < 0:
        return (
            flask.jsonify({"message": "Bad Request", "status_code": 400}),
            400,
        )

    if postid_lte is None:
        cur = connection.execute(
            "SELECT MAX(postid) as max FROM posts WHERE owner IN "
            "((SELECT username2 from following WHERE username1=?), ?)",
            (logname, logname),
        )
        postid_lte = cur.fetchone()["max"]
    print(postid_lte)
    cur = connection.execute(
        "SELECT owner from posts WHERE postid <= ?", (postid_lte,)
    )
    post_owners = cur.fetchall()

    # num_posts = int(cur.fetchone()['num'])
    num_posts = len([p for p in post_owners if p["owner"] in following_list])
    print(num_posts)
    offset = num_posts - (size * (page + 1))
    # offset = postid_lte - (size * (page + 1))
    print("Offset: ", offset)
    context = {"url": (flask.request.url).replace("http://localhost", "")}

    cur = connection.execute(
        "SELECT postid, owner FROM posts",
    )

    all_posts = cur.fetchall()

    posts_following = [
        post for post in all_posts if (post["owner"] in following_list)
    ]
    posts = []
    if offset < 0:
        offset = offset + size
        if offset < 0:
            offset = 0
        context["next"] = ""
        # cur = connection.execute(
        #     "SELECT postid, owner FROM posts LIMIT ? WHERE owner IN ",
        #     (offset, )
        # )
        for i in range(offset):
            posts.append(posts_following[i])

    else:
        context["next"] = (
            f"/api/v1/posts/?size={size}"
            f"&page={page + 1}&postid_lte={postid_lte}"
        )
        # cur = connection.execute(
        #     "SELECT postid, owner FROM posts LIMIT ? OFFSET ?  ",
        #     (size, offset)
        # )
        print(size)
        print(len(posts))
        for i in range(size):
            posts.append(posts_following[i + offset])
    # posts_not_filtered = cur.fetchall()
    # posts = [p for p in posts_not_filtered if p['owner'] in following_list]
    # posts = cur.fetchall()
    posts.sort(key=lambda post: post["postid"], reverse=True)

    for post in posts:
        post["url"] = f"/api/v1/posts/{post['postid']}/"
        post.pop("owner", None)
    print(posts)
    context["results"] = posts
    return flask.jsonify(**context)
    # numposts < lte - offset - len(posts)
    # 35 posts, lte = 36 page 0:
    # offset = 35 - (10 * 1) = 25, 35-26, PAGE 1: offset = 35 - 20 15, 16-25,
    # PAGE 2, 6-15, PAGE 3. offset = 35 - (10 * 4) = -5 + 10 = 5
    # 11 posts, lte = 11, page 0:
    # offset = 11 - (10 * 1) = 1, 2 - 11,
    # PAGE 1, offset = 11 - (10 * 2) = -9,
    # 1 SELECT postid FROM posts LIMIT 1


@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/", methods=["GET"])
def get_post(postid_url_slug):
    """Return post on postid."""
    """
    Example:
    {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": "/posts/1/",
        "url": "/api/v1/posts/1/"
    }
    """
    # username = flask.request.authorization['username']
    # password = flask.request.authorization['password']
    # if ('login' not
    # in flask.session and not http_authentication(username, password)):
    # 	return flask.jsonify({'message': "Forbidden", 'status_code': 403})
    # if ('login' in flask.session):
    # 	logname = flask.session['login']
    # else:
    # 	logname = username

    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return (
                flask.jsonify({"message": "Forbidden", "status_code": 403}),
                403,
            )
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return (
            flask.jsonify({"message": "Forbidden", "status_code": 403}),
            403,
        )

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT postid, filename as img_url, created as timestamp, owner "
        "FROM posts WHERE postid = ? ",
        (postid_url_slug,),
    )
    user_info = cur.fetchone()
    if user_info is None:

        return (
            flask.jsonify({"message": "Not Found", "status_code": 404}),
            404,
        )

    cur = connection.execute(
        "SELECT filename FROM users WHERE username=?", (user_info["owner"],)
    )
    user_img_url = cur.fetchone()["filename"]

    # get all comments
    cur = connection.execute(
        "SELECT commentid, owner, text FROM comments WHERE postid=?",
        (postid_url_slug,),
    )

    comments = cur.fetchall()
    print(comments)
    for comment in comments:
        comment["lognameOwnsThis"] = (
            True if logname == comment["owner"] else False
        )
        comment["ownerShowUrl"] = f"/users/{comment['owner']}/"
        comment["url"] = f"/api/v1/comments/{comment['commentid']}/"
        print(comment)
    # likes object

    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=?", (postid_url_slug,)
    )
    likes = cur.fetchall()
    num_likes = len(likes)
    owners = [like["owner"] for like in likes]
    lognameLikesThis = True if logname in owners else False
    likes_object = {
        "lognameLikesThis": lognameLikesThis,
        "numLikes": num_likes,
        "url": None,
    }
    if lognameLikesThis is True:
        for like in likes:
            if like["owner"] == logname:
                likes_object["url"] = f"/api/v1/likes/{like['likeid']}/"
                break
    context = {
        "comments": comments,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": user_info["timestamp"],
        "imgUrl": f"/uploads/{user_info['img_url']}",
        "likes": likes_object,
        "owner": user_info["owner"],
        "ownerImgUrl": f"/uploads/{user_img_url}",
        "ownerShowUrl": f"/users/{user_info['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/",
    }
    return flask.jsonify(**context)


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Return api for given route."""
    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return flask.jsonify({"message": "Forbidden", "status_code": 403})
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return flask.jsonify({"message": "Forbidden", "status_code": 403})

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM comments WHERE commentid=?", (commentid,)
    )
    comment = cur.fetchall()
    if len(comment) == 0:
        return (
            flask.jsonify({"message": "Not Found", "status_code": 404}),
            404,
        )
    elif logname != comment[0]["owner"]:
        return (
            flask.jsonify({"message": "Forbidden", "status_code": 403}),
            403,
        )
    cur = connection.execute(
        "DELETE FROM comments WHERE commentid=?", (commentid,)
    )
    return "", 204


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def post_likes():
    """Return api for given route."""
    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return flask.jsonify({"message": "Forbidden", "status_code": 403})
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return flask.jsonify({"message": "Forbidden", "status_code": 403})
    connection = insta485.model.get_db()
    postid = flask.request.args.get("postid")
    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=? AND owner = ?",
        (
            postid,
            logname,
        ),
    )
    doesLike = cur.fetchone()
    if doesLike is None:
        connection.execute(
            "INSERT INTO likes (owner, postid) VALUES(?, ?)",
            (
                logname,
                postid,
            ),
        )
        cur = connection.execute(
            "SELECT likeid FROM likes WHERE postid=? AND owner = ?",
            (
                postid,
                logname,
            ),
        )
        findLikeId = cur.fetchone()
        context = {
            "likeid": findLikeId["likeid"],
            "url": f"/api/v1/likes/{findLikeId['likeid']}/",
        }
        return flask.jsonify(**context), 201
    else:
        context = {
            "likeid": doesLike["likeid"],
            "url": f"/api/v1/likes/{doesLike['likeid']}/",
        }
        return flask.jsonify(**context), 200


@insta485.app.route("/api/v1/likes/<likeid>/", methods=["DELETE"])
def delete_likes(likeid):
    """Return api for given route."""
    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return flask.jsonify({"message": "Forbidden", "status_code": 403})
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return flask.jsonify({"message": "Forbidden", "status_code": 403})
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT likeid, owner FROM likes WHERE likeid=? ", (likeid,)
    )
    like = cur.fetchone()
    if like is None:
        return (
            flask.jsonify({"message": "Not Found", "status_code": 404}),
            404,
        )
    if like["owner"] != logname:
        return (
            flask.jsonify({"message": "Forbidden", "status_code": 403}),
            403,
        )
    connection.execute("DELETE FROM likes WHERE likeid = ? ", (likeid,))
    return flask.jsonify({"message": "NO CONTENT", "status_code": 204}), 204


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def add_comment():
    """Return api for given route."""
    if "login" not in flask.session and flask.request.authorization:
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        if not http_authentication(username, password):
            return flask.jsonify({"message": "Forbidden", "status_code": 403})
        else:
            logname = username
    elif "login" in flask.session:
        logname = flask.session["login"]
    else:
        return flask.jsonify({"message": "Forbidden", "status_code": 403})
    text = flask.request.json["text"]
    connection = insta485.model.get_db()
    print(flask.request.args.get("postid"))
    connection.execute(
        "INSERT INTO comments(owner, postid, text) VALUES(?, ?, ?)",
        (logname, flask.request.args.get("postid"), text),
    )

    cur = connection.execute("SELECT last_insert_rowid() from comments")
    row_id = cur.fetchone()["last_insert_rowid()"]
    cur = connection.execute(
        "SELECT * FROM comments WHERE commentid=?", (row_id,)
    )
    comment = cur.fetchone()
    context = {
        "commentid": comment["commentid"],
        "lognameOwnsThis": True if comment["owner"] == logname else False,
        "owner": comment["owner"],
        "ownerShowUrl": f"/users/{comment['owner']}/",
        "text": text,
        "url": f"/api/v1/comments/{row_id}/",
    }
    return flask.jsonify(**context), 201
