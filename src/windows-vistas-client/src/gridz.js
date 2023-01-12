const rows = 3;
const columns = 4;
const fadeSpeed = .5;
let cells = [];
let cellColors = []
let shapeColor;

function setup() {
  createCanvas(384, 576);

  for (let r = 0; r < rows; r++) {
    cells[r] = [];
    cellColors[r] = []
    for (let c = 0; c < columns; c++) {
      cells[r][c] = random(255);
      cellColors[r][c] = randomColor();
    }
  }
}

function randomColor() {
  return color(random(255), random(255), random(255))
}

function mousePressed(){
  shapeColor = color(random(255), random(255), random(255) );
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