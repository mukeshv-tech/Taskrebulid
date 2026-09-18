import React from 'react';

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
