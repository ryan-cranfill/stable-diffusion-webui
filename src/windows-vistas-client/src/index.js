// import "./styles.css";
import axios from "axios";
import p5 from 'p5';
import { io } from "socket.io-client";
import "./import-jquery";
import select2 from "./lib/select2.min";
import {Draggable} from "./draggable";
import {pollockSketch} from "./pollockSketch";
import {OutputSketch} from "./outputSketch";
import {clickyShapySketch} from "./clickyShapy";
import {backgroundChoices} from "./choices";

const interactiveSketch = new p5(clickyShapySketch, 'interactiveMount');
const outputSketch = new p5(OutputSketch, 'outputMount');

const socket = io();

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

axios.get('http://localhost:8000/pass').then((response) =>{
  document.getElementById('passcodeInput').setAttribute('value', response.data.passcode)
})

document.getElementById('resetButton').addEventListener('click', () => {
  interactiveSketch.resetSketch();
  // outputSketch.reset();
})

const saveButton = document.getElementById('saveButton')
saveButton.addEventListener('click', () => {
  console.log('save button clicked')
  outputSketch.toggleWaiting()
  // get p5 pixels then post to server
  let imageBase64String = interactiveSketch.saveTemp();
  // generate file from base64 string
  const file = dataURLtoFile(imageBase64String)
  const formData = new FormData();
  const prompt = document.getElementById('promptInput').value
  const denoisingStrength = document.getElementById('denoising-range').value / 100
  const passcode = document.getElementById('passcodeInput').value

  // formData.append("file", file);
  // formData.append("prompt", prompt);
  // formData.append('passcode', passcode)
  // formData.append("denoising_strength", denoisingStrength);
  // console.log(formData)
  // axios.post('http://localhost:5000/process_img2img', formData, {
  //   headers: {
  //     'Content-Type': 'multipart/form-data'
  //   }
  // }
  axios.post('http://localhost:5000/process_img2img', {image: imageBase64String, prompt: prompt, for_screen: 0}
  ).then(response => {
    const images = response.data.images
    if (!images) {
      return
    }

    for (const imgStr of images) {
      outputSketch.loadImage(imgStr, img => {
        outputSketch.image(img, 0, 0)
      })
    }
    outputSketch.toggleWaiting()
  })
})

$(document).ready(function() {
  select2($);
  const backgroundSelect = $('#backgroundSelect');
  backgroundSelect.select2({data: backgroundChoices});
  backgroundSelect.on('select2:select', function (e) {
    const data = e.params.data;
    console.log(data);
    interactiveSketch.setBackground(data);
  });
});

