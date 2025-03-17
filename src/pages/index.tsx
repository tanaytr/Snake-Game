import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

const GRID_WIDTH = 20;
const GRID_HEIGHT = 20;

interface GameState {
  snake: Array<{ x: number; y: number }>;
  direction: { x: number; y: number };
  food: { x: number; y: number };
  score: number;
  gameOver: boolean;
  paused: boolean;
  bwMode: boolean;
  showMenu: boolean;
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cellSize, setCellSize] = useState(20);
  const [dimensions, setDimensions] = useState({ width: 400, height: 400 });
  
  const [gameState, setGameState] = useState<GameState>({
    snake: [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }],
    direction: { x: 1, y: 0 },
    food: { x: 15, y: 10 },
    score: 0,
    gameOver: false,
    paused: false,
    bwMode: false,
    showMenu: true
  });

  useEffect(() => {
    const handleResize = () => {
      const container = document.querySelector('.canvas-container');
      if (!container) return;

      const { width, height } = container.getBoundingClientRect();
      const size = Math.min(width, height);
      const newCellSize = Math.floor(size / GRID_WIDTH);

      setCellSize(newCellSize);
      setDimensions({ width: size, height: size });
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const updateGame = () => {
    if (gameState.gameOver || gameState.paused || gameState.showMenu) return;

    const newSnake = [...gameState.snake];
    const head = { 
      x: (newSnake[0].x + gameState.direction.x + GRID_WIDTH) % GRID_WIDTH,
      y: newSnake[0].y + gameState.direction.y
    };

    // Check collisions
    if (head.y < 0 || head.y >= GRID_HEIGHT || checkSelfCollision(head)) {
      setGameState(prev => ({ ...prev, gameOver: true }));
      return;
    }

    // Check food
    if (head.x === gameState.food.x && head.y === gameState.food.y) {
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
      newSnake.unshift(head);
      newSnake.pop();
      setGameState(prev => ({ ...prev, snake: newSnake }));
    }
  };

  const checkSelfCollision = (head: { x: number; y: number }) => {
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

  const startGame = () => {
    setGameState({
      snake: [{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }],
      direction: { x: 1, y: 0 },
      food: generateFood([{ x: 5, y: 10 }, { x: 4, y: 10 }, { x: 3, y: 10 }]),
      score: 0,
      gameOver: false,
      paused: false,
      bwMode: false,
      showMenu: false
    });
  };

  const handleDirection = (newDirection: { x: number; y: number }) => {
    if (gameState.gameOver || gameState.paused || gameState.showMenu) return;
    
    const currentDir = gameState.direction;
    if (
      (newDirection.x !== 0 && newDirection.x !== -currentDir.x) ||
      (newDirection.y !== 0 && newDirection.y !== -currentDir.y)
    ) {
      setGameState(prev => ({ ...prev, direction: newDirection }));
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const gameLoop = setInterval(updateGame, 150);
    const render = () => {
      // Clear canvas
      ctx.fillStyle = gameState.bwMode ? '#FFFFFF' : '#1a1a1a';
      ctx.fillRect(0, 0, dimensions.width, dimensions.height);

      // Draw grid
      ctx.strokeStyle = gameState.bwMode ? '#CCCCCC' : '#333333';
      ctx.lineWidth = 1;
      
      for (let x = 0; x <= dimensions.width; x += cellSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, dimensions.height);
        ctx.stroke();
      }
      
      for (let y = 0; y <= dimensions.height; y += cellSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(dimensions.width, y);
        ctx.stroke();
      }

      if (gameState.showMenu) {
        ctx.fillStyle = gameState.bwMode ? '#000000' : '#FFFFFF';
        ctx.font = '20px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText('SNAKE GAME', dimensions.width/2, dimensions.height/2 - 40);
        ctx.font = '16px "Press Start 2P"';
        ctx.fillText('Press SPACE to Start', dimensions.width/2, dimensions.height/2 + 20);
        return;
      }

      // Draw snake
      ctx.fillStyle = gameState.bwMode ? '#000000' : '#4CAF50';
      gameState.snake.forEach((segment, index) => {
        ctx.fillRect(
          segment.x * cellSize,
          segment.y * cellSize,
          cellSize - 1,
          cellSize - 1
        );
      });

      // Draw food
      ctx.fillStyle = gameState.bwMode ? '#000000' : '#FF5252';
      ctx.beginPath();
      ctx.arc(
        gameState.food.x * cellSize + cellSize/2,
        gameState.food.y * cellSize + cellSize/2,
        cellSize/2 - 1,
        0,
        2 * Math.PI
      );
      ctx.fill();

      // Draw score
      ctx.fillStyle = gameState.bwMode ? '#000000' : '#FFFFFF';
      ctx.font = '16px "Press Start 2P"';
      ctx.textAlign = 'left';
      ctx.fillText(`Score: ${gameState.score}`, 10, 30);

      if (gameState.gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, dimensions.width, dimensions.height);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '20px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', dimensions.width/2, dimensions.height/2 - 20);
        ctx.font = '16px "Press Start 2P"';
        ctx.fillText(`Score: ${gameState.score}`, dimensions.width/2, dimensions.height/2 + 20);
        ctx.fillText('Press SPACE to Restart', dimensions.width/2, dimensions.height/2 + 60);
      }

      if (gameState.paused) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, dimensions.width, dimensions.height);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '20px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText('PAUSED', dimensions.width/2, dimensions.height/2);
      }

      requestAnimationFrame(render);
    };

    render();
    return () => clearInterval(gameLoop);
  }, [gameState, dimensions, cellSize]);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (gameState.showMenu && e.code === 'Space') {
        startGame();
        return;
      }

      if (gameState.gameOver && e.code === 'Space') {
        startGame();
        return;
      }

      if (e.code === 'Space' && !gameState.showMenu) {
        setGameState(prev => ({ ...prev, paused: !prev.paused }));
        return;
      }

      const directions: { [key: string]: { x: number; y: number } } = {
        ArrowUp: { x: 0, y: -1 },
        ArrowDown: { x: 0, y: 1 },
        ArrowLeft: { x: -1, y: 0 },
        ArrowRight: { x: 1, y: 0 },
        KeyW: { x: 0, y: -1 },
        KeyS: { x: 0, y: 1 },
        KeyA: { x: -1, y: 0 },
        KeyD: { x: 1, y: 0 }
      };

      if (directions[e.code]) {
        handleDirection(directions[e.code]);
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
      
      <div className="game-container">
        <div className="canvas-container">
          <canvas
            ref={canvasRef}
            width={dimensions.width}
            height={dimensions.height}
          />
        </div>

        <div className="controls">
          <div className="control-row">
            <button 
              className="control-btn"
              onTouchStart={() => handleDirection({ x: 0, y: -1 })}
            >
              ↑
            </button>
          </div>
          <div className="control-row">
            <button 
              className="control-btn"
              onTouchStart={() => handleDirection({ x: -1, y: 0 })}
            >
              ←
            </button>
            <button 
              className="control-btn"
              onTouchStart={() => handleDirection({ x: 0, y: 1 })}
            >
              ↓
            </button>
            <button 
              className="control-btn"
              onTouchStart={() => handleDirection({ x: 1, y: 0 })}
            >
              →
            </button>
          </div>
        </div>
      </div>
    </>
  );
} 