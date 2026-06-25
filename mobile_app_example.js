/**
 * SkyJames Mobile App Example (React Native)
 * Demonstrates how to integrate with the API
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';

const API_URL = 'http://YOUR_IP_ADDRESS:5002/api/mobile';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState('disconnected');

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      const data = await response.json();
      setStatus('online');
      console.log('API Status:', data);
    } catch (error) {
      setStatus('offline');
      console.error('API Error:', error);
    }
  };

  const captureImage = () => {
    launchCamera({ mediaType: 'photo', quality: 0.8 }, handleImageResponse);
  };

  const pickImage = () => {
    launchImageLibrary({ mediaType: 'photo', quality: 0.8 }, handleImageResponse);
  };

  const handleImageResponse = (response) => {
    if (response.didCancel) return;
    if (response.error) {
      Alert.alert('Error', 'Failed to capture image');
      return;
    }
    setImage(response.assets[0]);
    setResult(null);
  };

  const detectLanes = async () => {
    if (!image) {
      Alert.alert('Error', 'Please capture or select an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: image.uri,
        type: image.type || 'image/jpeg',
        name: image.fileName || 'photo.jpg',
      });

      const response = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
      
      if (data.error) {
        Alert.alert('Error', data.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to process image');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const detectObjects = async () => {
    if (!image) {
      Alert.alert('Error', 'Please capture or select an image first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: image.uri,
        type: image.type || 'image/jpeg',
        name: image.fileName || 'photo.jpg',
      });

      const response = await fetch(`${API_URL}/objects`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
      
      if (data.error) {
        Alert.alert('Error', data.error);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to process image');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🚀 SkyJames</Text>
        <Text style={[styles.status, { color: status === 'online' ? 'green' : 'red' }]}>
          {status === 'online' ? '● Online' : '● Offline'}
        </Text>
      </View>

      {image && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image.uri }} style={styles.image} />
          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.button} onPress={detectLanes}>
              <Text style={styles.buttonText}>🛣️ Detect Lanes</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.button} onPress={detectObjects}>
              <Text style={styles.buttonText}>🔍 Detect Objects</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4a6cf7" />
          <Text style={styles.loadingText}>Processing...</Text>
        </View>
      )}

      {result && result.status === 'success' && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>✅ Results</Text>
          {result.left_lane && (
            <Text style={styles.resultText}>
              Left Lane: {JSON.stringify(result.left_lane)}
            </Text>
          )}
          {result.right_lane && (
            <Text style={styles.resultText}>
              Right Lane: {JSON.stringify(result.right_lane)}
            </Text>
          )}
          {result.count !== undefined && (
            <Text style={styles.resultText}>
              Objects Detected: {result.count}
            </Text>
          )}
          {result.image && (
            <Image
              source={{ uri: `data:image/jpeg;base64,${result.image}` }}
              style={styles.resultImage}
            />
          )}
        </View>
      )}

      <View style={styles.footer}>
        <TouchableOpacity style={styles.footerButton} onPress={captureImage}>
          <Text style={styles.footerButtonText}>📷 Capture</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.footerButton} onPress={pickImage}>
          <Text style={styles.footerButtonText}>🖼️ Gallery</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.footerButton, styles.refreshButton]} onPress={checkStatus}>
          <Text style={styles.footerButtonText}>🔄 Refresh</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f7',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a2e',
  },
  status: {
    fontSize: 14,
    fontWeight: '600',
  },
  imageContainer: {
    alignItems: 'center',
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 10,
    marginBottom: 15,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  button: {
    backgroundColor: '#4a6cf7',
    padding: 12,
    borderRadius: 8,
    flex: 0.45,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  resultContainer: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginVertical: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a2e',
    marginBottom: 10,
  },
  resultText: {
    fontSize: 14,
    color: '#333',
    marginVertical: 2,
  },
  resultImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginTop: 10,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 'auto',
    paddingVertical: 20,
  },
  footerButton: {
    backgroundColor: '#e8e8e8',
    padding: 12,
    borderRadius: 8,
    flex: 0.3,
    alignItems: 'center',
  },
  footerButtonText: {
    color: '#333',
    fontWeight: '500',
  },
  refreshButton: {
    backgroundColor: '#4a6cf7',
  },
});

export default App;
