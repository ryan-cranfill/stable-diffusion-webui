let colors = [];
let brush = { x:0, y:0, px:0, py:0 }
let seed;
let saveCanvas;
let waiting = false;
let maxDiameter = 50;
let theta = 0;
let thetaInc = 0.04;

export const pollockSketch = (p) => {
  p.setup = () => {
    p.createCanvas(512, 512);
    saveCanvas = p.createGraphics(512, 512);
    p.noStroke();
    seed = p.random(1000);
    colors = [
      p.color(112,112,74), //green
      p.color(245,198,110), //yellow
      p.color(242,229,194), //cream
      p.color(115,106,97), //light grey
      p.color(215,90,34), //orange
      p.color(235,61,0), // red-orange
    ]
    let base = p.floor(p.random(colors.length));
    p.background(colors[base]);
    colors.splice(base,1);
  }

  p.randomColor = () => {
    let base = p.floor(p.random(colors.length));
    return colors[base];

  }

  p.draw = () => {
    if (waiting === true) {
      p.waitingCircle();
    } else {
      brush.x+=(p.mouseX-brush.x)/12;
      brush.y+=(p.mouseY-brush.y)/12;
      if(p.frameCount>40){
        // p.drizzle();
      }
      brush.px=brush.x;
      brush.py=brush.y;
    }
  }

  p.waitingCircle = () => {
    // p.background(255);
    let diam = 100 + p.sin(theta) * maxDiameter ;
    p.fill(255);
    p.stroke(0);
    // draw the circle
    p.ellipse(p.width / 2 , p.height/2, diam, diam);

    // make theta keep getting bigger
    // you can play with this number to change the speed
    theta += .1;
    console.log(theta, diam);
  }

  p.mouseMoved = () =>{
    if (waiting) {
      return;
    }
    // if(p.frameCount % 7===0){
    //   p.splatter(p.mouseX, p.mouseY);
    //   // p.splatter(p.width-p.mouseX, p.height-p.mouseY);
    //   p.stipple(p.mouseX, p.mouseY, 0);
    //   // p.stipple(p.width-p.mouseX, p.height-p.mouseY, 255);
    // }
  }

  p.resetSketch = () => {
    p.background(p.randomColor());
  }

  p.mouseDragged = () => {
    p.splatter(p.mouseX, p.mouseY);
    // p.splatter(p.width-p.mouseX, p.height-p.mouseY);
    p.stipple(p.mouseX, p.mouseY, 0);
  }

  p.mouseClicked = () => {
    for (let i = 0; i < 10; i++) {
      p.splatter(p.mouseX, p.mouseY);
      // p.splatter(p.width-p.mouseX, p.height-p.mouseY);
      p.stipple(p.mouseX, p.mouseY, 0);
    }
  }
  p.toggleWaiting = () => {
    waiting = !waiting;
  }

  p.drizzle = () =>{
    let s = 1+30/p.dist(brush.px, brush.py, brush.x, brush.y);
    s=p.min(15,s);
    p.strokeWeight(s);
    p.stroke(0);
    p.line(brush.px, brush.py, brush.x, brush.y);
    // p.stroke(255);
    // p.line(p.width-brush.px, p.height-brush.py, p.width-brush.x, p.height-brush.y);
  }

  p.splatter = (bx, by) => {
    let c = colors[p.floor(p.random(colors.length))];
    bx += p.random(-15,15);
    by += p.random(-15,15);
    let mx = 10*p.movedX;
    let my = 10*p.movedY;
    for(let i=0; i<80; i++){
      seed+=.01;
      let x = bx+mx*(0.5-p.noise(seed+i));
      let y = by+my*(0.5-p.noise(seed+2*i));
      let s = 150/p.dist(bx, by, x, y);
      if(s>20) s=20;
      let a = 255-s*5;
      p.noStroke();
      c.setAlpha(a);
      p.fill(c);
      p.ellipse(x,y,s);
      seed+=.01;
    }
  }

  p.stipple = (bx, by, c) =>{
    p.noStroke();
    p.fill(c);
    let radius = p.random(3, 12);
    p.ellipse(bx+p.random(-30,30), by+p.random(30,-30), radius);
    radius = p.random(3, 12);
    p.ellipse(bx + p.random(-30,30), by+p.random(30,-30), radius);
  }

  p.keyPressed = () => {
    if(p.keyCode === 32){
      // p.background(180);
    }
  }
  p.saveTemp = () => {
    let c = p.get(0,0,512,512);
    saveCanvas.image(c, 0, 0);
    return saveCanvas.canvas.toDataURL();
    // save(saveCanvas, frameCount+".png");
  }
}