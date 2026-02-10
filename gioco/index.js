let video;
let gameImage;
let logoImage;
let started = false;
let screen = "video";

// Pulsante
let buttonX, buttonY, buttonW, buttonH;

// Musica con Audio HTML5
let song1, song2;
let currentSong = 1;

function preload() {
  gameImage = loadImage('itis.png');
  logoImage = loadImage('logo.png');
}

function setup() {
  createCanvas(windowWidth, windowHeight);

  video = createVideo('video_menu.mp4');
  video.hide();
  video.volume(0);
  video.attribute('playsinline', '');
  video.elt.muted = true;

  // Audio HTML5
  song1 = new Audio('Down_under.mp3');
  song2 = new Audio('wind.mp3');

  buttonW = 200;
  buttonH = 60;
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;

  // Loop musicale continuo (menu + gioco)
  song1.onended = () => {
    song2.play();
    currentSong = 2;
  };

  song2.onended = () => {
    song1.play();
    currentSong = 1;
  };
}

function draw() {
  background(0);

  if (screen === "video") {
    if (started) {
      let videoW = video.width;
      let videoH = video.height;
      let scaleRatio = min(width / videoW, height / videoH);
      let w = videoW * scaleRatio;
      let h = videoH * scaleRatio;

      image(video, (width - w) / 2, (height - h) / 2, w, h);

      drawLogo();
      drawButton();
    } else {
      fill(255);
      textAlign(CENTER, CENTER);
      textSize(26);
      noStroke();
      text("Clicca per avviare il gioco", width / 2, height / 2);
    }
  }

  if (screen === "game") {
    imageMode(CENTER);
    let scaleRatio = min(width / gameImage.width, height / gameImage.height);
    image(
      gameImage,
      width / 2,
      height / 2,
      gameImage.width * scaleRatio,
      gameImage.height * scaleRatio
    );
    imageMode(CORNER);
  }
}

function drawLogo() {
  imageMode(CENTER);
  let logoW = min(600, width * 0.8);
  let logoH = logoW * 0.75;
  image(logoImage, width / 2, height / 2 - 150, logoW, logoH);
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
  noStroke();
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(26);
  textStyle(BOLD);
  text("GIOCA", buttonX + buttonW / 2, buttonY + buttonH / 2);
  textStyle(NORMAL);
}

function mousePressed() {
  // PRIMO CLICK → sblocca audio e video
  if (!started) {
    video.loop();
    started = true;

    song1.play().catch(e => console.log("Errore audio:", e));
    currentSong = 1;
    return;
  }

  // CLICK SUL PULSANTE GIOCA
  if (
    mouseX > buttonX && mouseX < buttonX + buttonW &&
    mouseY > buttonY && mouseY < buttonY + buttonH
  ) {
    screen = "game";
    video.stop(); // solo il video si ferma
    // 🎵 la musica CONTINUA
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;
}
