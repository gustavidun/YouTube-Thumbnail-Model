root = "http://127.0.0.1:8000/"

cur_item = 0
dataset_size = 299
cur_thumbnail = null

async function useFetch(endpoint, options){
    const url = root + endpoint;
    
    try {
        console.log("Calling endpoint " + endpoint);
        const res = await fetch(url, options);
        if (!res.ok) {
            throw new Error(`${res.status}`);
        }
        const data = await res.json();
        console.log("Data received:", data);
        return { data, error: null };
    } catch (error) {
        console.error("Error:", error);
        return { data: null, error };
    }
}

function set_thumbnail(index, thumbnail){
    console.log(JSON.stringify(thumbnail))
    options = {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify(thumbnail)
    } 
    useFetch("items/" + index, options).then((thumbnail) => {
        console.log("Thumbnail written.")
    })  
}

function get_thumbnail(index){
    if (index < 0 || index > dataset_size){
        console.log("Outside bounds.")
        return
    }
    img = document.getElementById("thumbnail")
    labels = {
        "question": document.getElementById("question"),
        "text": document.getElementById("text"),
        "conflict": document.getElementById("conflict"),
        "arrows": document.getElementById("arrows"),
        "monochrony": document.getElementById("monochrony"),
        "juxtaposition": document.getElementById("juxtaposition"),
        "cliffhanger": document.getElementById("cliffhanger"),
        "faces": document.getElementById("faces"),
    }
    if (cur_thumbnail != null){
        for (let key of Object.keys(labels)) {
            if (key == "faces"){
                cur_thumbnail[key] = labels[key].value
            }
            else {
                cur_thumbnail[key] = labels[key].checked
            }
        } 
        cur_thumbnail.reviewed = true
    }
    useFetch("items/" + index, {}).then((thumbnail) => {
        // set new thumbnail
        if (cur_thumbnail != null){ 
            set_thumbnail(cur_item, cur_thumbnail)
        }
        cur_thumbnail = thumbnail.data
        cur_item = index
        // update labels to new thumbnail
        for (let key of Object.keys(thumbnail.data)) {
            if (labels.hasOwnProperty(key)) {
                if (key == "faces"){
                    const selectElement = labels[key]; // Assuming labels["faces"] corresponds to the <select> element
                    const faceValue = thumbnail.data[key];
                    console.log(`Setting dropdown value for faces: ${faceValue}`);
                    
                    // Find the matching option in the select element
                    let optionIndex = -1;
                    for (let i = 0; i < selectElement.options.length; i++) {
                        if (selectElement.options[i].value === faceValue) {
                            optionIndex = i;
                            break;
                        }
                    }
                    
                    // If a valid option is found, update the custom dropdown
                    if (optionIndex !== -1) {
                        // Set the selected index of the select element
                        selectElement.selectedIndex = optionIndex;
                        
                        // Update the custom dropdown's displayed selected option
                        const selectedDiv = selectElement.parentNode.querySelector('.select-selected');
                        selectedDiv.innerHTML = selectElement.options[optionIndex].innerHTML;
                
                        // Ensure the custom dropdown reflects the change
                        const optionDivs = selectElement.parentNode.querySelectorAll('.select-items div');
                        optionDivs.forEach((optionDiv, idx) => {
                            if (idx === optionIndex) {
                                optionDiv.classList.add("same-as-selected");
                            } else {
                                optionDiv.classList.remove("same-as-selected");
                            }
                        });
                    } else {
                        console.warn(`Invalid value for faces: ${faceValue}, setting to "none"`);
                        selectElement.selectedIndex = 0; // Default to "none"
                    }
                }
                else {
                    labels[key].checked = thumbnail.data[key]
                }
            }
        } 
        img.src = thumbnail.data.url 
    })
}

get_thumbnail(cur_item)



