import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useState } from 'react';

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
      const response = await fetch(`https://ai-journal-backend-production.up.railway.app/api/ai/${analysisType}`, {
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

  const analyzeAll = async () => {
    if (!journalText.trim()) {
      Alert.alert('Input Required', 'Please enter some journal text');
      return;
    }

    setActiveTab('results');
    await Promise.all([
      handleAnalyze('summarize'),
      handleAnalyze('sentiment'),
      handleAnalyze('insights')
    ]);
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
    <View style={styles.inputSection}>
      <Text style={styles.label}>Journal Entry:</Text>
      <TextInput
        style={styles.textInput}
        placeholder="Write about your day, thoughts, or experiences...

Example: 'Today was an amazing day! I started my new job and met incredible colleagues. I feel excited about this new chapter in my life and can't wait to see what opportunities await.'"
        value={journalText}
        onChangeText={setJournalText}
        multiline
        numberOfLines={8}
        textAlignVertical="top"
      />
      
      <View style={styles.buttonRow}>
        <TouchableOpacity 
          style={[styles.button, styles.primaryButton]} 
          onPress={analyzeAll}
          disabled={loading.summarize || loading.sentiment || loading.insights}
        >
          <Text style={styles.buttonText}>
            {loading.summarize || loading.sentiment || loading.insights ? '🔄 Analyzing...' : '🚀 Analyze All'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.buttonRow}>
        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]} 
          onPress={() => handleAnalyze('summarize')}
          disabled={loading.summarize}
        >
          <Text style={styles.secondaryButtonText}>
            {loading.summarize ? '🔄' : '📝'} Summary
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]} 
          onPress={() => handleAnalyze('sentiment')}
          disabled={loading.sentiment}
        >
          <Text style={styles.secondaryButtonText}>
            {loading.sentiment ? '🔄' : '😊'} Sentiment
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]} 
          onPress={() => handleAnalyze('insights')}
          disabled={loading.insights}
        >
          <Text style={styles.secondaryButtonText}>
            {loading.insights ? '🔄' : '💡'} Insights
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderResultCard = (title, icon, result, type) => {
    if (!result) return null;
    
    const getConfidenceColor = (confidence) => {
      if (confidence >= 0.8) return '#4CAF50';
      if (confidence >= 0.6) return '#FF9800';
      return '#F44336';
    };

    const getSentimentEmoji = (sentiment) => {
      switch (sentiment) {
        case 'positive': return '😊';
        case 'negative': return '😔';
        case 'neutral': return '😐';
        default: return '🤔';
      }
    };

    return (
      <View style={styles.resultCard} key={type}>
        <View style={styles.resultHeader}>
          <Text style={styles.resultTitle}>{icon} {title}</Text>
          <View style={styles.confidenceBadge}>
            <View 
              style={[
                styles.confidenceDot, 
                { backgroundColor: getConfidenceColor(result.confidence) }
              ]} 
            />
            <Text style={styles.confidenceText}>
              {Math.round(result.confidence * 100)}%
            </Text>
          </View>
        </View>
        
        <Text style={styles.resultText}>{result.result}</Text>
        
        <View style={styles.metadata}>
          <Text style={styles.metadataText}>
            📊 {result.metadata.word_count} words
          </Text>
          {result.metadata.sentiment && (
            <Text style={styles.metadataText}>
              {getSentimentEmoji(result.metadata.sentiment)} {result.metadata.sentiment}
            </Text>
          )}
          <Text style={styles.metadataText}>
            🤖 {result.metadata.model}
          </Text>
        </View>
      </View>
    );
  };

  const renderResultsTab = () => (
    <ScrollView style={styles.resultsSection}>
      {!Object.keys(aiResults).length ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateTitle}>🧠 AI Analysis Results</Text>
          <Text style={styles.emptyStateText}>
            Write a journal entry and analyze it to see AI insights here!
          </Text>
        </View>
      ) : (
        <>
          {renderResultCard('Summary', '📝', aiResults.summarize, 'summarize')}
          {renderResultCard('Sentiment Analysis', '😊', aiResults.sentiment, 'sentiment')}
          {renderResultCard('Personal Insights', '💡', aiResults.insights, 'insights')}
        </>
      )}
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      <View style={styles.header}>
        <Text style={styles.title}>🧠 AI Journal Summarizer</Text>
        <Text style={styles.subtitle}>Transform thoughts into insights</Text>
      </View>

      {renderTabBar()}

      <View style={styles.content}>
        {activeTab === 'write' ? renderWriteTab() : renderResultsTab()}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: '#1a1a2e',
    borderBottomWidth: 1,
    borderBottomColor: '#16213e',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#8892b0',
    textAlign: 'center',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#1a1a2e',
    borderBottomWidth: 1,
    borderBottomColor: '#16213e',
  },
  tab: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  activeTab: {
    borderBottomColor: '#64ffda',
  },
  tabText: {
    fontSize: 16,
    color: '#8892b0',
    fontWeight: '500',
  },
  activeTabText: {
    color: '#64ffda',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  inputSection: {
    padding: 20,
  },
  label: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  textInput: {
    backgroundColor: '#1a1a2e',
    borderWidth: 2,
    borderColor: '#16213e',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#ffffff',
    height: 200,
    marginBottom: 20,
    fontFamily: 'System',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  button: {
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  primaryButton: {
    backgroundColor: '#64ffda',
    flex: 1,
  },
  secondaryButton: {
    backgroundColor: '#1a1a2e',
    borderWidth: 2,
    borderColor: '#64ffda',
    flex: 1,
    marginHorizontal: 4,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0f0f23',
  },
  secondaryButtonText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#64ffda',
  },
  resultsSection: {
    flex: 1,
    padding: 20,
  },
  resultCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#64ffda',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#64ffda',
  },
  confidenceBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#16213e',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  confidenceDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  confidenceText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  resultText: {
    fontSize: 16,
    color: '#ffffff',
    lineHeight: 24,
    marginBottom: 12,
  },
  metadata: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    borderTopWidth: 1,
    borderTopColor: '#16213e',
    paddingTop: 12,
  },
  metadataText: {
    fontSize: 12,
    color: '#8892b0',
    fontWeight: '500',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#64ffda',
    marginBottom: 12,
    textAlign: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#8892b0',
    textAlign: 'center',
    lineHeight: 24,
    paddingHorizontal: 20,
  },
});
