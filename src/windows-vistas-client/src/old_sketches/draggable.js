// Click and Drag an object
// Daniel Shiffman <http://www.shiffman.net>

export class Draggable {
  constructor(x, y, w, h, p) {
    this.dragging = false; // Is the object being dragged?
    this.rollover = false; // Is the mouse over the ellipse?
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
    this.p = p;
    this.offsetX = 0;
    this.offsetY = 0;
  }

  over() {
    // Is mouse over object
    if (this.p.mouseX > this.x && this.p.mouseX < this.x + this.w && this.p.mouseY > this.y && this.p.mouseY < this.y + this.h) {
      this.rollover = true;
    } else {
      this.rollover = false;
    }
  }

  update() {
    // Adjust location if being dragged
    if (this.dragging) {
      this.x = this.p.mouseX + this.offsetX;
      this.y = this.p.mouseY + this.offsetY;
    }
  }

  show() {
    this.p.stroke(0);
    // Different fill based on state
    if (this.dragging) {
      this.p.fill(50);
    } else if (this.rollover) {
      this.p.fill(100);
    } else {
      this.p.fill(175, 200);
    }
    this.p.rect(this.x, this.y, this.w, this.h);
  }

  pressed() {
    // Did I click on the rectangle?
    if (this.p.mouseX > this.x && this.p.mouseX < this.x + this.w && this.p.mouseY > this.y && this.p.mouseY < this.y + this.h) {
      this.dragging = true;
      // If so, keep track of relative location of click to corner of rectangle
      this.offsetX = this.x - this.p.mouseX;
      this.offsetY = this.y - this.p.mouseY;
    }
  }

  released() {
    // Quit dragging
    this.dragging = false;
  }
}