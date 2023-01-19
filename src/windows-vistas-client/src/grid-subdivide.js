let saveCanvas;
const targetWidth = 512
const targetHeight = 512

// Grid
let widMod = 1
let lenMod = 1
let rectInfo = [];
let rectInfoMap = new Map();
let lastRectTouched = null;
// size of the padding between grid and sketch borders
const padding = 0;
// number of rows and columns of the grid
const rows = 8;
const columns = 12;
const gridDivsX = rows * widMod;
const gridDivsY = columns * lenMod;
// actual spacing between grid points
let gridSpacingX, gridSpacingY;
let wx, wy;

// here we populate the 2d boolean array
let bools = [];


let cellColors = []
let shapeColor;
let isTouching = false;
let lastCellTouched = [null, null];


const sketchDiv = document.getElementById('interactiveMount')

export const gridSketch = (p) => {
  p.setup = () => {
    console.log('lol')
    wx = sketchDiv.offsetWidth
    wy = sketchDiv.offsetHeight
    p.createCanvas(wx, wy);

    // actual spacing between grid points
    gridSpacingX = (wx - padding*2)/gridDivsX;
    gridSpacingY = (wy - padding*2)/gridDivsY;

    constructGeometry();
    p.background(0);
    p.stroke(0)
    p.strokeWeight(2);
    p.noFill()
    drawGrid()
    markEmptySpots()

    createMetaTag()
    // p.createCanvas(w, h);
    // p.createCanvas(sketchDiv.offsetWidth, sketchDiv.offsetHeight);
    // p.createCanvas(window.innerWidth, window.innerHeight);
    saveCanvas = p.createGraphics(targetWidth, targetHeight);
    // randomizeCellColors()
  }

  function constructGeometry() {
    bools = [];
    for(let x = 0; x<gridDivsX; x++){
      let column = [];
      for(let y = 0; y<gridDivsY; y++){
        column.push(1);
      }
      bools.push(column);
    }

    rectInfo = [];
    rectInfoMap = new Map();
    for(let x = 0; x<gridDivsX; x++){
        rectInfoMap[x] = new Map();
        for(let y = 0; y<gridDivsY; y++){
          rectInfoMap[x][y] = null;
        }
    }
    // constructIrregularGrid([2,3,4,5,6,7,8], [2,3,4,5,6,7,8]);
    constructIrregularGrid([1,2,2,3,3,4], [1,2,2,3,3,4]);
    constructIrregularGrid([1,1,2], [1,2,3]);
    constructIrregularGrid([1], [1]);
  }

  function MakeRect(posX, posY, dimX, dimY){
    this.posX = posX;
    this.posY = posY;
    this.dimX = dimX;
    this.dimY = dimY;
    this.color = randomColor();
    this.id = `${posX},${posY},${dimX},${dimY}`;
  }

  function constructIrregularGrid(sizesArrX, sizesArrY){
    for(let x = 0; x<gridDivsX-p.max(sizesArrX)+1; x++){
      for(let y = 0; y<gridDivsY-p.max(sizesArrY)+1; y++){

        let xdim = p.random(sizesArrX)
        let ydim = p.random(sizesArrY)

        let fits = true

        // check if within bounds
        if(x + xdim > gridDivsX || y + ydim > gridDivsY){
          fits = false
        }

        // check if rectangle overlaps with any other rectangle
        if(fits){
          for(let xc = x; xc < x + xdim; xc++){
            for(let yc = y; yc < y + ydim; yc++){
              if(bools[xc][yc] === false){
                fits = false
              }
            }
          }
        }

        if(fits){
          // Make the rectangle
          let rect = new MakeRect(x, y, xdim, ydim)
          // mark area as occupied
          for(let xc = x; xc < x + xdim; xc++){
            for(let yc = y; yc < y + ydim; yc++){
              bools[xc][yc] = false
              rectInfoMap[xc][yc] = rect
            }
          }
          // add to array
          rectInfo.push(rect)
        }
      }
    }
  }

  function drawGrid(){
    for(let n = 0; n<rectInfo.length; n++){
      const r = rectInfo[n]
      p.stroke(0)
      p.fill(r.color)
      p.rect(r.posX * gridSpacingX + padding, r.posY * gridSpacingY + padding,
            r.dimX * gridSpacingX, r.dimY * gridSpacingY)
    }
  }

  function markEmptySpots(){
    for(let x = 0; x<gridDivsX; x++){
      for(let y = 0; y<gridDivsY; y++){
        if(bools[x][y]){
          p.point(x * gridSpacingX + gridSpacingX/2 + padding,
                y * gridSpacingY + gridSpacingY/2 + padding)
        }
      }
    }
  }

  p.windowResized = () => {
    wx = sketchDiv.offsetWidth
    wy = sketchDiv.offsetHeight
    gridSpacingX = (wx - padding*2)/gridDivsX;
    gridSpacingY = (wy - padding*2)/gridDivsY;
    p.resizeCanvas(wx, wy);
  }

  p.draw = () => {
    if (
      p.mouseX > 0 && p.mouseX < p.width &&
      p.mouseY > 0 && p.mouseY < p.height &&
      (p.mouseIsPressed === true || isTouching === true)
    ) {
      const mouseR = p.floor(gridDivsY * (p.mouseY / p.height));
      const mouseC = p.floor(gridDivsX * (p.mouseX / p.width));
      // Change shapeColor when a new cell is touched
      const rectTouched = rectInfoMap[mouseC][mouseR]
      if (lastRectTouched === null && rectTouched !== null) {
        lastRectTouched = rectTouched;
        rectTouched.color = shapeColor;
        shapeColor = randomColor()
      }
      else if (rectTouched !== null && rectTouched.id !== lastRectTouched.id) {
          shapeColor = randomColor()
          rectTouched.color = shapeColor
          lastRectTouched = rectTouched
      }
    }


    drawGrid()
    if (isTouching) {
      p.fill(30, 255, 255);
      p.ellipse(p.mouseX, p.mouseY, 30, 30);
    }
  }

  p.mousePressed = () => {
    shapeColor = randomColor()
  }

  p.mouseReleased = () => {
    lastRectTouched = null
  }

  p.touchStarted = () => {
    isTouching = true;
    shapeColor = randomColor()
  }

  p.touchEnded = () => {
    isTouching = false;
    lastRectTouched = null;
  }

  p.touchMoved = () => {
    // prevent the display from moving around when you touch it
    return false;
  }

  p.saveTemp = () => {
    let c = p.get(0, 0, p.width, p.height);
    saveCanvas.image(c, 0, 0, targetWidth, targetHeight);
    return saveCanvas.canvas.toDataURL();
  }

  p.resetSketch = () => {
    // randomizeCellColors()
    constructGeometry()
  }

  p.randomizeColors = () => {
    randomizeCellColors()
  }

  p.setBackground = (data) => {
    if (data.isSolid) {
      p.background(data.color);
    } else {
      const src = `/backgrounds/${data.src}`;
      p.loadImage(src, (img) => {
        p.image(img, 0, 0)
      });
    }
  }

  function randomizeCellColors() {
    for (let r of rectInfo) {
      r.color = randomColor()
    }
  }

  function randomColor() {
    let minColor = 50;
    let maxColor = 255;
    return p.color(p.random(minColor, maxColor), p.random(minColor, maxColor), p.random(minColor, maxColor))
  }

  function createMetaTag() {
    // let meta = p.createElement('meta');
    // meta.attribute('name', 'viewport');
    // meta.attribute('content', 'user-scalable=no,initial-scale=1,maximum-scale=1,minimum-scale=1,width=device-width,height=device-height');
    //
    // let head = p.select('head');
    // meta.parent(head);
  }
}
