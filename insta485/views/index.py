"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
import arrow
import uuid
import hashlib
import pathlib
import os

# Helper functions


def check_password(password: str, username: str) -> bool:
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password " "FROM users " "WHERE username=?", (username,)
    )
    hashed_password = cur.fetchone()["password"]
    db_password_split = hashed_password.split("$")
    print(db_password_split)
    salt = db_password_split[1]
    salted_password = salt + password
    algorithm = "sha512"
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(salted_password.encode("utf-8"))
    input_password = hash_obj.hexdigest()
    print(input_password)
    return True if (db_password_split[2] == input_password) else False


def check_logged_in():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return False
    else:
        return True


def get_new_hashed_password(password: str) -> str:
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    algorithm = "sha512"
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode("utf-8"))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


@insta485.app.route("/", methods=["GET"])
def show_index():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT *" "FROM posts")
    posts = cur.fetchall()

    # posts = [{all the data for one post}, {all the data for post 2}]
    posts.sort(reverse=True, key=lambda x: x["created"])
    for post in posts:
        postid = post["postid"]

        post["created"] = arrow.get(post["created"]).humanize()
        # we want to get the number of likes for that post
        cur = connection.execute(
            "SELECT * " "FROM likes " "WHERE postid=?", (postid,)
        )
        likes = cur.fetchall()
        post["num_likes"] = len(likes)
        post["likes"] = likes
        user_liked_post = any(
            x["owner"] == flask.session["login"] for x in likes
        )
        post["user_liked_post"] = user_liked_post
        # get comments: comments = {[all the data for one comment
        # (comment id, owner, text, created)], [all the data for comment 2]}
        cur = connection.execute(
            "SELECT commentid, owner, text, created "
            "FROM comments "
            "WHERE postid=?",
            (postid,),
        )
        comments = cur.fetchall()
        post["comments"] = comments
        # get pfp
        cur = connection.execute(
            "SELECT filename " "FROM users " "WHERE username=?",
            (post["owner"],),
        )
        pfp = cur.fetchall()
        post["pfp"] = pfp[0]["filename"]
        cur = connection.execute(
            "SELECT COUNT(*) as following "
            "FROM following WHERE username1=? and username2=?",
            (flask.session["login"], post["owner"]),
        )
        following = cur.fetchone()
        post["following"] = following["following"]
        print(post["likes"])
    context = {
        "posts": posts,
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("index.html", **context)
    # [{'username': 'jflinn', 'fullname': 'Jason Flinn'},
    # {'username': 'michjc', 'fullname': 'Michael Cafarella'},
    # {'username': 'jag', 'fullname': 'H.V. Jagadish'}]


@insta485.app.route("/users/<username>/", methods=["GET"])
def show_user_page(username):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    )
    user_data = cur.fetchone()
    print(user_data)
    cur = connection.execute("SELECT * FROM posts WHERE owner=?", (username,))
    posts = cur.fetchall()
    user_data["posts"] = posts
    user_data["total_posts"] = len(posts)
    if flask.session["login"] != username:
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? and username2=?",
            (flask.session["login"], username),
        )
        f = cur.fetchall()
        logname_follows_username = True if len(f) == 1 else False
        print(logname_follows_username)
        user_data["logname_follows_username"] = logname_follows_username

    # get followers and following
    cur = connection.execute(
        "SELECT * FROM following WHERE username2=?", (username,)
    )
    followers = len(cur.fetchall())
    cur = connection.execute(
        "SELECT * FROM following WHERE username1=?", (username,)
    )
    following = len(cur.fetchall())
    user_data["followers"] = followers
    user_data["following"] = following
    print(posts)
    context = {
        "user_data": user_data,
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("user.html", **context)


@insta485.app.route("/posts/<postid>/", methods=["GET"])
def show_post(postid):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect("/accounts/login/")
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT * FROM posts WHERE postid=?", (postid,))
    post = cur.fetchone()
    post["created"] = arrow.get(post["created"]).humanize()
    cur = connection.execute(
        "SELECT filename as pfp FROM users WHERE username=?", (post["owner"],)
    )
    filename = cur.fetchone()["pfp"]
    post["pfp"] = filename
    cur = connection.execute(
        "SELECT COUNT(*) as num_likes FROM likes WHERE postid=?", (postid,)
    )
    num_likes = cur.fetchone()["num_likes"]
    post["num_likes"] = num_likes
    cur = connection.execute(
        "SELECT * FROM comments WHERE postid=?", (postid,)
    )
    comments = cur.fetchall()
    post["comments"] = comments
    cur = connection.execute(
        "SELECT * FROM likes WHERE owner=? and postid=?",
        (flask.session["login"], postid),
    )
    user_liked = cur.fetchall()
    user_liked_post = True if len(user_liked) == 1 else False
    context = {
        "post": post,
        "user_liked_post": user_liked_post,
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("post.html", **context)


@insta485.app.route("/accounts/login/", methods=["GET"])
def login_get():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" in flask.session:
        return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("login.html", context={})


@insta485.app.route("/accounts/", methods=["POST"])
def accounts_post():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    # logging in
    if flask.request.form["operation"] == "login":
        if (
            flask.request.form["username"] == ""
            or flask.request.form["password"] == ""
        ):
            flask.abort(400)
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT COUNT(*) as user_exists FROM USERS WHERE username=?",
            (flask.request.form["username"],),
        )
        user_exists = cur.fetchone()
        print(user_exists)
        print(flask.request.args.get("target"))
        if user_exists["user_exists"] != 0 and check_password(
            flask.request.form["password"], flask.request.form["username"]
        ):  # username exists in db
            flask.session["login"] = flask.request.form["username"]
            if not (flask.request.args.get("target")):
                return flask.redirect(flask.url_for("show_index"))
            return flask.redirect(flask.request.args.get("target"))
        else:
            flask.abort(403)
    # edit account
    elif flask.request.form["operation"] == "edit_account":
        if (
            flask.request.form["fullname"] == ""
            or flask.request.form["email"] == ""
        ):
            flask.abort(400)
        elif not flask.request.files["file"]:
            connection = insta485.model.get_db()
            cur = connection.execute(
                "UPDATE users SET fullname=?, email=? WHERE username=?",
                (
                    flask.request.form["fullname"],
                    flask.request.form["email"],
                    flask.session["login"],
                ),
            )
            return flask.redirect(flask.url_for("account_edit"))
        else:
            # get old pfp
            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT filename FROM users WHERE username=?",
                (flask.session["login"],),
            )
            old_filename = cur.fetchone()["filename"]
            fileobj = flask.request.files["file"]
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix
            uuid_basename = f"{stem}{suffix}"
            path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
            fileobj.save(path)
            # remove old file
            os.remove(insta485.app.config["UPLOAD_FOLDER"] / old_filename)
            cur = connection.execute(
                "UPDATE users "
                "SET fullname=?, email=?, filename=? WHERE username=?",
                (
                    flask.request.form["fullname"],
                    flask.request.form["email"],
                    uuid_basename,
                    flask.session["login"],
                ),
            )
            return flask.redirect(flask.url_for("account_edit"))
    elif flask.request.form["operation"] == "update_password":
        if "login" not in flask.session:
            flask.abort(403)
        if (
            flask.request.form["password"] == ""
            or flask.request.form["new_password1"] == ""
            or flask.request.form["new_password2"] == ""
        ):
            flask.abort(400)
        if check_password(
            flask.request.form["password"], flask.session["login"]
        ):
            if (
                flask.request.form["new_password1"]
                != flask.request.form["new_password2"]
            ):
                flask.abort(401)
            new_password = get_new_hashed_password(
                flask.request.form["new_password1"]
            )
            connection = insta485.model.get_db()
            cur = connection.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_password, flask.session["login"]),
            )
            return flask.redirect(flask.request.args.get("target"))
        else:
            flask.abort(403)
    elif flask.request.form["operation"] == "create":
        if (
            flask.request.form["password"] == ""
            or flask.request.form["username"] == ""
            or flask.request.form["fullname"] == ""
            or flask.request.form["email"] == ""
            or flask.request.files["file"].filename == ""
        ):
            flask.abort(400)
        else:
            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT username FROM users WHERE username=?",
                (flask.request.form["username"],),
            )
            username_exists = True if len(cur.fetchall()) > 0 else False
            if username_exists:
                print(username_exists)
                flask.abort(409)
            fileobj = flask.request.files["file"]
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix
            uuid_basename = f"{stem}{suffix}"
            path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
            fileobj.save(path)
            connection.execute(
                "INSERT INTO users(username, fullname, "
                "email, filename, password) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    flask.request.form["username"],
                    flask.request.form["fullname"],
                    flask.request.form["email"],
                    uuid_basename,
                    get_new_hashed_password(flask.request.form["password"]),
                ),
            )

            flask.session["login"] = flask.request.form["username"]
            return flask.redirect(flask.url_for("show_index"))
    elif flask.request.form["operation"] == "delete":
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?",
            (flask.session["login"],),
        )
        filename = cur.fetchone()["filename"]
        os.remove(insta485.app.config["UPLOAD_FOLDER"] / filename)
        cur = connection.execute(
            "SELECT filename FROM posts WHERE owner=?",
            (flask.session["login"],),
        )
        post_files = cur.fetchall()
        for file in post_files:
            print(file)
            os.remove(insta485.app.config["UPLOAD_FOLDER"] / file["filename"])
        connection.execute(
            "DELETE FROM users WHERE username=? ", (flask.session["login"],)
        )
        connection.execute(
            "DELETE FROM posts WHERE owner=? ", (flask.session["login"],)
        )
        flask.session.clear()
        if not flask.request.args.get("target"):
            return flask.redirect(flask.url_for("show_index"))
        return flask.redirect(flask.request.args.get("target"))


@insta485.app.route("/users/<username>/following/", methods=["GET"])
def user_following(username):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?", (username,)
    )
    print(username)
    following = cur.fetchall()

    for f in following:
        print(f)
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (f["username2"],)
        )
        filename = cur.fetchone()["filename"]
        f["filename"] = filename
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? and username2=?",
            (flask.session["login"], f["username2"]),
        )
        follows = cur.fetchall()
        logname_follows_username = True if len(follows) else False
        f["logname_follows_username"] = logname_follows_username
        print(f["logname_follows_username"])
    print(following)
    context = {
        "following": following,
        "logname": flask.session["login"],
        "username": username,
        "current_page": flask.request.path,
    }
    return flask.render_template("following.html", **context)


@insta485.app.route("/users/<username>/followers/", methods=["GET"])
def user_followers(username):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username1 FROM following WHERE username2=?", (username,)
    )
    print(username)
    following = cur.fetchall()

    for f in following:
        print(f)
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (f["username1"],)
        )
        filename = cur.fetchone()["filename"]
        f["filename"] = filename
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? and username2=?",
            (flask.session["login"], f["username1"]),
        )
        follows = cur.fetchall()
        logname_follows_username = True if len(follows) else False
        f["logname_follows_username"] = logname_follows_username
        print(f["logname_follows_username"])
    print(following)
    context = {
        "following": following,
        "logname": flask.session["login"],
        "username": username,
        "current_page": flask.request.path,
    }
    return flask.render_template("followers.html", **context)


@insta485.app.route("/explore/", methods=["GET"])
def explore():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("show_index"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?",
        (flask.session["login"],),
    )

    f = cur.fetchall()
    following = [follower["username2"] for follower in f]
    cur = connection.execute("SELECT username FROM users")
    u = cur.fetchall()

    users = [user["username"] for user in u]
    print(users)
    print(following)
    not_following = []
    for u in users:
        if (u not in following) and u != flask.session["login"]:
            cur = connection.execute(
                "SELECT filename, username FROM users WHERE username=?", (u,)
            )
            z = cur.fetchone()
            not_following.append(
                {"username": z["username"], "filename": z["filename"]}
            )
    context = {
        "not_following": not_following,
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("explore.html", **context)


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    flask.session.clear()
    return flask.redirect("/accounts/login/")


@insta485.app.route("/accounts/edit/", methods=["GET"])
def account_edit():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (flask.session["login"],)
    )
    user = cur.fetchone()
    context = {
        "user": user,
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("edit.html", **context)


@insta485.app.route("/accounts/create/", methods=["GET"])
def account_create():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" in flask.session:
        return flask.redirect(flask.url_for("account_edit"))
    return flask.render_template("create.html", context={})


@insta485.app.route("/accounts/password/", methods=["GET"])
def account_password():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    context = {
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("account_password.html", **context)


@insta485.app.route("/accounts/delete/", methods=["GET"])
def account_delete():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        return flask.redirect(flask.url_for("login_get"))
    context = {
        "logname": flask.session["login"],
        "current_page": flask.request.path,
    }
    return flask.render_template("delete.html", **context)


@insta485.app.route("/likes/", methods=["POST"])
def likes_post():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes WHERE owner=? and postid=?",
        (flask.session["login"], flask.request.form["postid"]),
    )
    like = cur.fetchall()
    if flask.request.form["operation"] == "like":
        # check for like already
        if len(like) != 0:
            print(len(like))
            print(like)
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes(owner, postid) VALUES(?, ?)",
            (flask.session["login"], flask.request.form["postid"]),
        )
        if flask.request.args.get("target") == "/":
            return flask.redirect(flask.url_for("show_index"))
        return flask.redirect(flask.request.args.get("target"))
    else:

        if len(like) == 0:
            print(len(like))
            print("her")
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE owner=? and postid=?",
            (flask.session["login"], flask.request.form["postid"]),
        )
        if flask.request.args.get("target") == "/":
            print("correct")
            print(flask.request.args.get("target"))
            return flask.redirect(flask.url_for("show_index"))
        else:
            print(flask.request.args.get("target"))
            return flask.redirect(flask.request.args.get("target"))


@insta485.app.route("/comments/", methods=["POST"])
def comments_post():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if flask.request.form["operation"] == "create":
        if flask.request.form["text"] == "":
            flask.abort(400)
        else:
            connection = insta485.model.get_db()
            connection.execute(
                "INSERT INTO comments(owner, postid, text) VALUES (?, ?, ?)",
                (
                    flask.session["login"],
                    flask.request.form["postid"],
                    flask.request.form["text"],
                ),
            )
            # if flask.request.args.get("target") == "":
            #     return flask.redirect(flask.url_for("show_index"))
            # else:
            #     print("redirecting incorrectly")
            #     print(flask.request.args.get("target"))
            #     return flask.redirect(flask.request.args.get("target"))
            if not flask.request.args.get("target"):
                return flask.redirect(flask.url_for("show_index"))
            return flask.redirect(flask.request.args.get("target"))
    else:
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT owner FROM comments WHERE commentid=?",
            (flask.request.form["commentid"]),
        )
        owner = cur.fetchone()["owner"]
        if flask.session["login"] != owner:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments WHERE commentid=?",
            (flask.request.form["commentid"]),
        )
        if not flask.request.args.get("target"):
            return flask.redirect(flask.url_for("show_index"))
        return flask.redirect(flask.request.args.get("target"))


@insta485.app.route("/following/", methods=["POST"])
def follow_post():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(*) as count "
        "FROM following WHERE username1=? and username2=?",
        (flask.session["login"], flask.request.form["username"]),
    )
    count = cur.fetchone()["count"]
    print(flask.request.form["username"])
    if flask.request.form["operation"] == "follow":

        if count > 0:
            flask.abort(409)
        else:
            print(flask.session["login"])
            print("following")
            print(flask.request.form["username"])
            connection.execute(
                "INSERT INTO following(username1, username2) VALUES (?, ?)",
                (flask.session["login"], flask.request.form["username"]),
            )
            return flask.redirect(flask.request.args.get("target"))
    else:

        if count == 0:
            flask.abort(409)
        else:
            connection.execute(
                "DELETE FROM following WHERE username1=? and username2=?",
                (flask.session["login"], flask.request.form["username"]),
            )
            print(flask.request.args.get("target"))
            return flask.redirect(flask.request.args.get("target"))


@insta485.app.route("/posts/", methods=["POST"])
def post_post():
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if flask.request.form["operation"] == "delete":
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT * FROM posts WHERE postid=?",
            (flask.request.form["postid"]),
        )
        post = cur.fetchone()
        owner = post["owner"]
        old_filename = post["filename"]
        if flask.session["login"] != owner:
            flask.abort(403)
        connection.execute(
            "DELETE FROM posts WHERE postid=?", (flask.request.form["postid"])
        )

        os.remove(insta485.app.config["UPLOAD_FOLDER"] / old_filename)
        if not flask.request.args.get("target"):
            return flask.redirect(f"/users/{flask.session['login']}/")
        else:
            return flask.redirect(flask.request.args.get("target"))
    else:
        if flask.request.files["file"].filename == "":
            flask.abort(400)

        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_basename = f"{stem}{suffix}"
        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
        fileobj.save(path)
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES(?, ?)",
            (uuid_basename, flask.session["login"]),
        )
        print(flask.request.args.get("target"))
        if not flask.request.args.get("target"):
            return flask.redirect(f"/users/{flask.session['login']}/")
        else:
            return flask.redirect(flask.request.args.get("target"))


@insta485.app.route("/uploads/<filename>", methods=["GET"])
def serve_image(filename):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    if "login" not in flask.session:
        flask.abort(403)

    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"], filename
    )
