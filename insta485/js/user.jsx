import React from "react";
import PropTypes from "prop-types";

class User extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {};
  }

  render() {
    const { owner, ownerImgUrl, ownerShowUrl } = this.props;
    return (
      <div className="user">
        <img src={ownerImgUrl} alt="" width="40" height="40" />
        <a href={ownerShowUrl}>
          <b>{owner}</b>
        </a>
      </div>
    );
  }
}

User.propTypes = {
  owner: PropTypes.string.isRequired,
  ownerImgUrl: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
};

export default User;
