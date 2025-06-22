# OPTCG Deck Builder UI

This project is a web-based deck builder and playmat simulator for the One Piece Card Game.

## Tech Stack

- **Framework**: React with TypeScript
- **Styling**: Standard CSS with Flexbox and Grid
- **Build Tool**: Vite for fast development and optimized builds

## Project Structure

```
frontend/
├── public/              # Static assets and index.html
└── src/
    ├── assets/          # Images, logos, etc.
    ├── pages/
    │   └── deckbuilder.tsx # Main UI component
    ├── App.tsx          # Root application component
    ├── main.tsx         # Application entry point
    └── index.css        # Global styles
```

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager

### Installation

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Start the development server:**
    ```sh
    npm run dev
    ```

4.  **Open your browser** and navigate to the local URL provided in the terminal (e.g., `http://localhost:5173`).

## Building for Production

To create an optimized build for deployment:

```sh
npm run build
```
The built files will be in the `dist` directory.
