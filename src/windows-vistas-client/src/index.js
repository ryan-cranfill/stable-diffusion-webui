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

const queryParams = decodeURI(window.location.search)
                  .replace('?', '')
                  .split('&')
                  .map(param => param.split('='))
                  .reduce((values, [ key, value ]) => {
                    values[ key ] = value
                    return values
                  }, {})

// Disable zooming on mobile devices
document.addEventListener('touchmove', function (event) {
  if (event.scale !== 1) { event.preventDefault(); }
}, false);

var lastTouchEnd = 0;
document.addEventListener('touchend', function (event) {
  var now = (new Date()).getTime();
  if (now - lastTouchEnd <= 300) {
    event.preventDefault();
  }
  lastTouchEnd = now;
}, false);

import axios from "axios";
import p5 from 'p5';
import "./import-jquery";
import select2 from "./lib/select2.min";
// import {gridSketch} from "./gridz";
import {gridSketch} from "./grid-subdivide";
import {backgroundChoices, subjectChoices} from "./choices";

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
let HOST = serverUrl || window.location.origin
// Add trailing slash if it's not there already
if (HOST.slice(-1) !== "/") {
  HOST += "/"
}
console.log('Server URL is:', serverUrl, 'Host URL is:', HOST)

// Tell server I received the code
const code = queryParams.code
if (code) {
    axios.get(`${HOST}received_code/${code}`)
}

// axios.get('http://localhost:8000/pass').then((response) =>{
//   document.getElementById('passcodeInput').setAttribute('value', response.data.passcode)
// })
const resetButton = document.getElementById('resetButton')
resetButton.addEventListener('click', () => {
  interactiveSketch.resetSketch();
})

const minTimeBetweenSubmissions = 1000 * 60 * 1 // 1 minutes
function getLastSubmissionTime() {
  // Look in local cookies for last submission time
    let lastSubmissionTime = localStorage.getItem('windowVistasLastSubmissionTime')
    if (lastSubmissionTime) {
        lastSubmissionTime = parseInt(lastSubmissionTime)
    } else {
        lastSubmissionTime = 0
    }
    return lastSubmissionTime
}

function setLastSubmissionTime() {
    localStorage.setItem('windowVistasLastSubmissionTime', Date.now())
}

// const minDistanceFromWindow = 500 // meters
//
// function getDistanceFromLatLonInM(lat1,lon1,lat2,lon2) {
//     var R = 6371; // Radius of the earth in km
//     var dLat = deg2rad(lat2-lat1);  // deg2rad below
//     var dLon = deg2rad(lon2-lon1);
//     var a =
//         Math.sin(dLat/2) * Math.sin(dLat/2) +
//         Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
//         Math.sin(dLon/2) * Math.sin(dLon/2)
//         ;
//     var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
//     var d = R * c; // Distance in km
//     return d * 1000;
// }
//
// const agencyLat = 41.9607952273792,
//     agencyLon = -87.72299139718032;
//
// function deg2rad(deg) {
//     return deg * (Math.PI/180)
// }
// function checkGeolocationCloseEnough() {
//     if (navigator.geolocation) {
//         return navigator.geolocation.getCurrentPosition((position) => {
//             console.log('position', position)
//             const lat = position.coords.latitude
//             const lon = position.coords.longitude
//             const distance = getDistanceFromLatLonInM(lat, lon, agencyLat, agencyLon)
//             return distance < minDistanceFromWindow;
//         }, (error) => {
//             console.log('error', error)
//             return false;
//         })
//     } else {
//         // Geolocation is not supported by this browser.
//         return false
//     }
// }

document.getElementById('changeColorsButton').addEventListener('click', () => {
  interactiveSketch.randomizeColors();
})

const saveButton = document.getElementById('saveButton')
saveButton.addEventListener('click', () => {
    console.log('save button clicked')
    if (Date.now() - getLastSubmissionTime() < minTimeBetweenSubmissions) {
        alert('You have already submitted a window recently. Please wait a bit before submitting again.')
        return
    }
    // if (!checkGeolocationCloseEnough()) {
    //     alert('You must be within 500 meters of the windows to submit.')
    //     return
    // }
    // Disable save button
    saveButton.disabled = true;
    resetButton.disabled = true;

    // get p5 pixels then post to server
    let imageBase64String = interactiveSketch.saveTemp();
    const url = `${HOST}process_img2img`
    console.log(url)
    const data = {image: imageBase64String, code: queryParams.code}
    const for_screen = parseInt(queryParams.screen)
    if (for_screen) {
        data.for_screen = for_screen
    }
    // axios.post(url, {image: imageBase64String, prompt: prompt, for_screen}
    axios.post(url, data).then(response => {
        const changes = response.data
        console.log(changes)
        saveButton.disabled = false;
        resetButton.disabled = false;
        if (changes.success === true) {
            alert('Success! Your stained glass will appear shortly :-D')
            setLastSubmissionTime()
        } else {
            alert('Uh oh! Something went wrong, please wait a few seconds and try again. If the error persists, try scanning the code again.')
        }
    }).catch(reason => {
        console.log(reason)
        alert('Uh oh! Something went wrong, please wait a few seconds and try again. If the error persists, try scanning the code again.')
        saveButton.disabled = false;
        resetButton.disabled = false;
    })
})

$(document).ready(function() {
  // select2($);
  // const subjectSelect = $('#subject-select');
  // subjectSelect.select2({data: subjectChoices});
  // subjectSelect.on('select2:select', function (e) {
  //   const data = e.params.data;
  //   console.log(data);
  // });
});

