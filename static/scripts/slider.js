var slider = document.getElementById("iterationsSlider");
var output = document.getElementById("iterations");
output.innerHTML = slider.value;

slider.oninput = function() {
    output.innerHTML = this.value;
}