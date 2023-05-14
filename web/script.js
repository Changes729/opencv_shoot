let cw;
let grid = 20;
let px = 0;
let py = 0;
let x=0
let y =0
let easing = 0.1
function setup() {
  createCanvas(window.innerWidth, window.innerHeight);
  cw = width / grid;
}
function draw() {
  background(255);
  $.get("http://127.0.0.1:5000", function (data) {
    pp = JSON.parse(data);
    px = pp["x"];
    py = pp["y"];
  });
  fill(0)
  // for (let col = 0; col < grid; col++) {
  //   for (let row = 0; row < grid; row++) {
  //     x = col * cw + (1 / 2) * cw;
  //     y = row * cw + (1 / 2) * cw;
  //     d = dist(px*width,py*height,x,y)/width
  //     // print (d)
  //     // console.log(distance / width);
  //     ellipse(x, y, cw*d);
  //   }
  // }
  // print(px,py)
  x+=(px*width-x)*easing
  y+=(py*height-y)*easing
  print(x)
  ellipse(x,y,30,30)
  // noLoop();
}
