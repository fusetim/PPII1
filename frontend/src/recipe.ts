import "normalize-css/normalize.js";

// Selectors
const edit_btn = document.querySelector("#action-edit");
const delete_btn = document.querySelector("#action-delete");

// Event Listeners
if (edit_btn !== null) {
    edit_btn.addEventListener("click", editRecipe);
}

if (delete_btn !== null) {
    delete_btn.addEventListener("click", deleteRecipe);
}

// Functions
function editRecipe() {
    // Get recipe_uid from URL
    let recipe_uid = window.location.pathname.split("/").pop();
    // Redirect to editor page
    window.location.href = "/editor?recipe_uid=" + recipe_uid;
}

function deleteRecipe() {
    // Get recipe_uid from URL
    let recipe_uid = window.location.pathname.split("/").pop();
    // Send DELETE request to backend
    fetch("/api/recipes/delete", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            recipe_uid: recipe_uid
        })
    }).then(response => {
        if (response.ok) {
            // Redirect to homepage
            window.location.href = "/";
        } else {
            // Show error message
            alert("Echec: impossible de supprimer la recette.");
        }
    });
}