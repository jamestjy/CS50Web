document.addEventListener("DOMContentLoaded", function() {
    const csrftoken = document.getElementById("csrf-token").value;

    const editButton = document.getElementById("edit-post-button");
    if (editButton) {
        editButton.addEventListener("click", function() {
            const postContent = document.getElementById("post-content");
            const originalContent = postContent.innerText;

            // Create a textarea for editing
            const editTextarea = document.createElement("textarea");
            editTextarea.id = "edit-post-textarea";
            editTextarea.value = originalContent;
            editTextarea.style.width = "100%";
            editTextarea.style.height = "150px";
            postContent.replaceWith(editTextarea);
            editButton.style.display = "none"; // hide edit button

            // create save button
            const saveButton = document.createElement("button");
            saveButton.id = "save-post-button";
            saveButton.innerText = "Save";
            editTextarea.after(saveButton); // .after() adds new element right after original element

            // create a cancel button
            const cancelButton = document.createElement("button");
            cancelButton.id = "cancel-edit-button";
            cancelButton.innerText = "Cancel";
            saveButton.after(cancelButton);

            saveButton.addEventListener("click", function() {
                const updatedContent = editTextarea.value;
                const postId = editButton.dataset.postId;

                // Send the updated content to the server via fetch
                fetch(`/edit/${postId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({ content: updatedContent })
                })
                .then(response => response.json())
                .then(data => {
                    // replace textarea with updated content
                    if (data.error) {
                        console.error(data.error);
                        alert("Error updating post");

                        // keep edit mode active
                        editTextarea.value = data.current_content;

                    } else {
                        const newContent = document.createElement("p");
                        newContent.id = "post-content";
                        newContent.innerText = updatedContent;
                        editTextarea.replaceWith(newContent);
                        saveButton.remove();
                        cancelButton.remove();
                        editButton.style.display = "inline"; // show edit button again
                    }  
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("An error occurred while updating the post.");
                });
            });

            cancelButton.addEventListener("click", function() {
                // Restore original content
                editTextarea.replaceWith(postContent);
                saveButton.remove();
                cancelButton.remove();
                editButton.style.display = "inline"; // show edit button again
            });
        }); 
    }
});


