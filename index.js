let video;
let gameImage;
let started = false;
let screen = "video"; // può essere "video" o "game"

function preload() {
  gameImage = loadImage('ak_prova.png'); // Sostituisci con il nome della tua immagine
}

function setup() {
  createCanvas(windowWidth, windowHeight);

  video = createVideo('video_menu.mp4');
  video.volume(0);
  video.hide();
}

function draw() {
  background(0);

  if (screen === "video") {
    // Disegna il video
    if (started && video && video.width > 0 && video.height > 0) {
      let w = 1920;
      let h = 1080;
      image(video, (width - w) / 2, (height - h) / 2, w, h);
      
      // Pulsante GIOCA in sovraimpressione
      drawPlayButton();
    }

    // Messaggio iniziale
    if (!started) {
      fill(255);
      textAlign(CENTER, CENTER);
      textSize(24);
      text("Clicca per avviare il video", width / 2, height / 2);
    }
  } else if (screen === "game") {
    // Mostra l'immagine
    imageMode(CENTER);
    image(gameImage, width / 2, height / 2);
    imageMode(CORNER);
  }
}

function drawPlayButton() {
  let buttonW = 200;
  let buttonH = 80;
  let buttonX = width / 2 - buttonW / 2;
  let buttonY = height / 2 - buttonH / 2;
  
  // Evidenzia se il mouse è sopra
  if (mouseX > buttonX && mouseX < buttonX + buttonW &&
      mouseY > buttonY && mouseY < buttonY + buttonH) {
    fill(100, 200, 255, 200);
  } else {
    fill(50, 150, 255, 200);
  }
  
  rect(buttonX, buttonY, buttonW, buttonH, 10);
  
  fill(255);
  textAlign(CENTER, CENTER);
  textSize(32);
  text("GIOCA", width / 2, height / 2);
}

function mousePressed() {
  if (screen === "video") {
    if (!started && video) {
      // Avvia il video
      video.loop();
      started = true;
    } else if (started) {
      // Controlla se ha cliccato sul pulsante GIOCA
      let buttonW = 200;
      let buttonH = 80;
      let buttonX = width / 2 - buttonW / 2;
      let buttonY = height / 2 - buttonH / 2;
      
      if (mouseX > buttonX && mouseX < buttonX + buttonW &&
          mouseY > buttonY && mouseY < buttonY + buttonH) {
        screen = "game";
      }
    }
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}