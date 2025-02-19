
var canvas = document.getElementById("sine");
var context = canvas.getContext("2d");

var amplitude = 50;
var frequency = 0.02;
var offset = 0;
var sineMargin = 200;

const gradSine = context.createLinearGradient(sineMargin, 0, canvas.width - sineMargin, 0);
gradSine.addColorStop(0.0,'transparent');
gradSine.addColorStop(0.5,'rgba(255,0,255)');
gradSine.addColorStop(1,'transparent');

const gradLine = context.createLinearGradient(0, 0, canvas.width, 0);
gradLine.addColorStop(0.0,'transparent');
gradLine.addColorStop(0.5,'black');
gradLine.addColorStop(1,'transparent');

function drawLine(){
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.lineWidth = 7;
  context.strokeStyle = gradLine;
  context.beginPath();
  context.moveTo(0, canvas.height/2)
  context.lineTo(canvas.width, canvas.height/2)
  context.stroke()
  requestAnimationFrame(drawLine);
}

function drawSine() {
  context.strokeStyle = gradSine;
  context.beginPath();
  context.lineWidth = 15;
  for (var x = sineMargin; x < canvas.width - sineMargin; x++) {
      var y = amplitude * Math.sin(frequency * x + offset);
      context.lineTo(x, canvas.height/2 - y);
  }
  context.stroke();
  offset += 0.04;
  
  requestAnimationFrame(drawSine);
}

drawLine();
drawSine();