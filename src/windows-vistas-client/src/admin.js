import axios from "axios";
import "./import-jquery";

// default host should be location of window
// let HOST = window.location.origin
let HOST = 'http://beefcake.local:5000'
// Add trailing slash if it's not there already
if (HOST.slice(-1) !== "/") {
    HOST += "/"
}
const SETTINGS_URL = `${HOST}settings`
const SETTINGS_EDITOR = document.getElementById('settings-editor')
const UPDATE_SETTINGS_BUTTON = document.getElementById('update-settings')

UPDATE_SETTINGS_BUTTON.addEventListener('click', () => {
    try {
        const data = JSON.parse(SETTINGS_EDITOR.value)
        axios.post(SETTINGS_URL, data).then(response => {
            alert(response.data.status)
            getSettings()
        })
    } catch (e) {
        alert(e)
    }
})

function getSettings() {
    axios.get(SETTINGS_URL).then((response) => {
        console.log(response)
        SETTINGS_EDITOR.innerHTML = JSON.stringify(response.data, null, 4)
    })
}

$(document).ready(function() {
    console.log('lol', SETTINGS_URL)
    // Get settings from settings endpoint
    getSettings()
});
