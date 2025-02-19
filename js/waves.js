
document.addEventListener("click", getCursorPosition);

var canvasWaves = document.getElementById('waveCanvas');
var contextWaves = canvasWaves.getContext('2d');

canvasWaves.height=window.innerHeight;
canvasWaves.width=window.innerWidth;

var max_depth = 3;
var max_r = 300;
var thickness = 10;
var max_circles_amount = 5;
var circles_amount = 0; 
var base_opaciy = 0.3;

contextWaves.beginPath();
contextWaves.lineWidth = 2;

var circles = [];

function newCircle(x, y, d){
    if(circles_amount>max_circles_amount) return;

    circles.push({"x": x, "y": y, "r": 1, "depth": d})
    circles_amount += 1;
}

function getCursorPosition(event) {
    newCircle(event.clientX, event.clientY, 1)
}

function draw(){
    contextWaves.clearRect(0, 0, canvasWaves.width, canvasWaves.height);
    
    circles.forEach((circle, index) => {

        for(var i = thickness; i > -thickness; i--){
            if (circle.r < i) break;

            contextWaves.beginPath();

            if(i==0) opacity = base_opaciy * ((1 - (circle.depth/max_depth)) * (1 - (circle.r/max_r)));
            else opacity = base_opaciy * ((1 - (Math.abs(i)/thickness)) * (1 - (circle.depth/max_depth)) * (1 - (circle.r/max_r)));
            
            contextWaves.strokeStyle = "rgba( 255, 0, 255, "+opacity+" )"
            contextWaves.arc(circle.x, circle.y, circle.r+i, 0, 2 * Math.PI);
            contextWaves.stroke();
        }

        //delete circle
        if (circle.r > max_r || circle.depth > max_depth){
            circles.splice(index, 1);
            circles_amount -= 1;
        }

        //wall reflections
        if(circle.x + circle.r == canvasWaves.width){
            newCircle(canvasWaves.width, circle.y, circle.depth + 1);
        }
        if(circle.x - circle.r == 0){
            newCircle(0, circle.y, circle.depth + 1);
        }
        if(circle.y + circle.r == canvasWaves.height){
            newCircle(circle.x, canvasWaves.height, circle.depth + 1);
        }
        if(circle.y - circle.r == 0){
            newCircle(circle.x, 0, circle.depth + 1);
        }

        circle.r+=1;
    });
    
    requestAnimationFrame(draw);
}
draw()