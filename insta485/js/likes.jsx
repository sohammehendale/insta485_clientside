import React from "react";
import PropTypes from "prop-types";

class Likes extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const { likes, createLike, deleteLike } = this.props;
    let likePlural = "";
    if (likes.numLikes === 1) {
      likePlural = " like";
    } else {
      likePlural = " likes";
    }

    let button = (
      <div>
        <button
          className="like-unlike-button"
          type="button"
          onClick={() => createLike()}
        >
          like
        </button>
      </div>
    );
    if (likes.lognameLikesThis) {
      button = (
        <div>
          <button
            className="like-unlike-button"
            type="button"
            onClick={() => deleteLike(likes.url[14])}
          >
            unlike
          </button>
        </div>
      );
    }

    return (
      <div>
        {likes.numLikes} {likePlural} {button}{" "}
      </div>
    );
  }
}

Likes.propTypes = {
  likes: PropTypes.shape({
    lognameLikesThis: PropTypes.bool,
    numLikes: PropTypes.number,
    url: PropTypes.string,
  }),
  createLike: PropTypes.func.isRequired,
  deleteLike: PropTypes.func.isRequired,
};

Likes.defaultProps = {
  likes: [],
};

export default Likes;
