import React from "react";
import PropTypes from "prop-types";

class Image extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {};
  }

  render() {
    const { imgUrl, doubleLike } = this.props;
    return (
      <div className="Image">
        <button type="button" onDoubleClick={() => doubleLike()}>
          <img src={imgUrl} alt="" width="500" height="350" />
        </button>
      </div>
    );
  }
}
Image.propTypes = {
  imgUrl: PropTypes.string.isRequired,
  doubleLike: PropTypes.func.isRequired,
};

export default Image;
