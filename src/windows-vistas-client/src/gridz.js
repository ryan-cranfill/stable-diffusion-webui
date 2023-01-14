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



export const gridSketch = (p) => {
  p.setup = () => {
    p.createCanvas(w, h);
    saveCanvas = p.createGraphics(w, h);

    for (let r = 0; r < rows; r++) {
      cells[r] = [];
      cellColors[r] = []
      for (let c = 0; c < columns; c++) {
        cells[r][c] = p.random(255);
        cellColors[r][c] = randomColor();
      }
    }
  }

  p.draw = () => {
    const cellWidth = p.width / columns;
    const cellHeight = p.height / rows;

    if (
      p.mouseX > 0 && p.mouseX < p.width &&
      p.mouseY > 0 && p.mouseY < p.height &&
      p.mouseIsPressed === true
    ) {
      const mouseR = p.floor(rows * (p.mouseY / p.height));
      const mouseC = p.floor(columns * (p.mouseX / p.width));
      cells[mouseR][mouseC] = 255;
      cellColors[mouseR][mouseC] = shapeColor;
    }

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < columns; c++) {
        cells[r][c] -= fadeSpeed;
        cells[r][c] = p.constrain(cells[r][c], 0, 255);

        const y = p.height * (r / rows);
        const x = p.width * (c / columns);

        // Original with fade
        //       fill(cells[r][c], 0, 255);
        p.fill(cellColors[r][c])
        // fill(randomColor());
        p.rect(x, y, cellWidth, p.height);
      }
    }
  }

  p.mousePressed = () => {
    shapeColor = randomColor()
  }

  p.saveTemp = () => {
    let c = p.get(0, 0, w, h);
    saveCanvas.image(c, 0, 0);
    return saveCanvas.canvas.toDataURL();
    // save(saveCanvas, frameCount+".png");
  }

  p.resetSketch = () => {
    p.background(255);
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

  function randomColor() {
    return p.color(p.random(255), p.random(255), p.random(255))
  }
  //
  // p.mouseClicked = () => {
  //   p.drawRandomShape(null, p.mouseX, p.mouseY);
  // }
  //
  // p.drawRandomShape = (choice=null, x=null, y=null) => {
  //   if (!choice) {
  //     // randomly choose between rectangle and ellipse
  //     choice = p.random(["rectangle", "ellipse"]);
  //   }
  //
  //   if (!x) {
  //     x = p.random(p.width);
  //   }
  //   if (!y) {
  //     y = p.random(p.height);
  //   }
  //   w = p.random(75, 200);
  //   h = p.random(75, 200);
  //
  //   if (choice === "ellipse") {
  //     p.noStroke();
  //     p.fill(p.random(50, 255), p.random(50, 255), p.random(50, 255));
  //     p.ellipse(x, y, w, h);
  //   }
  //   else {
  //     p.noStroke();
  //     p.fill(p.random(50, 255), p.random(50, 255), p.random(50, 255));
  //     p.rect(x, y, w, h);
  //   }
  // }
  //
  // p.saveTemp = () => {
  //   let c = p.get(0,0,512,512);
  //   saveCanvas.image(c, 0, 0);
  //   return saveCanvas.canvas.toDataURL();
  //   // save(saveCanvas, frameCount+".png");
  // }
  //
  // p.resetSketch = () => {
  //   p.background(255);
  // }
  //
  // p.setBackground = (data) => {
  //   if (data.isSolid) {
  //     p.background(data.color);
  //   } else {
  //     const src = `/backgrounds/${data.src}`;
  //     p.loadImage(src, (img) => {
  //       p.image(img, 0, 0)
  //     });
  //   }
  // }

}

// function setup() {
//   createCanvas(384, 576);
//
//   for (let r = 0; r < rows; r++) {
//     cells[r] = [];
//     cellColors[r] = []
//     for (let c = 0; c < columns; c++) {
//       cells[r][c] = random(255);
//       cellColors[r][c] = randomColor();
//     }
//   }
// }

function randomColor() {
  return p.color(p.random(255), p.random(255), p.random(255))
}

function mousePressed(){
  shapeColor = randomColor()
}

function draw() {
  const cellWidth = width / columns;
  const cellHeight = height / rows;

  if (
    mouseX > 0 && mouseX < width &&
    mouseY > 0 && mouseY < height &&
    mouseIsPressed === true
  ) {
    const mouseR = floor(rows * (mouseY / height));
    const mouseC = floor(columns * (mouseX / width));
    cells[mouseR][mouseC] = 255;
    cellColors[mouseR][mouseC] = shapeColor;
  }

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < columns; c++) {
      cells[r][c] -= fadeSpeed;
      cells[r][c] = constrain(cells[r][c], 0, 255);

      const y = height * (r / rows);
      const x = width * (c / columns);

      // Original with fade
      //       fill(cells[r][c], 0, 255);
      fill(cellColors[r][c])
      // fill(randomColor());
      rect(x, y, cellWidth, height);
    }
  }
}