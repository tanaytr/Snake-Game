import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

// Base cell size that will be adjusted based on screen size
const BASE_CELL_SIZE = 20;
const GRID_WIDTH = 20;
const GRID_HEIGHT = 20;

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cellSize, setCellSize] = useState(BASE_CELL_SIZE);
  const [screenDimensions, setScreenDimensions] = useState({
    width: BASE_CELL_SIZE * GRID_WIDTH,
    height: BASE_CELL_SIZE * GRID_HEIGHT
  });
  const [isMobile, setIsMobile] = useState(false);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);

  const [gameState, setGameState] = useState({
    snake: [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }],
    direction: { x: 1, y: 0 },
    food: { x: 15, y: 10 },
    score: 0,
    gameOver: false,
    paused: false,
    bwMode: false
  });

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const isMobileDevice = window.innerWidth < 768;
      setIsMobile(isMobileDevice);

      // Calculate new cell size based on screen size
      const maxWidth = Math.min(window.innerWidth * 0.9, 600);
      const maxHeight = Math.min(window.innerHeight * 0.7, 600);
      
      const newCellSize = Math.floor(Math.min(
        maxWidth / GRID_WIDTH,
        maxHeight / GRID_HEIGHT
      ));

      setCellSize(newCellSize);
      setScreenDimensions({
        width: newCellSize * GRID_WIDTH,
        height: newCellSize * GRID_HEIGHT
      });
    };

    handleResize(); // Initial calculation
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Touch controls for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStart) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    
    // Determine swipe direction based on which delta is larger
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      if (deltaX > 0 && gameState.direction.x !== -1) {
        setGameState(prev => ({ ...prev, direction: { x: 1, y: 0 } }));
      } else if (deltaX < 0 && gameState.direction.x !== 1) {
        setGameState(prev => ({ ...prev, direction: { x: -1, y: 0 } }));
      }
    } else {
      // Vertical swipe
      if (deltaY > 0 && gameState.direction.y !== -1) {
        setGameState(prev => ({ ...prev, direction: { x: 0, y: 1 } }));
      } else if (deltaY < 0 && gameState.direction.y !== 1) {
        setGameState(prev => ({ ...prev, direction: { x: 0, y: -1 } }));
      }
    }
    
    setTouchStart(null);
  };

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
    ctx.fillRect(0, 0, screenDimensions.width, screenDimensions.height);

    // Draw grid
    ctx.strokeStyle = gameState.bwMode ? '#000000' : '#96C147';
    for (let x = 0; x <= screenDimensions.width; x += cellSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, screenDimensions.height);
      ctx.stroke();
    }
    for (let y = 0; y <= screenDimensions.height; y += cellSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(screenDimensions.width, y);
      ctx.stroke();
    }

    // Draw snake
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#4A752C';
    gameState.snake.forEach(segment => {
      ctx.fillRect(
        segment.x * cellSize,
        segment.y * cellSize,
        cellSize,
        cellSize
      );
    });

    // Draw food
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#FF0000';
    ctx.beginPath();
    ctx.arc(
      gameState.food.x * cellSize + cellSize/2,
      gameState.food.y * cellSize + cellSize/2,
      cellSize/2,
      0,
      2 * Math.PI
    );
    ctx.fill();

    // Draw score with responsive font size
    const fontSize = Math.max(16, Math.floor(cellSize * 0.8));
    ctx.fillStyle = gameState.bwMode ? '#000000' : '#FFFFFF';
    ctx.font = `${fontSize}px Arial`;
    ctx.fillText(`Score: ${gameState.score}`, 10, fontSize + 5);

    // Draw game over with responsive font size
    if (gameState.gameOver) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(0, 0, screenDimensions.width, screenDimensions.height);
      ctx.fillStyle = '#FFFFFF';
      
      const largeFontSize = Math.max(24, Math.floor(cellSize * 1.2));
      const smallFontSize = Math.max(16, Math.floor(cellSize * 0.8));
      
      ctx.font = `${largeFontSize}px Arial`;
      ctx.fillText('Game Over!', screenDimensions.width/2 - largeFontSize*2, screenDimensions.height/2);
      
      ctx.font = `${smallFontSize}px Arial`;
      const restartText = isMobile ? 'Tap to restart' : 'Press Space to restart';
      ctx.fillText(restartText, screenDimensions.width/2 - ctx.measureText(restartText).width/2, screenDimensions.height/2 + largeFontSize);
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
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900 p-4">
        <canvas
          ref={canvasRef}
          width={screenDimensions.width}
          height={screenDimensions.height}
          className="border border-gray-600 touch-none"
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
        />
        <div className="mt-4 text-white text-center">
          {isMobile ? (
            <p>Swipe to move the snake</p>
          ) : (
            <>
              <p>Use Arrow keys or WASD to move</p>
              <p>Space to pause/resume</p>
            </>
          )}
        </div>
      </main>
    </>
  );
} 