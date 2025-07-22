console.log('🔧 Index.js starting...');

try {
  const { registerRootComponent } = require('expo');
  console.log('📦 Expo loaded successfully');
  
  const MinimalTest = require('./MinimalTest').default;
  console.log('🎯 MinimalTest component loaded');
  
  console.log('� About to register root component...');
  registerRootComponent(MinimalTest);
  console.log('✅ Root component registered successfully!');
  
} catch (error) {
  console.error('❌ Error in index.js:', error);
  console.error('Stack:', error.stack);
  
  // Fallback - create simple div
  document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('root');
    if (root) {
      root.innerHTML = `
        <div style="
          background: #0a0a0a; 
          color: #ff0000; 
          padding: 50px; 
          text-align: center;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: Arial;
        ">
          ❌ JavaScript Error: ${error.message}
        </div>
      `;
    }
  });
}
