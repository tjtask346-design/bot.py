export const aimSpaceTheme = {
  colors: {
    // Primary Colors (From your code)
    primary: {
      50: '#f0fdff',
      100: '#ccf5ff',
      200: '#99e9ff',
      300: '#66d9ff',
      400: '#3fc9ff',
      500: '#22d3ee', // Main cyan
      600: '#06b6d4', // Dark cyan
      700: '#0891b2',
      800: '#0e7490',
      900: '#155e75',
    },
    
    // Background Gradients (Exact from your code)
    background: {
      primary: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      glass: 'rgba(30, 41, 59, 0.6)',
      glassDark: 'rgba(15, 23, 42, 0.8)'
    },
    
    // Text Colors
    text: {
      primary: '#e2e8f0',
      secondary: '#94a3b8',
      muted: '#64748b'
    },
    
    // Border Colors
    border: {
      light: 'rgba(255, 255, 255, 0.1)',
      medium: '#334155',
      dark: '#1e293b'
    }
  },
  
  effects: {
    glass: {
      background: 'rgba(30, 41, 59, 0.6)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '1.5rem'
    },
    shadow: {
      button: '0 4px 20px rgba(34, 211, 238, 0.3)',
      buttonHover: '0 6px 25px rgba(34, 211, 238, 0.4)'
    }
  }
};
