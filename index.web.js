import { AppRegistry } from 'react-native';
import App from './AppMinimal';

// Register the main application
AppRegistry.registerComponent('main', () => App);

// Run the application for web
AppRegistry.runApplication('main', {
  initialProps: {},
  rootTag: document.getElementById('root'),
});
