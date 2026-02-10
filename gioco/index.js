let video;
let gameImage;
let logoImage; // Logo
let started = false;
let screen = "video"; // può essere "video" o "game"

// Pulsante
let buttonX, buttonY, buttonW, buttonH;

// Musica
let song1, song2;
let currentSong = 1;

function preload() {
  gameImage = loadImage('verra.png'); // Sostituisci con il nome della tua immagine
  logoImage = loadImage('logo.png'); 
  song1 = loadSound('Down_under.mp3'); // Sostituisci con il tuo file audio 1
  song2 = loadSound('wind.mp3'); // Sostituisci con il tuo file audio 2
}

function setup() {
  createCanvas(windowWidth, windowHeight);

  video = createVideo('video_menu.mp4');
  video.volume(0);
  video.hide();

  // Posizione e dimensione pulsante
  buttonW = 200;
  buttonH = 60;
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;

  // Imposta loop manuale alternato per le canzoni
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
    if (started && video && video.width > 0 && video.height > 0) {
      let w = 1920;
      let h = 1080;
      image(video, (width - w) / 2, (height - h) / 2, w, h);

      drawLogo();
      drawButton();
    } else {
      fill(255);
      textAlign(CENTER, CENTER);
      textSize(24);
      text("Clicca per avviare il gioco", width / 2, height / 2);
    }
  } else if (screen === "game") {
    imageMode(CENTER);
    image(gameImage, width / 2, height / 2);
    imageMode(CORNER);
  }
}

function drawLogo() {
  imageMode(CENTER);
  let logoWidth = 600;
  let logoHeight = 450;
  image(logoImage, width / 2, height / 2 - 150, logoWidth, logoHeight);
  imageMode(CORNER);
}

function drawButton() {
  let baseColor = color(50, 200, 100);
  let hoverColor = color(80, 255, 130);

  let isHover = mouseX > buttonX && mouseX < buttonX + buttonW &&
                mouseY > buttonY && mouseY < buttonY + buttonH;

  let btnColor = isHover ? hoverColor : baseColor;

  fill(btnColor);
  if (isHover) {
    stroke(255);
    strokeWeight(3);
  } else {
    noStroke();
  }

  drawingContext.shadowBlur = isHover ? 20 : 10;
  drawingContext.shadowColor = color(0, 150);

  rect(buttonX, buttonY, buttonW, buttonH, 20);

  noShadow();
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(26);
  textStyle(BOLD);
  text("GIOCA", buttonX + buttonW / 2, buttonY + buttonH / 2);
}

function noShadow() {
  drawingContext.shadowBlur = 0;
}

function mousePressed() {
  if (screen === "video") {
    if (!started && video) {
      video.loop();
      started = true;

      // Avvia la prima canzone quando il video parte
      if (!song1.isPlaying() && !song2.isPlaying()) {
        song1.play();
        currentSong = 1;
      }
    } else if (started) {
      if (mouseX > buttonX && mouseX < buttonX + buttonW &&
          mouseY > buttonY && mouseY < buttonY + buttonH) {
        screen = "game";

        // Ferma musica quando si passa al gioco
        song1.stop();
        song2.stop();
      }
    }
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  buttonX = width / 2 - buttonW / 2;
  buttonY = height / 2 + 100;
}
