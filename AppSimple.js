import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';

export default function App() {
  const [journalText, setJournalText] = useState('');
  const [aiResults, setAiResults] = useState({});
  const [loading, setLoading] = useState({});
  const [activeTab, setActiveTab] = useState('write');

  const handleAnalyze = async (analysisType = 'summarize') => {
    if (!journalText.trim()) {
      Alert.alert('Input Required', 'Please enter some journal text');
      return;
    }

    setLoading(prev => ({ ...prev, [analysisType]: true }));
    
    try {
      const response = await fetch(`http://localhost:8000/api/ai/${analysisType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: journalText,
          task_type: analysisType
        })
      });

      if (response.ok) {
        const result = await response.json();
        setAiResults(prev => ({ ...prev, [analysisType]: result }));
        if (activeTab === 'write') {
          setActiveTab('results');
        }
      } else {
        Alert.alert('Error', 'Failed to process text');
      }
    } catch (error) {
      Alert.alert('Error', 'Error connecting to AI service');
      console.error(error);
    }
    
    setLoading(prev => ({ ...prev, [analysisType]: false }));
  };

  const renderTabBar = () => (
    <View style={styles.tabBar}>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'write' && styles.activeTab]}
        onPress={() => setActiveTab('write')}
      >
        <Text style={[styles.tabText, activeTab === 'write' && styles.activeTabText]}>
          ✍️ Write
        </Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.tab, activeTab === 'results' && styles.activeTab]}
        onPress={() => setActiveTab('results')}
      >
        <Text style={[styles.tabText, activeTab === 'results' && styles.activeTabText]}>
          🧠 AI Analysis
        </Text>
      </TouchableOpacity>
    </View>
  );

  const renderWriteTab = () => (
    <ScrollView style={styles.content}>
      <Text style={styles.heading}>📝 Journal Entry</Text>
      <TextInput
        style={styles.textInput}
        placeholder="Write your thoughts, experiences, or reflections here..."
        placeholderTextColor="#666"
        multiline
        value={journalText}
        onChangeText={setJournalText}
        textAlignVertical="top"
      />
      
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={() => handleAnalyze('sentiment')}
          disabled={loading.sentiment}
        >
          <Text style={styles.buttonText}>
            {loading.sentiment ? '🔄 Analyzing...' : '😊 Analyze Sentiment'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={() => handleAnalyze('insights')}
          disabled={loading.insights}
        >
          <Text style={styles.buttonText}>
            {loading.insights ? '🔄 Extracting...' : '🎯 Extract Insights'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={() => handleAnalyze('summarize')}
          disabled={loading.summarize}
        >
          <Text style={styles.buttonText}>
            {loading.summarize ? '🔄 Summarizing...' : '📋 Summarize'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );

  const renderResultsTab = () => (
    <ScrollView style={styles.content}>
      <Text style={styles.heading}>🤖 AI Analysis Results</Text>
      
      {Object.keys(aiResults).length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>No analysis results yet.</Text>
          <Text style={styles.emptySubtext}>Switch to the Write tab to analyze your journal entry.</Text>
        </View>
      ) : (
        Object.entries(aiResults).map(([type, result]) => (
          <View key={type} style={styles.resultCard}>
            <Text style={styles.resultTitle}>
              {type === 'sentiment' && '😊 Sentiment Analysis'}
              {type === 'insights' && '🎯 Key Insights'}
              {type === 'summarize' && '📋 Summary'}
            </Text>
            <Text style={styles.resultText}>{result.result}</Text>
            {result.confidence && (
              <Text style={styles.confidenceText}>
                Confidence: {Math.round(result.confidence * 100)}%
              </Text>
            )}
          </View>
        ))
      )}
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      <View style={styles.header}>
        <Text style={styles.title}>🤖 AI Journal Summarizer</Text>
      </View>

      {renderTabBar()}

      {activeTab === 'write' ? renderWriteTab() : renderResultsTab()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  header: {
    backgroundColor: '#1a1a2e',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#00d9ff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00d9ff',
    textAlign: 'center',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#16213e',
  },
  tab: {
    flex: 1,
    paddingVertical: 15,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#00d9ff',
  },
  tabText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#888',
  },
  activeTabText: {
    color: '#00d9ff',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  heading: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 20,
  },
  textInput: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 15,
    color: '#ffffff',
    fontSize: 16,
    minHeight: 200,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#333',
  },
  buttonContainer: {
    gap: 12,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#00d9ff',
  },
  secondaryButton: {
    backgroundColor: '#1a1a2e',
    borderWidth: 1,
    borderColor: '#00d9ff',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 18,
    color: '#888',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  resultCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#333',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#00d9ff',
    marginBottom: 10,
  },
  resultText: {
    fontSize: 14,
    color: '#ffffff',
    lineHeight: 20,
    marginBottom: 8,
  },
  confidenceText: {
    fontSize: 12,
    color: '#888',
    fontStyle: 'italic',
  },
});
