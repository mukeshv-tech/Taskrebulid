const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'taskrebuild', 'extension');

const files = {
  'package.json': `{
  "name": "taskrebuild",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \\"src/**/*.{ts,tsx,css}\\"",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/chrome": "^0.0.260",
    "@types/react": "^18.2.66",
    "@types/react-dom": "^18.2.22",
    "@typescript-eslint/eslint-plugin": "^7.2.0",
    "@typescript-eslint/parser": "^7.2.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.6",
    "prettier": "^3.2.5",
    "typescript": "^5.2.2",
    "vite": "^5.2.0"
  }
}
`,
  'tsconfig.json': `{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
`,
  'tsconfig.node.json': `{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
`,
  'vite.config.ts': `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'index.html'),
        background: resolve(__dirname, 'src/background/index.ts'),
        content: resolve(__dirname, 'src/content/index.ts')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background' || chunkInfo.name === 'content') {
            return '[name].js';
          }
          return 'assets/[name]-[hash].js';
        }
      }
    }
  }
});
`,
  '.eslintrc.cjs': `module.exports = {
  root: true,
  env: { browser: true, es2020: true, webextensions: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
`,
  '.prettierrc': `{
  "semi": true,
  "tabWidth": 2,
  "singleQuote": true,
  "trailingComma": "es5"
}
`,
  '.gitignore': `node_modules
dist
dist-ssr
*.local
.env
.env.*
.env.*.local
.DS_Store
`,
  'README.md': `# TaskRebuild

1. **What TaskRebuild is:** A future AI-powered, task-aware browser system.
2. **Current phase:** Phase 0 — Project Foundation.
3. **Technology stack:** TypeScript, Manifest V3, Vite, React, npm, ESLint, Prettier.
4. **Installation:** Run \`npm install\`.
5. **Development commands:** \`npm run dev\`, \`npm run build\`, \`npm run lint\`, \`npm run format\`, \`npm run typecheck\`.
6. **How to build:** Run \`npm run build\`. The output will be in the \`dist\` directory.
7. **How to load the extension into Chrome:** 
   - Open Chrome and navigate to \`chrome://extensions/\`.
   - Enable "Developer mode" in the top right corner.
   - Click "Load unpacked" and select the \`dist\` directory within this project.
8. **Current limitations:** This is a minimal skeleton with no logic.
9. **Planned future phases:** Phase 1 will include further setup.

**Phase 0 does NOT include:**
* Authentication
* Supabase
* Cloud synchronization
* AI
* Automatic task detection
* Browsing-history collection
* Task graphs
* Resource monitoring
* Reconstruction
`,
  'public/manifest.json': `{
  "manifest_version": 3,
  "name": "TaskRebuild",
  "version": "0.1.0",
  "description": "Experimental task-aware browsing project prototype.",
  "action": {
    "default_popup": "index.html"
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ]
}
`,
  'index.html': `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TaskRebuild Popup</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/popup/main.tsx"></script>
  </body>
</html>
`,
  'src/background/index.ts': `console.log('TaskRebuild background service started');\n`,
  'src/content/index.ts': `console.log('TaskRebuild content script initialized');\n`,
  'src/popup/main.tsx': `import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
`,
  'src/popup/App.tsx': `import React from 'react';

const App: React.FC = () => {
  return (
    <div className="popup-container">
      <h1>TaskRebuild</h1>
      <p>Your browser remembers the work, not just the tabs.</p>
      
      <div className="status-section">
        <span className="status-label">Status</span>
        <span className="status-value">Local prototype</span>
      </div>
      
      <button className="new-task-btn" type="button">New Task</button>
    </div>
  );
};

export default App;
`,
  'src/popup/styles.css': `body {
  margin: 0;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  width: 300px;
  background-color: #f9fafb;
  color: #111827;
}

.popup-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

p {
  margin: 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.4;
}

.status-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  margin-top: 4px;
}

.status-label {
  font-size: 13px;
  font-weight: 600;
}

.status-value {
  font-size: 13px;
  color: #059669;
  font-weight: 500;
}

.new-task-btn {
  margin-top: 8px;
  padding: 10px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.new-task-btn:hover {
  background-color: #1d4ed8;
}
`
};

function ensureDirSync(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

for (const [relativePath, content] of Object.entries(files)) {
  const fullPath = path.join(basePath, relativePath);
  ensureDirSync(path.dirname(fullPath));
  fs.writeFileSync(fullPath, content, 'utf8');
  console.log('Created:', fullPath);
}
