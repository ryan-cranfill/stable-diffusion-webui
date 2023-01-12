let x, y, w, h, i;
let totalShapeCount = 0;
let saveCanvas;

export const clickyShapySketch = (p) => {
  p.setup = () => {
    p.createCanvas(512, 512);
    saveCanvas = p.createGraphics(512, 512);
    p.noStroke();
    p.background(255);
    p.stroke(255, 50);
    for (i = 0; i < totalShapeCount; i++) {
      p.drawRandomShape("rectangle");
    }

    p.stroke (0, 50);
    for (i = 0; i < totalShapeCount; i++) {
      p.drawRandomShape("ellipse");
    }
  }

  p.draw = () => {

  }

  p.mouseClicked = () => {
    p.drawRandomShape(null, p.mouseX, p.mouseY);
  }

  p.drawRandomShape = (choice=null, x=null, y=null) => {
    if (!choice) {
      // randomly choose between rectangle and ellipse
      choice = p.random(["rectangle", "ellipse"]);
    }

    if (!x) {
      x = p.random(p.width);
    }
    if (!y) {
      y = p.random(p.height);
    }
    w = p.random(75, 200);
    h = p.random(75, 200);

    if (choice === "ellipse") {
      p.noStroke();
      p.fill(p.random(50, 255), p.random(50, 255), p.random(50, 255));
      p.ellipse(x, y, w, h);
    }
    else {
      p.noStroke();
      p.fill(p.random(50, 255), p.random(50, 255), p.random(50, 255));
      p.rect(x, y, w, h);
    }
  }

  p.saveTemp = () => {
    let c = p.get(0,0,512,512);
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

}

