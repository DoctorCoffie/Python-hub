const canvas = document.getElementById("game-canvas");
const scoreEl = document.getElementById("score");
const timeEl = document.getElementById("time");
const startButton = document.getElementById("start-game");
const messageEl = document.getElementById("game-message");
const nameInput = document.getElementById("player-name");

if (canvas && scoreEl && timeEl && startButton && messageEl && nameInput) {
  const ctx = canvas.getContext("2d");
  const gridSize = 20;
  const cells = canvas.width / gridSize;
  let snake = [];
  let direction = { x: 1, y: 0 };
  let food = { x: 10, y: 10 };
  let score = 0;
  let gameInterval = null;
  let startTime = null;
  let timeInterval = null;

  const resetGame = () => {
    snake = [
      { x: 9, y: 10 },
      { x: 8, y: 10 },
      { x: 7, y: 10 },
    ];
    direction = { x: 1, y: 0 };
    food = randomFood();
    score = 0;
    scoreEl.textContent = "0";
    timeEl.textContent = "0";
    messageEl.textContent = "Enter your name and press Start game.";
  };

  const randomFood = () => {
    let pos;
    do {
      pos = {
        x: Math.floor(Math.random() * cells),
        y: Math.floor(Math.random() * cells),
      };
    } while (snake.some((segment) => segment.x === pos.x && segment.y === pos.y));
    return pos;
  };

  const draw = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#c9d5b2";
    snake.forEach((segment, index) => {
      ctx.fillStyle = index === 0 ? "#f2b450" : "#6d7f3a";
      ctx.fillRect(
        segment.x * gridSize,
        segment.y * gridSize,
        gridSize - 2,
        gridSize - 2
      );
    });

    ctx.fillStyle = "#f05d23";
    ctx.fillRect(
      food.x * gridSize,
      food.y * gridSize,
      gridSize - 2,
      gridSize - 2
    );
  };

  const step = () => {
    const head = {
      x: (snake[0].x + direction.x + cells) % cells,
      y: (snake[0].y + direction.y + cells) % cells,
    };

    if (snake.some((segment) => segment.x === head.x && segment.y === head.y)) {
      endGame();
      return;
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
      score += 1;
      scoreEl.textContent = String(score);
      food = randomFood();
    } else {
      snake.pop();
    }

    draw();
  };

  const endGame = async () => {
    clearInterval(gameInterval);
    clearInterval(timeInterval);
    gameInterval = null;
    const durationSeconds = Math.max(
      1,
      Math.floor((Date.now() - startTime) / 1000)
    );
    const name = nameInput.value.trim();
    messageEl.textContent = `Game over. Score ${score} in ${durationSeconds}s.`;
    await fetch("/api/snake-game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        player_name: name || "anon",
        score,
        duration_seconds: durationSeconds,
      }),
    });
  };

  const startGame = () => {
    if (gameInterval) {
      return;
    }
    const playerName = nameInput.value.trim();
    if (!playerName) {
      messageEl.textContent = "Please enter your name before playing.";
      nameInput.focus();
      return;
    }
    resetGame();
    startTime = Date.now();
    timeInterval = setInterval(() => {
      const seconds = Math.floor((Date.now() - startTime) / 1000);
      timeEl.textContent = String(seconds);
    }, 1000);
    draw();
    gameInterval = setInterval(step, 140);
    canvas.focus();
  };

  document.addEventListener("keydown", (event) => {
    if (!gameInterval) {
      return;
    }
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
    }
    if (event.key === "ArrowUp" && direction.y !== 1) {
      direction = { x: 0, y: -1 };
    } else if (event.key === "ArrowDown" && direction.y !== -1) {
      direction = { x: 0, y: 1 };
    } else if (event.key === "ArrowLeft" && direction.x !== 1) {
      direction = { x: -1, y: 0 };
    } else if (event.key === "ArrowRight" && direction.x !== -1) {
      direction = { x: 1, y: 0 };
    }
  });

  startButton.addEventListener("click", startGame);
  resetGame();
}
