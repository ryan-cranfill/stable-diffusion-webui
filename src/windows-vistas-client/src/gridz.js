let x, y, w, h, i;
let totalShapeCount = 0;
let saveCanvas;
w = 384
h = 576

const rows = 3;
const columns = 4;
const fadeSpeed = .5;
let cells = [];
let cellColors = []
let shapeColor;
let isTouching = false;
let lastCellTouched = [null, null];

const sketchDiv = document.getElementById('interactiveMount')

export const gridSketch = (p) => {
  p.setup = () => {
    createMetaTag()
    // p.createCanvas(w, h);
    p.createCanvas(sketchDiv.offsetWidth, sketchDiv.offsetHeight);
    // p.createCanvas(window.innerWidth, window.innerHeight);
    saveCanvas = p.createGraphics(w, h);
    randomizeCellColors()
  }

  p.draw = () => {
    const cellWidth = p.width / columns;
    const cellHeight = p.height / rows;

    if (
      p.mouseX > 0 && p.mouseX < p.width &&
      p.mouseY > 0 && p.mouseY < p.height &&
      (p.mouseIsPressed === true || isTouching === true)
    ) {
      const mouseR = p.floor(rows * (p.mouseY / p.height));
      const mouseC = p.floor(columns * (p.mouseX / p.width));
      cells[mouseR][mouseC] = 255;
      // Change shapeColor when a new cell is touched
        if (mouseR !== lastCellTouched[0] || mouseC !== lastCellTouched[1]) {
            shapeColor = randomColor()
            lastCellTouched = [mouseR, mouseC]
        }


      // if (lastCellTouched === [mouseR, mouseC]) {
      //   shapeColor = randomColor();
      // }
      cellColors[mouseR][mouseC] = shapeColor;
      // lastCellTouched = [mouseR, mouseC];
    }

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < columns; c++) {
        const y = p.height * (r / rows);
        const x = p.width * (c / columns);

        // Original with fade
        //       fill(cells[r][c], 0, 255);
        p.fill(cellColors[r][c])
        p.rect(x, y, cellWidth, cellHeight);
      }
    }
    if (isTouching) {
    p.fill(p.random(255), 255, 255);
    p.ellipse(p.mouseX, p.mouseY, 30, 30);
  }

    // for (let i = 0; i < p.touches.length; i++) {
    //   let t = p.touches[i];
    //   p.ellipse(t.x, t.y, 50, 50);
    //
    //       // draw a line between this touch point and every other touch point
    //   for (let j = 0; j < p.touches.length; j++) {
    //     if (i == j) {
    //       continue;
    //     }
    //     let t2 = p.touches[j];
    //     p.line(t.x, t.y, t2.x, t2.y);
    //   }
    // }
  }

  p.mousePressed = () => {
    shapeColor = randomColor()
  }

  p.touchStarted = () => {
    isTouching = true;
    shapeColor = randomColor()
  }

  p.touchEnded = () => {
    isTouching = false;
  }

  p.touchMoved = () => {
    // prevent the display from moving around when you touch it
    return false;
  }

  p.saveTemp = () => {
    let c = p.get(0, 0, w, h);
    saveCanvas.image(c, 0, 0);
    return saveCanvas.canvas.toDataURL();
  }

  p.resetSketch = () => {
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
    for (let r = 0; r < rows; r++) {
      cells[r] = [];
      cellColors[r] = []
      for (let c = 0; c < columns; c++) {
        cells[r][c] = p.random(255);
        cellColors[r][c] = randomColor();
      }
    }
  }

  function randomColor() {
    return p.color(p.random(255), p.random(255), p.random(255))
  }

  function createMetaTag() {
  let meta = p.createElement('meta');
  meta.attribute('name', 'viewport');
  meta.attribute('content', 'user-scalable=no,initial-scale=1,maximum-scale=1,minimum-scale=1,width=device-width,height=device-height');

  let head = p.select('head');
  meta.parent(head);
}
}
