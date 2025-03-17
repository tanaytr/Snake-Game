import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

const CELL_SIZE = 20;
const GRID_WIDTH = 20;
const GRID_HEIGHT = 20;
const INITIAL_SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH;
const INITIAL_SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT;

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [gameState, setGameState] = useState({
    snake: [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }],
    direction: { x: 1, y: 0 },
    food: { x: 15, y: 10 },
    score: 0,
    gameOver: false,
    paused: false,
    bwMode: false
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Game loop
    const gameLoop = setInterval(() => {
      if (!gameState.gameOver && !gameState.paused) {
        updateGame();
      }
      drawGame(ctx);
    }, 150);

    return () => clearInterval(gameLoop);
  }, [gameState]);

  const updateGame = () => {
    // Move snake
    const newSnake = [...gameState.snake];
    const head = { 
      x: newSnake[0].x + gameState.direction.x,
      y: newSnake[0].y + gameState.direction.y 
    };

    // Check collisions
    if (checkCollision(head)) {
      setGameState(prev => ({ ...prev, gameOver: true }));
      return;
    }

    // Check food
    if (head.x === gameState.food.x && head.y === gameState.food.y) {
      // Grow snake and generate new food
      newSnake.unshift(head);
      const newFood = generateFood(newSnake);
      setGameState(prev => ({
        ...prev,
        snake: newSnake,
        food: newFood,
        score: prev.score + 10,
        bwMode: prev.score + 10 >= 100
      }));
    } else {
      // Move snake
      newSnake.unshift(head);
      newSnake.pop();
      setGameState(prev => ({ ...prev, snake: newSnake }));
    }
  };

  const checkCollision = (head: { x: number; y: number }) => {
    // Check walls
    if (head.y < 0 || head.y >= GRID_HEIGHT) return true;
    
    // Check self collision
    return gameState.snake.some(segment => 
      segment.x === head.x && segment.y === head.y
    );
  };

  const generateFood = (snake: Array<{ x: number; y: number }>) => {
    while (true) {
      const food = {
        x: Math.floor(Math.random() * GRID_WIDTH),
        y: Math.floor(Math.random() * GRID_HEIGHT)
      };
      if (!snake.some(segment => segment.x === food.x && segment.y === food.y)) {
        return food;
      }
    }
  };

  const drawGame = (ctx: CanvasRenderingContext2D) => {
    // Clear canvas
    ctx.fillStyle = gameState.bwMode ? '#FFFFFF' : '#AAD751';
    ctx.fillRect(0, 0, INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT);

    // Draw grid
    ctx.strokeStyle = gameState.bwMode ? '#000000' : '#96C147';
    for (let x = 0; x <= INITIAL_SCREEN_WIDTH; x += CELL_SIZE) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, INITIAL_SCREEN_HEIGHT);
      ctx.stroke();
    }
    for (let y = 0; y <= INITIAL_SCREEN_HEIGHT; y += CELL_SIZE) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(INITIAL_SCREEN_WIDTH, y);
      ctx.stroke();
    }

    // Draw snake
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#4A752C';
    gameState.snake.forEach(segment => {
      ctx.fillRect(
        segment.x * CELL_SIZE,
        segment.y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
      );
    });

    // Draw food
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#FF0000';
    ctx.beginPath();
    ctx.arc(
      gameState.food.x * CELL_SIZE + CELL_SIZE/2,
      gameState.food.y * CELL_SIZE + CELL_SIZE/2,
      CELL_SIZE/2,
      0,
      2 * Math.PI
    );
    ctx.fill();

    // Draw score
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#FFFFFF';
    ctx.font = '20px Arial';
    ctx.fillText(`Score: ${gameState.score}`, 10, 30);

    // Draw game over
    if (gameState.gameOver) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(0, 0, INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT);
      ctx.fillStyle = '#FFFFFF';
      ctx.font = '30px Arial';
      ctx.fillText('Game Over!', INITIAL_SCREEN_WIDTH/2 - 70, INITIAL_SCREEN_HEIGHT/2);
      ctx.font = '20px Arial';
      ctx.fillText('Press Space to restart', INITIAL_SCREEN_WIDTH/2 - 90, INITIAL_SCREEN_HEIGHT/2 + 40);
    }
  };

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (gameState.gameOver) {
        if (e.code === 'Space') {
          setGameState({
            snake: [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }],
            direction: { x: 1, y: 0 },
            food: generateFood([{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }]),
            score: 0,
            gameOver: false,
            paused: false,
            bwMode: false
          });
        }
        return;
      }

      switch (e.code) {
        case 'ArrowUp':
        case 'KeyW':
          if (gameState.direction.y !== 1) {
            setGameState(prev => ({ ...prev, direction: { x: 0, y: -1 } }));
          }
          break;
        case 'ArrowDown':
        case 'KeyS':
          if (gameState.direction.y !== -1) {
            setGameState(prev => ({ ...prev, direction: { x: 0, y: 1 } }));
          }
          break;
        case 'ArrowLeft':
        case 'KeyA':
          if (gameState.direction.x !== 1) {
            setGameState(prev => ({ ...prev, direction: { x: -1, y: 0 } }));
          }
          break;
        case 'ArrowRight':
        case 'KeyD':
          if (gameState.direction.x !== -1) {
            setGameState(prev => ({ ...prev, direction: { x: 1, y: 0 } }));
          }
          break;
        case 'Space':
          setGameState(prev => ({ ...prev, paused: !prev.paused }));
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gameState]);

  return (
    <>
      <Head>
        <title>Snake Game</title>
        <meta name="description" content="A modern take on the classic Snake game" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900">
        <canvas
          ref={canvasRef}
          width={INITIAL_SCREEN_WIDTH}
          height={INITIAL_SCREEN_HEIGHT}
          className="border border-gray-600"
        />
        <div className="mt-4 text-white text-center">
          <p>Use Arrow keys or WASD to move</p>
          <p>Space to pause/resume</p>
        </div>
      </main>
    </>
  );
} 