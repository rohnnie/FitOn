var selectedExercises = [];

function downloadCSV() {
    // Initialize CSV content with header row
    var csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Name,Level,Equipment,Primary Muscles,Secondary Muscles,Instructions\r\n";

    // Select all elements with class "selected-card"
    var exerciseCards = document.querySelectorAll(".selected-card");

    // Loop through each exercise card
    exerciseCards.forEach(function(card) {
        // Extract data from HTML elements
        var name = card.querySelector(".exercise-details h3").innerText.trim();
        var level = card.querySelector(".exercise-details p:nth-of-type(1)").textContent.replace("Level:", "").trim();
        var equipment = card.querySelector(".exercise-details p:nth-of-type(2)").textContent.replace("Equipment:", "").trim();
        var primaryMuscles = card.querySelector(".exercise-details p:nth-of-type(3)").textContent.replace("Primary Muscles:", "").trim();
        var secondaryMuscles = card.querySelector(".exercise-details p:nth-of-type(4)").textContent.replace("Secondary Muscles:", "").trim();
        var instructions = card.getAttribute("data-instructions");

        // Format the data
        var row = [
            name,
            level,
            equipment,
            '"' + primaryMuscles.replace(/"/g, '""') + '"', // Enclose in double quotes and escape double quotes within
            '"' + secondaryMuscles.replace(/"/g, '""') + '"',
            '"' + instructions.replace(/"/g, '""') + '"'
        ].join(",");

        // Append the row to CSV content
        csvContent += row + "\r\n";
    });

    // Create a temporary link and trigger download
    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "exercises.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function getFilterString() {
    var filters = document.getElementById("filter-fieldset").getElementsByClassName("custom-select");
    filter_url = "";
    for(let i = 0; i < filters.length; ++i) {
      let element = filters[i];
      filter_url += "&";
      filter_url += element.name;
      filter_url += "=";
      filter_url += element.value;
    }
  
    search_name = document.getElementById("search-form").elements[0].name
    search_value = document.getElementById("search-form").elements[0].value;
    filter_url += `&${search_name}=${search_value}`

    for(var i=0; i < selectedExercises.length; i++) {
        filter_url += "&exercise=" + encodeURIComponent(selectedExercises[i]);
    }
  
    return filter_url
  }

function handleFilterChange() {
    var filter_form = document.getElementById("filter-form");
    var search_form = document.getElementById("search-form");
    if(filter_form.checkValidity() && search_form.checkValidity()) {
        const baseURL = window.location.origin+window.location.pathname;
        url = "?page=1";
        filters = getFilterString();
        url += filters;
        window.location.href = baseURL+url;
    }

    return false;
}

function getPageUrl(page) {
    const baseURL = window.location.origin+window.location.pathname;
    url = `?page=${page}`;
    filters = getFilterString();
    url += filters;

    window.location.href = baseURL+url;
    return false;
}

document.addEventListener("DOMContentLoaded", function() {

    document.getElementById("exercise_name").value = filter_dict.name;

    var selectElement = document.getElementById("exercise_muscle");
    var options = selectElement.options;
    for (var i = 0; i < options.length; i++) {
        if (options[i].value === filter_dict.muscle) {
            options[i].selected = true;
            break;
        }
    }

    var selectElement = document.getElementById("exercise_level");
    var options = selectElement.options;
    for (var i = 0; i < options.length; i++) {
        if (options[i].value === filter_dict.level) {
            options[i].selected = true;
            break;
        }
    }

    var selectElement = document.getElementById("exercise_equipment");
    var options = selectElement.options;
    for (var i = 0; i < options.length; i++) {
        if (options[i].value === filter_dict.equipment) {
            options[i].selected = true;
            break;
        }
    }

    var selectElement = document.getElementById("exercise_category");
    var options = selectElement.options;
    for (var i = 0; i < options.length; i++) {
        if (options[i].value === filter_dict.category) {
            options[i].selected = true;
            break;
        }
    }

    document.getElementById('filter-form').addEventListener('change', function(event) {
        handleFilterChange()
    }, false);

    document.getElementById("selected_ex_container").style.height = document.getElementById("display_ex_container").offsetHeight + 170;

    function removeExercise(id) {
        var index = selectedExercises.indexOf(id);
        if (index !== -1) {
            selectedExercises.splice(index, 1);
        }
        var parentDiv = document.getElementById("selected_ex_container");
        parentDiv.removeChild(document.getElementById(`selected_exercise_${id}`));
    }

    function addExercise(exercise_bt) {
        var mainDiv = document.createElement("div");
        mainDiv.classList.add("selected-card", "mx-2");
        mainDiv.setAttribute("data-id", exercise_bt.getAttribute("data-id"));
        mainDiv.setAttribute("data-instructions", exercise_bt.getAttribute("data-instructions"));
        mainDiv.id = `selected_exercise_${exercise_bt.getAttribute("data-id")}`;

        var exerciseDetailsDiv = document.createElement("div");
        exerciseDetailsDiv.classList.add("exercise-details");

        var exerciseNameHeading = document.createElement("h3");
        exerciseNameHeading.classList.add("mb-4");
        exerciseNameHeading.innerHTML = `<strong>${exercise_bt.getAttribute("data-name")}</strong>`;
        exerciseDetailsDiv.appendChild(exerciseNameHeading);

        var levelParagraph = document.createElement("p");
        levelParagraph.innerHTML = `<strong>Level: </strong> ${exercise_bt.getAttribute("data-level")}`;
        exerciseDetailsDiv.appendChild(levelParagraph);

        var equipmentParagraph = document.createElement("p");
        equipmentParagraph.innerHTML = `<strong>Equipment: </strong> ${exercise_bt.getAttribute("data-equipment")}`;
        exerciseDetailsDiv.appendChild(equipmentParagraph);

        var primaryMusclesParagraph = document.createElement("p");
        primaryMusclesParagraph.innerHTML = `<strong>Primary Muscles: </strong> ${exercise_bt.getAttribute("data-primary")}`;
        exerciseDetailsDiv.appendChild(primaryMusclesParagraph);

        var secondaryMusclesParagraph = document.createElement("p");
        secondaryMusclesParagraph.innerHTML = `<strong>Secondary Muscles: </strong> ${exercise_bt.getAttribute("data-seconday")}`;
        exerciseDetailsDiv.appendChild(secondaryMusclesParagraph);

        // Append exercise details div to the main div
        mainDiv.appendChild(exerciseDetailsDiv);

        // Create and append the remove button
        var removeButton = document.createElement("button");
        removeButton.classList.add("remove_selected");
        removeButton.textContent = "X";
        removeButton.addEventListener("click", function() {
            removeExercise(exercise_bt.getAttribute("data-id"));
        });
        mainDiv.appendChild(removeButton);

        // Get a reference to the parent div where you want to append the new content
        var parentDiv = document.getElementById("selected_ex_container");

        // Append the main div to the parent div
        parentDiv.appendChild(mainDiv);
    }

    var buttons = document.querySelectorAll(".add_to_selected");

    buttons.forEach(function(button) {
        button.addEventListener("click", function() {
            selectedExercises.push(this.getAttribute("data-id"));
            addExercise(this);
        });
    });

    var cross = document.querySelectorAll(".remove_selected");

    cross.forEach(function(button) {
        selectedExercises.push(button.getAttribute("data-id"));
        button.addEventListener("click", function() {
            removeExercise(this);
        });
    });

    document.getElementById("download_exercises").addEventListener("click", function() {
        downloadCSV();
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            url: '/exercise/store/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({data_list: selectedExercises}),
            beforeSend: function(xhr, settings) {
                // Include CSRF token in request headers
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response){
                // Handle success response
                console.log(response);
            },
            error: function(xhr, status, error){
                console.error(error);
            }
        });
    })

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Check if cookie name matches csrfmiddlewaretoken
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

});

