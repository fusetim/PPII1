let postsData = "";
const postsContainer = document.querySelector(".posts-container");
const searchDisplay = document.querySelector(".search-display");

fetch(
  "/static/js_admin_add.json"
).then(async (response) => {
  postsData = await response.json();
  postsData.map((post) => createPost(post));
});

const createPost = (postData) => {
  const { name, code } = postData;
  const post = document.createElement("div");
  post.className = "post";
  post.innerHTML = `
      <div class="post-content">
        <p class="post-title">${name}</p>
      </div>
  `;

  postsContainer.append(post);
};

const handleSearchPosts = (query) => {
  const searchQuery = query.trim().toLowerCase();
  
  if (searchQuery.length <= 1) {
    resetPosts()
    return
  }
  
  let searchResults = [...postsData].filter(
    (post) =>
      post.categories.some((category) => category.toLowerCase().includes(searchQuery)) ||
      post.title.toLowerCase().includes(searchQuery)
  );
  
  if (searchResults.length == 0) {
    searchDisplay.innerHTML = "No results found"
  } else if (searchResults.length == 1) {
    searchDisplay.innerHTML = `1 result found for your query: ${query}`
  } else {
    searchDisplay.innerHTML = `${searchResults.length} results found for your query: ${query}`
  }

  postsContainer.innerHTML = "";
  searchResults.map((post) => createPost(post));
};

const resetPosts = () => {
  searchDisplay.innerHTML = ""
  postsContainer.innerHTML = "";
  postsData.map((post) => createPost(post));
};

const search = document.getElementById("search");

let debounceTimer;
const debounce = (callback, time) => {
  window.clearTimeout(debounceTimer);
  debounceTimer = window.setTimeout(callback, time);
};

search.addEventListener(
  "input",
  (event) => {
    const query = event.target.value;
    debounce(() => handleSearchPosts(query), 500);
  },
  false
);
