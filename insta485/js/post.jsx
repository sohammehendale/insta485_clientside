import React from "react";
import moment from "moment";
import PropTypes from "prop-types";
import Likes from "./likes";
import User from "./user";
import Image from "./image";
import Comments from "./comments";

class Post extends React.Component {
    /* Display image and post owner of a single post
     */
    constructor(props) {
        // Initialize mutable state
        super(props);
        this.state = {
            imgUrl: "",
            owner: "",
            comments: [],
            created: "",
            likes: {},
            commentsUrl: "",
            ownerImgUrl: "",
            ownerShowUrl: "",
            postShowUrl: "",
            postid: 0,
            url: "",
            newCommentText: "",
        };
        this.deleteComment = this.deleteComment.bind(this);
        this.submitComment = this.submitComment.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.createLike = this.createLike.bind(this);
        this.deleteLike = this.deleteLike.bind(this);
        this.doubleLike = this.doubleLike.bind(this);
    }

    componentDidMount() {
        // This line automatically assigns this.props.url to the const variable url
        const { url } = this.props;
        // Call REST API to get the post's information
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                this.setState({
                    imgUrl: data.imgUrl,
                    owner: data.owner,
                    comments: data.comments,
                    created: data.created,
                    likes: data.likes,
                    commentsUrl: data.commentsUrl,
                    ownerImgUrl: data.ownerImgUrl,
                    ownerShowUrl: data.ownerShowUrl,
                    postShowUrl: data.postShowUrl,
                    postid: data.postid,
                    url: data.url,
                });
            })
            .catch((error) => console.log(error));
    }

    handleChange(event) {
        const { newCommentText } = this.state;
        console.log(event.target.value);
        this.setState({ newCommentText: event.target.value });
        console.log(newCommentText);
    }

    submitComment(event) {
        const { newCommentText, postid, comments } = this.state;

        console.log(JSON.stringify({ text: newCommentText }));
        console.log(postid)
        fetch(`/api/v1/comments/?postid=${postid}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: JSON.stringify({ text: newCommentText }),
        })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                console.log(data);
                const newComment = data;
                const newComments = comments;
                newComments.push(newComment);
                this.setState((prevState) => ({
                    imgUrl: prevState.imgUrl,
                    owner: prevState.owner,
                    comments: newComments,
                    created: prevState.created,
                    likes: prevState.likes,
                    commentsUrl: prevState.commentsUrl,
                    ownerImgUrl: prevState.ownerImgUrl,
                    ownerShowUrl: prevState.ownerShowUrl,
                    postShowUrl: prevState.postShowUrl,
                    postid: prevState.postid,
                    url: prevState.url,
                    newCommentText: prevState.newCommentText,
                }));
                console.log(this.state);
            })
            .catch((error) => console.log(error));
        event.preventDefault();
    }

    deleteComment(commentid) {
        const { comments } = this.state;
        fetch(`/api/v1/comments/${commentid}/`, { method: "DELETE" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                console.log(`Deleted comment ${commentid}`);
                const { url } = this.props;
                console.log(url);
                // I am pretty sure it has to do with this it is doing one fetch righr after the other and with asynch programming, this wont work
                // fetch(url, { credentials: "same-origin" })
                //     .then((response) => {
                //         if (!response.ok) throw Error(response.statusText);
                //         return response.json();
                //     })
                //     .then((data) => {

                // const array = ["one", "two", "three"]
                // array.forEach(function (item, index) {
                //     console.log(item, index);
                // });
                const newComments = comments;
                newComments.forEach((item, index) => {
                    if (item.commentid === commentid) {
                        newComments.splice(index, 1);
                    }
                });

                this.setState((prevState) => ({
                    imgUrl: prevState.imgUrl,
                    owner: prevState.owner,
                    comments: newComments,
                    created: prevState.created,
                    likes: prevState.likes,
                    commentsUrl: prevState.commentsUrl,
                    ownerImgUrl: prevState.ownerImgUrl,
                    ownerShowUrl: prevState.ownerShowUrl,
                    postShowUrl: prevState.postShowUrl,
                    postid: prevState.postid,
                    url: prevState.url,
                }));
            })
            .catch((error) => console.log(error));
    }

    createLike() {
        const { postid, likes } = this.state;
        fetch(`/api/v1/likes/?postid=${postid}`, { method: "POST" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                const newLikes = likes;
                newLikes.lognameLikesThis = true;
                newLikes.numLikes = likes.numLikes + 1;
                newLikes.url = data.url;

                this.setState((prevState) => ({
                    imgUrl: prevState.imgUrl,
                    owner: prevState.owner,
                    comments: prevState.comments,
                    created: prevState.created,
                    likes: newLikes,
                    commentsUrl: prevState.commentsUrl,
                    ownerImgUrl: prevState.ownerImgUrl,
                    ownerShowUrl: prevState.ownerShowUrl,
                    postShowUrl: prevState.postShowUrl,
                    postid: prevState.postid,
                    url: prevState.url,
                }));
            })
            .catch((error) => console.log(error));
    }

    deleteLike(likeid) {
        const { likes } = this.state;
        fetch(`/api/v1/likes/${likeid}/`, { method: "DELETE" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);

                const newLikes = likes;
                newLikes.lognameLikesThis = false;
                newLikes.numLikes = likes.numLikes - 1;
                newLikes.url = null;

                this.setState((prevState) => ({
                    imgUrl: prevState.imgUrl,
                    owner: prevState.owner,
                    comments: prevState.comments,
                    created: prevState.created,
                    likes: newLikes,
                    commentsUrl: prevState.commentsUrl,
                    ownerImgUrl: prevState.ownerImgUrl,
                    ownerShowUrl: prevState.ownerShowUrl,
                    postShowUrl: prevState.postShowUrl,
                    postid: prevState.postid,
                    url: prevState.url,
                }));
            })
            .catch((error) => console.log(error));
    }

    doubleLike() {
        const { likes, postid } = this.state;
        if (likes.lognameLikesThis) {
            return;
        }
        fetch(`/api/v1/likes/?postid=${postid}`, { method: "POST" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                const newLikes = likes;
                newLikes.lognameLikesThis = true;
                newLikes.numLikes = likes.numLikes + 1;
                newLikes.url = data.url;

                this.setState((prevState) => ({
                    imgUrl: prevState.imgUrl,
                    owner: prevState.owner,
                    comments: prevState.comments,
                    created: prevState.created,
                    likes: newLikes,
                    commentsUrl: prevState.commentsUrl,
                    ownerImgUrl: prevState.ownerImgUrl,
                    ownerShowUrl: prevState.ownerShowUrl,
                    postShowUrl: prevState.postShowUrl,
                    postid: prevState.postid,
                    url: prevState.url,
                }));
            })
            .catch((error) => console.log(error));
        // }
    }

    render() {
        console.log("render()");
        // This line automatically assigns this.state.imgUrl to the const variable imgUrl
        // and this.state.owner to the const variable owner
        const {
            imgUrl,
            owner,
            comments,
            created,
            likes,
            commentsUrl,
            ownerImgUrl,
            ownerShowUrl,
            postShowUrl,
        } = this.state;
        // 2022-10-12 16:10:37
        console.log(created)
        const timestamp = moment(created, "YYYY-MM-DD hh:mm:ss").fromNow();
        // Render post image and post owner
        // use map function, passing event handlers to children components for comments
        // moment(created, "YYYY-MM-DD hh:mm:ss").fromNow()
        return (
            <div className="post">
                <User
                    owner={owner}
                    ownerImgUrl={ownerImgUrl}
                    ownerShowUrl={ownerShowUrl}
                />
                <Image imgUrl={imgUrl} doubleLike={this.doubleLike} />
                <a href={postShowUrl}>{timestamp}</a>
                <Likes
                    likes={likes}
                    createLike={this.createLike}
                    deleteLike={this.deleteLike}
                />
                <Comments
                    comments={comments}
                    comments_url={commentsUrl}
                    deleteComment={this.deleteComment}
                />
                <form className="comment-form" onSubmit={this.submitComment}>
                    <input type="text" onChange={this.handleChange} />
                </form>
            </div>
        );
    }
}

Post.propTypes = {
    url: PropTypes.string.isRequired,
};
export default Post;
