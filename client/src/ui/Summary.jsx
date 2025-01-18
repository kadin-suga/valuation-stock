import React from 'react';
import { useLocation } from 'react-router-dom';

const Summary = ({ aiResponse }) => {
  // Helper function to convert plain text into HTML with formatting
  const formatText = (text) => {
    if (!text) return null;

    // Replace line breaks with <br> tags
    const formattedText = text
      .replace(/\n\n/g, '</p><p>') // Separate paragraphs
      .replace(/\n/g, '<br>') // Line breaks within a paragraph
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>') // Bold text
      .replace(/\* ([^\n]+)/g, '<li>$1</li>'); // List items

    // Wrap bullet points in <ul> tags
    return formattedText.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
  };

  const analysis = aiResponse?.['LLM analysis'] || 
    'The AI-generated summary of this stock will appear here. The summary will provide insights about the company\'s performance, market position, and potential outlook.';
  
  return (
    <div className="w-full max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow p-8">
        <h3 className="text-2xl font-semibold mb-6 text-black">AI Summary</h3>
        <div className="prose prose-lg max-w-none">
          {/* Use dangerouslySetInnerHTML to render formatted content */}
          <div
            className="text-gray-800 leading-relaxed text-lg"
            dangerouslySetInnerHTML={{ __html: formatText(analysis) }}
          />
        </div>
      </div>
    </div>
  );
};

export default Summary;
