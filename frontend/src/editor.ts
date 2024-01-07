//  ===  DOM Selectors  ===
const editor_form = document.getElementById("editor-form") as HTMLFormElement;
const msg_group = document.getElementById("msg-group") as HTMLElement;
const add_ingredient_chip = document.getElementById("add-ingredient-chip") as HTMLElement;
const ingredients = document.getElementById("ingredients") as HTMLElement;
const ingredient_suggestions = document.getElementById("ingredient-suggestions") as HTMLElement;
const tags = document.getElementById("tags") as HTMLElement;
const tags_suggestions = document.getElementById("tags-suggestions") as HTMLElement;
const tag_input = document.getElementById("tag-input") as HTMLInputElement;
const preview_btn = document.getElementById("preview-btn") as HTMLInputElement;
const save_btn = document.getElementById("save-btn") as HTMLInputElement;

const ingredient_popover = {
    element: document.getElementById("add-ingredient-popover") as HTMLElement,
    name_input: document.getElementsByName("ingredient_name")[0] as HTMLInputElement,
    display_name_input: document.getElementsByName("ingredient_display_name")[0] as HTMLInputElement,
    quantity_input: document.getElementsByName("ingredient_quantity")[0] as HTMLInputElement,
    unit_input: document.getElementsByName("ingredient_unit")[0] as HTMLSelectElement,
    reference_quantity_input: document.getElementsByName("ingredient_reference_quantity")[0] as HTMLInputElement,
    add_btn: document.getElementById("ingredient-add") as HTMLInputElement,
    cancel_btn: document.getElementById("ingredient-cancel") as HTMLInputElement,
};

const MESSAGE_TIMEOUT = 10000; // 10 seconds

//  ===  Event Handlers  ===

// On click, the add chip should open the popover if it's closed, and close it if it's open
add_ingredient_chip.addEventListener("click", () => {
    ingredient_popover.element.classList.toggle("open");
    ingredient_popover.name_input.focus();
});

// When the focus is lost, close the popover
ingredient_popover.element.addEventListener("focusout", (evt) => {
    // Check if the focus is lost to an element outside the popover, if so, close it.
    if (evt.relatedTarget != null && evt.relatedTarget.closest("#add-ingredient-popover") != ingredient_popover.element) {
        ingredient_popover.element.classList.remove("open");
    }
});


// Display the ingredient suggestions when the name input is focused and at least one character
// is entered.
ingredient_popover.name_input.addEventListener("input", () => {
    if (ingredient_popover.name_input.value.length > 0) {
        ingredient_suggestions.classList.remove("hidden");
        searchIngredient(ingredient_popover.name_input.value).then((ingredients) => {
            // Clear the precedent suggestions
            ingredient_suggestions.innerHTML = "";
            // Create the new suggestions
            for (let ingredient of ingredients) {
                let sugg = document.createElement("p");
                sugg.classList.add("suggestion");
                sugg.setAttribute("data-ingr-code", ingredient.code);
                sugg.textContent = ingredient.name ?? ingredient.code;
                ingredient_suggestions.appendChild(sugg);
                sugg.addEventListener("click", () => {
                    ingredient_popover.name_input.value = sugg.textContent ?? "";
                    ingredient_popover.name_input.setAttribute("data-ingr-code", sugg.getAttribute("data-ingr-code") ?? "");
                    ingredient_popover.display_name_input.value = sugg.textContent ?? "";
                    ingredient_suggestions.classList.add("hidden");
                });
            }
        });
    } else {
        ingredient_suggestions.classList.add("hidden");
    }
    // On change, update the display name input
    ingredient_popover.display_name_input.value = ingredient_popover.name_input.value;
});

// Hide the ingredient suggestions when the name input is not focused anymore
// Except if the focus is lost on a suggestion, in which case the suggestion should
// be selected.
ingredient_popover.name_input.addEventListener("focusout", (evt) => {
    if (evt.relatedTarget == null || evt.relatedTarget.closest("#ingredient-suggestions") == ingredient_suggestions) {
        return;
    }
    ingredient_suggestions.classList.add("hidden");
});


// Handling the action of the add button in the ingredient popover
ingredient_popover.add_btn.addEventListener("click", (evt) => {
    // Prevent the click event from bubbling up to the form
    evt.preventDefault();
    // Perform validation
    if (ingredient_popover.name_input.getAttribute("data-ingr-code") == null || ingredient_popover.name_input.getAttribute("data-ingr-code") == "") {
        ingredient_popover.name_input.setCustomValidity("Veuillez sélectionner un ingrédient dans la liste.");
        ingredient_popover.name_input.reportValidity();
        return;
    }
    if (ingredient_popover.display_name_input.value == "") {
        ingredient_popover.display_name_input.setCustomValidity("Veuillez entrer un nom d'affichage.");
        ingredient_popover.name_input.reportValidity();
        return;
    }
    if (ingredient_popover.quantity_input.value == "") {
        ingredient_popover.quantity_input.setCustomValidity("Veuillez entrer une quantité.");
        ingredient_popover.name_input.reportValidity();
        return;
    }
    if (ingredient_popover.reference_quantity_input.value == "") {
        let mass_equivalent = +(ingredient_popover.unit_input.selectedOptions[0].getAttribute("data-mass-equivalent") ?? 0);
        if (mass_equivalent == null || mass_equivalent == 0) {
            ingredient_popover.reference_quantity_input.setCustomValidity("Veuillez entrer une quantité de référence.");
            ingredient_popover.name_input.reportValidity();
            return;
        }
    }
    // Remove previous validation errors
    ingredient_popover.name_input.setCustomValidity("");
    ingredient_popover.display_name_input.setCustomValidity("");
    ingredient_popover.quantity_input.setCustomValidity("");
    ingredient_popover.reference_quantity_input.setCustomValidity("");
    
    // Close the popover
    ingredient_popover.element.classList.remove("open");
    // Create the new chip
    const chip = document.createElement("p");
    chip.classList.add("chip", "clickable-chip");
    chip.setAttribute("data-name", ingredient_popover.name_input.value);
    chip.setAttribute("data-ingr-code", ingredient_popover.name_input.getAttribute("data-ingr-code") ?? "");
    chip.setAttribute("data-display-name", ingredient_popover.display_name_input.value);
    chip.setAttribute("data-quantity", ingredient_popover.quantity_input.value);
    chip.setAttribute("data-quantity-type", ingredient_popover.unit_input.value);
    chip.setAttribute("data-reference-quantity", ingredient_popover.reference_quantity_input.value);
    chip.innerHTML = `
        <span class="name">${ingredient_popover.display_name_input.value}</span>
        <span class="quantity">${ingredient_popover.quantity_input.value}</span>
        <span class="unit">${ingredient_popover.unit_input.selectedOptions[0].innerText}</span>
    `;
    // Add the chip to the list
    ingredients.insertBefore(chip, add_ingredient_chip);
    // Clear the inputs
    ingredient_popover.name_input.value = "";
    ingredient_popover.display_name_input.value = "";
    ingredient_popover.quantity_input.value = "";
    ingredient_popover.reference_quantity_input.value = "";
    // Add the event handlers to the new chip
    ingredientChipAddEventHandlers(chip);
});

// Handling the action of the cancel button in the ingredient popover
ingredient_popover.cancel_btn.addEventListener("click", (evt) => {
    // Close the popover
    ingredient_popover.element.classList.remove("open");
    // Clear the inputs
    ingredient_popover.name_input.value = "";
    ingredient_popover.display_name_input.value = "";
    ingredient_popover.quantity_input.value = "";
    ingredient_popover.reference_quantity_input.value = "";
    // Prevent the click event from bubbling up to the form
    evt.preventDefault();
});

// Handling the action of the tag input
tag_input.addEventListener("input", (evt) => {
    if (tag_input.value.length > 0) {
        tags_suggestions.classList.remove("hidden");
        // If the user entered a comma, it means they want to add the tag
        if (evt instanceof InputEvent && evt.data?.includes(",")) {
            // Create the new chip
            const chip = document.createElement("p");
            chip.classList.add("chip");
            chip.setAttribute("data-tag-uid", "TODO");
            let stext = tag_input.value.split(",");
            if (stext[0].length >= 1) {
                chip.textContent = stext[0].trim();
                // Add the chip to the list
                tags.insertBefore(chip, tag_input);
            }
            // Clear the input
            tag_input.value = stext[1] ?? "";
        }
    } else {
        tags_suggestions.classList.add("hidden");
    }
});

// Handling keypress in the tag input
tag_input.addEventListener("keydown", (evt) => {
    if (evt.isComposing || evt.keyCode === 229) {
        return;
    }
    // Delete the last chip if the user pressed backspace and the input is empty
    if (evt.key === "Backspace" && tag_input.value.length == 0 && tags.children.length > 2) {
        tags.children[tags.children.length - 3].remove();
    }
    // If the user pressed enter, just ignore it
    if (evt.key === "Enter") {
        evt.preventDefault();
    }
});

// Hide the tag suggestions when the tag input is not focused anymore
// Except if the focus is lost on a suggestion, in which case the suggestion should
// be selected.
tag_input.addEventListener("focusout", (evt) => {
    if (evt.relatedTarget == null || evt.relatedTarget.closest("#tags-suggestions") == tags_suggestions) {
        return;
    }
    tags_suggestions.classList.add("hidden");
});

// Retrieve the quantity types from the server
retrieveQuantityTypes().then((quantity_types) => {
    ingredient_popover.unit_input.replaceChildren();
    for (let quantity_type of Object.values(quantity_types)) {
        let option = document.createElement("option");
        option.value = quantity_type.quantity_type_uid;
        option.setAttribute("data-mass-equivalent", quantity_type.mass_equivalent.toString());
        option.textContent = quantity_type.unit;
        ingredient_popover.unit_input.appendChild(option);
    }
});

// When the user changes the quantity type, update the reference quantity input
ingredient_popover.unit_input.addEventListener("change", updateReferenceQuantity);

// When the user changes the quantity, update the reference quantity input.
ingredient_popover.quantity_input.addEventListener("input", updateReferenceQuantity);

// Prevent the form from being submitted
// We want to handle ourself the submission of the form.
editor_form.addEventListener("submit", (evt) => {
    evt.preventDefault();
});

// == Handling event on the buttons ==
preview_btn.addEventListener("click", () => {
    let recipe = getData();
    saveRecipe(recipe).then((recipe_uid) => {
        let recipe_uid_input = (document.getElementById("recipe-uid") as HTMLInputElement);
        recipe_uid_input.value = recipe_uid;
        window.location.href = `/recipe/${recipe_uid}`;
    }, (err) => {
        console.error(err);
        let msg = createMessage("Erreur lors de la sauvegarde de la recette.", (err as Error).message, true);
        msg_group.appendChild(msg);
        autoTimeoutMessage(msg);
        return null;
    });
});

save_btn.addEventListener("click", () => {
    let recipe = getData();
    saveRecipe(recipe).then((recipe_uid) => {
        let recipe_uid_input = (document.getElementById("recipe-uid") as HTMLInputElement);
        recipe_uid_input.value = recipe_uid;
        let msg = createMessage("Recette sauvegardée !", null, false);
        msg_group.appendChild(msg);
        autoTimeoutMessage(msg);
        resetIllustration();
    }, (err) => {
        console.error(err);
        let msg = createMessage("Erreur lors de la sauvegarde de la recette.", (err as Error).message, true);
        msg_group.appendChild(msg);
        autoTimeoutMessage(msg);
        return null;
    });
});

//  === Event Handlers for pre-rendered elements ===
// When the user clicks on an ingredient chip, open the popover with the ingredient's data to 
// edit them.
for (let chip of ingredients?.children ?? []) {
    if (chip == add_ingredient_chip) continue;
    ingredientChipAddEventHandlers(chip as HTMLElement);
}

// TEMPORARY: Handling the click on a tag suggestion
for (let sugg of tags_suggestions?.children ?? []) {
    sugg.addEventListener("click", () => {
        // Create the new chip
        const chip = document.createElement("p");
        chip.classList.add("chip");
        chip.setAttribute("data-tag-uid", "TODO");
        chip.textContent = sugg.textContent ?? "";
        // Add the chip to the list
        tags.insertBefore(chip, tag_input);
        // Clear the input & hide the suggestions
        tag_input.value = "";
        tags_suggestions.classList.add("hidden");
    });
}

//  === Type definitions ===

// Ingredient type
interface Ingredient {
    code: string;
    name: string;
};

// IngredientLink type
interface IngredientLink {
    ingr_code: string;
    display_name: string | null;
    quantity: number;
    quantity_type: string;
    reference_quantity: number | null;
};

// Recipe type
interface Recipe {
    recipe_uid: string | null;
    title: string;
    short_description: string;
    preparation_time: number;
    description: string;
    ingredients: IngredientLink[];
    tags: string[];
    illustration: File | null;
};

// Recipe request type
interface RecipeRequest {
    // If recipe_uid is null, it means we want to create a new recipe
    recipe_uid: string | null;
    title: string;
    short_description: string;
    preparation_time: number;
    description: string;
    ingredients: IngredientLink[];
    tags: string[];
    illustration_uid: string | null;
};

// Upload type
interface Upload {
    cid: string;
    upload_uid: string;
    url: string;
};

// Quantity type
interface QuantityType {
    quantity_type_uid: string;
    name: string;
    unit: string;
    mass_equivalent: number | null;
};

//  ===  Functions  ===

// Add the event handlers to a chip
function ingredientChipAddEventHandlers(chip: HTMLElement) {
    chip.addEventListener("click", () => {
        ingredient_popover.name_input.value = chip.getAttribute("data-name") ?? "";
        ingredient_popover.name_input.setAttribute("data-ingr-code", chip.getAttribute("data-ingr-code") ?? "");
        ingredient_popover.display_name_input.value = chip.getAttribute("data-display-name") ?? "";
        ingredient_popover.quantity_input.value = chip.getAttribute("data-quantity") ?? "";
        ingredient_popover.unit_input.value = chip.getAttribute("data-quantity-type") ?? "";
        ingredient_popover.reference_quantity_input.value = chip.getAttribute("data-reference-quantity") ?? "";
        ingredient_popover.element?.classList.add("open");
        chip.remove();
    });
}

// Handle the retrieval of all the information from the form
function getData(): Recipe {
    let ingredients: IngredientLink[] = [];
    let tags: string[] = [];
    let illustration = null;
    for (let chip of document.querySelectorAll("#ingredients > .chip")) {
        if (chip == add_ingredient_chip) continue;
        ingredients.push({
            ingr_code: chip.getAttribute("data-ingr-code") ?? "",
            display_name: chip.getAttribute("data-display-name") ?? "",
            quantity: +(chip.getAttribute("data-quantity") ?? "0") as number,
            quantity_type: chip.getAttribute("data-quantity-type") ?? "",
            reference_quantity: chip.getAttribute("data-reference-quantity") == null ? +chip.getAttribute("data-reference-quantity") : null,
        });
    }
    // TODO: Implement the real tag system
    let illustration_input = document.getElementById("illustration") as HTMLInputElement;
    if (illustration_input.files != null && illustration_input.files.length >= 1) {
        illustration = illustration_input.files[0];
    }

    let recipe_uid_input = (document.getElementById("recipe-uid") as HTMLInputElement);

    let recipe: Recipe = {
        recipe_uid: recipe_uid_input.value == "" ? null : recipe_uid_input.value,
        title: (document.getElementById("title") as HTMLInputElement).value,
        short_description: (document.getElementById("short_description") as HTMLInputElement).value,
        preparation_time: +(document.getElementById("preparation_time") as HTMLInputElement).value,
        description: (document.getElementById("steps") as HTMLTextAreaElement).value,
        ingredients: ingredients,
        tags: tags,
        illustration: illustration,
    };

    return recipe;
}

// Handle the upload of the illustration
function uploadIllustration(file: File): Promise<Upload> {
    let formData = new FormData();
    formData.append("file", file);
    return fetch("/api/uploads/add", {
        method: "POST",
        body: formData,
        credentials: "same-origin",
    }).then(async (res) => {
        if (res.ok) {
            return await res.json();
        } else {
            throw new Error((await res.json())["error"]);
        }
    });
}

// Handle the saving of the recipe
async function saveRecipe(recipe: Recipe): Promise<string> {
    let illustration_uid = null;
    if (recipe.illustration != null) {
        try {
            let upload = await uploadIllustration(recipe.illustration);
            illustration_uid = upload.upload_uid;
        }
        catch (err) {
            console.error(err);
            let msg = createMessage("Erreur lors de l'upload de l'illustration.", (err as Error).message, true);
            msg_group.appendChild(msg);
            autoTimeoutMessage(msg);
        }
    }
    let recipeRequest: RecipeRequest = {
        recipe_uid: recipe.recipe_uid,
        title: recipe.title,
        short_description: recipe.short_description,
        preparation_time: recipe.preparation_time,
        description: recipe.description,
        ingredients: recipe.ingredients,
        tags: recipe.tags,
        illustration_uid: illustration_uid,
    };

    let endpoint = recipeRequest.recipe_uid == null ? "/api/recipes/add" : "/api/recipes/edit";
    let method = recipeRequest.recipe_uid == null ? "POST" : "PATCH";

    return await fetch(endpoint, {
        method: method,
        body: JSON.stringify(recipeRequest),
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "same-origin",
    }).then((res) => {
        if (res.ok) {
            return res.json();
        } else {
            throw new Error("Error while saving the recipe");
        }
    }).then((data) => {
        return data.recipe_uid;
    });
}

// Search an ingredient by its name
function searchIngredient(name: string): Promise<Ingredient[]> {
    return fetch(`/api/ingredients/search/${encodeURIComponent(name)}`, {
        method: "GET",
        credentials: "omit",
    }).then((res) => {
        if (res.ok) {
            return res.json() as Promise<Ingredient[]>;
        } else {
            throw new Error("Error while searching for the ingredient");
        }
    });
}

// Create a message element
function createMessage(message: string, context: string | null, is_error: boolean): HTMLElement {
    let msg = document.createElement("div");
    msg.classList.add("message");
    if (is_error) {
        msg.classList.add("error");
    }
    let p = document.createElement("p");
    p.textContent = message;
    msg.appendChild(p);
    if (context != null) {
        let p2 = document.createElement("p");
        p2.textContent = context;
        msg.appendChild(p2);
    }
    return msg;
}

// Automatically remove a message after MESSAGE_TIMEOUT milliseconds
function autoTimeoutMessage(msg: HTMLElement) {
    setTimeout(() => {
        msg.remove();
    }, MESSAGE_TIMEOUT);
}

// Reset the illustration file input
// This is mostly used to clear the input after the illustration has been uploaded
// and the recipe saved. We don't need to re-upload the illustration if the user
// have not changed it.
function resetIllustration() {
    let illustration_input = document.getElementById("illustration") as HTMLInputElement;
    illustration_input.value = "";
}

// Retrieve the quantity types from the server
async function retrieveQuantityTypes(): Promise<QuantityType> {
    return await fetch("/api/recipes/all_quantities", {
        method: "GET",
        credentials: "omit",
    }).then((res) => {
        if (res.ok) {
            return res.json() as Promise<QuantityType>;
        } else {
            throw new Error("Error while retrieving the quantity types");
        }
    });
}

function updateReferenceQuantity() {
    let option = ingredient_popover.unit_input.selectedOptions[0];
    let mass_equivalent = option.getAttribute("data-mass-equivalent");
    if (mass_equivalent != null && mass_equivalent != "" && +mass_equivalent != 0) {
        ingredient_popover.reference_quantity_input.value = (+mass_equivalent * +ingredient_popover.quantity_input.value).toString();
    } else {
        ingredient_popover.reference_quantity_input.value = "";
    }
}