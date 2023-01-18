if (module.hot) {
  module.hot.accept();
}

import axios from "axios";
import "./import-jquery";

// default host should be location of window
let HOST = window.location.origin
// let HOST = 'http://beefcake.local:5000'
// Add trailing slash if it's not there already
if (HOST.slice(-1) !== "/") {
    HOST += "/"
}
const SETTINGS_URL = `${HOST}settings`
const SETTINGS_EDITOR = document.getElementById('settings-editor')
const UPDATE_SETTINGS_BUTTON = document.getElementById('update-settings')
const SAVE_SETTINGS_BUTTON = document.getElementById('save-settings')
const LOAD_SETTINGS_BUTTON = document.getElementById('load-settings')
const IMAGE_CONTAINER = document.getElementById('images-container')

UPDATE_SETTINGS_BUTTON.addEventListener('click', () => {
    try {
        const data = JSON.parse(SETTINGS_EDITOR.value)
        axios.post(SETTINGS_URL, data).then(async response => {
            await getSettings()
            alert(response.data.status)
        })
    } catch (e) {
        alert(e)
    }
})

SAVE_SETTINGS_BUTTON.addEventListener('click', () => {
    try {
        axios.get(`${HOST}save_settings`).then(response => {
            alert(response.data.status)
        })
    } catch (e) {
        alert(e)
    }
})

LOAD_SETTINGS_BUTTON.addEventListener('click', () => {
    try {
        axios.get(`${HOST}load_settings`).then(async response => {
            await getSettings()
            alert(response.data.status)
        })
    } catch (e) {
        alert(e)
    }
})

async function getSettings() {
    return axios.get(SETTINGS_URL).then((response) => {
        console.log(response)
        SETTINGS_EDITOR.innerHTML = JSON.stringify(response.data, null, 4)
        return response.data
    })
}

$(document).ready(async function() {
    console.log('lol', SETTINGS_URL)
    // Get settings from settings endpoint
    const settings = await getSettings()
    console.log(settings)
    for (let i=0; i<settings.other_settings.num_screens; i++) {
        const imgContainer = document.createElement('div')
        imgContainer.classList.add('flex')
        imgContainer.classList.add('w-3/4')
        imgContainer.classList.add('mx-6')
        const inImgElement = document.createElement('img')
        inImgElement.src = `${HOST}input_img/${i}`
        imgContainer.appendChild(inImgElement)

        const outImgElement = document.createElement('img')
        outImgElement.src = `${HOST}output_img/${i}`
        imgContainer.appendChild(outImgElement)
        IMAGE_CONTAINER.appendChild(imgContainer)
    }
});
