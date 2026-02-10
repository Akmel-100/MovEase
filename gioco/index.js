let video;
let gameImage;
let logoImage;
let started = false;
let screen = "video";

// Pulsante
let buttonX, buttonY, buttonW, buttonH;

// Musica
let song1, song2;
let currentSong = 1;

function preload() {
  gameImage = loadImage('verra.png');
  logoImage = loadImage('logo.png');
  song1 = loadSound('Down_under.mp3');
  song2 = loadSound('wind.mp3');
}

function setup() {
  createCanvas(windowWidth, windowHeight);

  video = createVideo('video_menu.mp4');
  video.hide();
  video.volume(0);
  video.attribute('playsinline', '');
  video.elt.muted = true; // NECESSARIO PER I BROWSER

  buttonW = 200;
  buttonH = 60;
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;

  song1.onended(() => {
    song2.play();
    currentSong = 2;
  });

  song2.onended(() => {
    song1.play();
    currentSong = 1;
  });
}

function draw() {
  background(0);

  if (screen === "video") {
    if (started) {
      let w = 1920;
      let h = 1080;
      image(video, (width - w) / 2, (height - h) / 2, w, h);

      drawLogo();
      drawButton();
    } else {
      fill(255);
      textAlign(CENTER, CENTER);
      textSize(26);
      text("Clicca per avviare il gioco", width / 2, height / 2);
    }
  }

  if (screen === "game") {
    imageMode(CENTER);
    image(gameImage, width / 2, height / 2);
    imageMode(CORNER);
  }
}

function drawLogo() {
  imageMode(CENTER);
  image(logoImage, width / 2, height / 2 - 150, 600, 450);
  imageMode(CORNER);
}

function drawButton() {
  let isHover =
    mouseX > buttonX && mouseX < buttonX + buttonW &&
    mouseY > buttonY && mouseY < buttonY + buttonH;

  fill(isHover ? color(80, 255, 130) : color(50, 200, 100));

  if (isHover) {
    stroke(255);
    strokeWeight(3);
  } else {
    noStroke();
  }

  drawingContext.shadowBlur = isHover ? 20 : 10;
  drawingContext.shadowColor = color(0, 150);

  rect(buttonX, buttonY, buttonW, buttonH, 20);

  drawingContext.shadowBlur = 0;
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(26);
  textStyle(BOLD);
  text("GIOCA", buttonX + buttonW / 2, buttonY + buttonH / 2);
}

function mousePressed() {
  // PRIMO CLICK → sblocca tutto
  if (!started) {
    userStartAudio(); // SBLOCCA AUDIO
    video.loop();
    started = true;

    if (!song1.isPlaying() && !song2.isPlaying()) {
      song1.play();
      currentSong = 1;
    }
    return;
  }

  // CLICK SUL PULSANTE
  if (
    mouseX > buttonX && mouseX < buttonX + buttonW &&
    mouseY > buttonY && mouseY < buttonY + buttonH
  ) {
    screen = "game";
    video.stop();
    song1.stop();
    song2.stop();
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;
}
