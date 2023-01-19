// import "./styles.css";
if (module.hot) {
  module.hot.accept(() => {
    const parent = document.getElementById('interactiveMount');
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
    interactiveSketch = new p5(gridSketch, 'interactiveMount');
  });
}

import axios from "axios";
import p5 from 'p5';
import "./import-jquery";
import select2 from "./lib/select2.min";
// import {gridSketch} from "./gridz";
import {gridSketch} from "./grid-subdivide";
import {backgroundChoices, subjectChoices} from "./choices";

console.log('Server URL is:', serverUrl)

let interactiveSketch = new p5(gridSketch, 'interactiveMount');

let openInfoModalButton = document.getElementById("whatisthis");
let modal = document.getElementById("info-modal");
let closeInfoModalButton = document.getElementById("ok-btn");
// We want the modal to open when the Open button is clicked
openInfoModalButton.onclick = function() {
  modal.style.display = "block";
}
// We want the modal to close when the OK button is clicked
closeInfoModalButton.onclick = function() {
  modal.style.display = "none";
}
// The modal will close when the user clicks anywhere outside the modal
window.onclick = function(event) {
  if (event.target === modal) {
      modal.style.display = "none";
  }
}

// default host should be location of window
let HOST = window.location.origin
// Add trailing slash if it's not there already
if (HOST.slice(-1) !== "/") {
  HOST += "/"
}

// helper function: generate a new file from base64 String
const dataURLtoFile = (dataurl, filename) => {
  const arr = dataurl.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n) {
    u8arr[n - 1] = bstr.charCodeAt(n - 1)
    n -= 1 // to make eslint happy
  }
  return new File([u8arr], filename, { type: mime })
}

// axios.get('http://localhost:8000/pass').then((response) =>{
//   document.getElementById('passcodeInput').setAttribute('value', response.data.passcode)
// })
const resetButton = document.getElementById('resetButton')
resetButton.addEventListener('click', () => {
  interactiveSketch.resetSketch();
})

document.getElementById('changeColorsButton').addEventListener('click', () => {
  interactiveSketch.randomizeColors();
})

const saveButton = document.getElementById('saveButton')
saveButton.addEventListener('click', () => {
  console.log('save button clicked')
  // Disable save button
  saveButton.disabled = true;
  resetButton.disabled = true;

  // get p5 pixels then post to server
  let imageBase64String = interactiveSketch.saveTemp();
  // const prompt = document.getElementById('promptInput').value
  // let prompt = document.getElementById('subject-select').value
  // prompt = `a beautiful intricate ornate ((stained glass window)) of (((${prompt}))) high quality flickr`
  // const denoisingStrength = document.getElementById('denoising-range').value / 100
  // const passcode = document.getElementById('passcodeInput').value
  const url = `${HOST}process_img2img`
  console.log(url)
  const queryParams = decodeURI(window.location.search)
                      .replace('?', '')
                      .split('&')
                      .map(param => param.split('='))
                      .reduce((values, [ key, value ]) => {
                        values[ key ] = value
                        return values
                      }, {})
  const for_screen = parseInt(queryParams.screen) || 0
  // axios.post(url, {image: imageBase64String, prompt: prompt, for_screen}
  axios.post(url, {image: imageBase64String, for_screen}).then(response => {
    const changes = response.data
    console.log(changes)
    saveButton.disabled = false;
    resetButton.disabled = false;
    alert('Success! Your stained glass will appear shortly :-D')
  }).catch(reason => {
    console.log(reason)
    alert('Uh oh! Something went wrong, please try again. If the error persists, try refreshing.')
    saveButton.disabled = false;
    resetButton.disabled = false;
  })
})

$(document).ready(function() {
  select2($);
  const subjectSelect = $('#subject-select');
  subjectSelect.select2({data: subjectChoices});
  subjectSelect.on('select2:select', function (e) {
    const data = e.params.data;
    console.log(data);
  });
});

