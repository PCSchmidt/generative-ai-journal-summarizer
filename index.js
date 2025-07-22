import { registerRootComponent } from 'expo';
import MinimalTest from './MinimalTest';

console.log('🔧 Index.js loading...');
console.log('📦 Components loaded, registering root component...');

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(MinimalTest);

console.log('✅ Root component registered successfully!');
