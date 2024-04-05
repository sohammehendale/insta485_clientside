import React from "react";
import PropTypes from "prop-types";

class Comments extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {};
  }

  render() {
    const { comments, deleteComment } = this.props;
    return (
      <div className="comments">
        {comments.map((comment) =>
          comment.lognameOwnsThis ? (
            <div key={comment.commentid}>
              <a href={comment.ownerShowUrl} style={{ display: "inline" }}>
                {comment.owner}
              </a>
              <p style={{ display: "inline" }}>{comment.text}</p>
              <button
                className="delete-comment-button"
                type="button"
                onClick={() => deleteComment(comment.commentid)}
              >
                Delete Comment
              </button>
            </div>
          ) : (
            <div key={comment.commentid}>
              <a href={comment.ownerShowUrl} style={{ display: "inline" }}>
                {comment.owner}
              </a>
              <p style={{ display: "inline" }}>{comment.text}</p>
            </div>
          )
        )}

        {/* {comments.map(({ commentid, text, lognameOwnsThis }) => (
            <div>
                <p>{lognameOwnsThis}</p>
                <p>{text}</p>
            </div>
        ))} */}
      </div>
    );
  }
}
// "commentid": 1,
//       "lognameOwnsThis": true,
//       "owner": "awdeorio",
//       "ownerShowUrl": "/users/awdeorio/",
//       "text": "#chickensofinstagram",
//       "url": "/api/v1/comments/1/"
Comments.propTypes = {
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      owner: PropTypes.string.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    })
  ),
  // commentsUrl: PropTypes.string.isRequired,
  deleteComment: PropTypes.func.isRequired,
};

Comments.defaultProps = {
  comments: [],
};

export default Comments;
