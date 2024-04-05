import React from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

class Feed extends React.Component {
  /* Display image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { posts: [], next: "", hasMore: true };
    this.fetchData = this.fetchData.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    console.log("componentDidMount()");
    const { url } = this.props;
    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        let newHasMore = true;
        if (data.next === "") {
          newHasMore = false;
        }
        this.setState({
          posts: data.results,
          next: data.next,
          hasMore: newHasMore,
        });
      })
      .catch((error) => console.log(error));
  }

  fetchData() {
    const { next, posts } = this.state;
    fetch(next, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(data);
        let newHasMore = true;
        if (data.next === "") {
          newHasMore = false;
        }
        console.log(posts.concat(data.results));
        this.setState({
          posts: posts.concat(data.results),
          next: data.next,
          hasMore: newHasMore,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { posts, hasMore } = this.state;
    return (
      <div className="scroll">
        <InfiniteScroll
          dataLength={posts.length}
          next={this.fetchData}
          hasMore={hasMore}
          loader={<p>Loading...</p>}
        >
          {posts.map((post) => (
            <Post url={post.url} key={post.postid} />
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
