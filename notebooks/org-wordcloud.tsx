import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import _ from 'lodash';

const WordCloud = () => {
  const [words, setWords] = useState([]);
  
  useEffect(() => {
    const loadData = async () => {
      const fileContent = await window.fs.readFile('HHA_All_Owners_2025.01.02.csv', { encoding: 'utf8' });
      const results = Papa.parse(fileContent, {
        header: true,
        skipEmptyLines: true
      });
      
      const orgFrequencies = _.countBy(results.data, 'ORGANIZATION NAME');
      const sortedOrgs = Object.entries(orgFrequencies)
        .map(([text, value]) => ({ text, value }))
        .filter(item => item.text && item.text.trim().length > 0)
        .sort((a, b) => b.value - a.value)
        .slice(0, 50); // Display top 50 organizations
      
      setWords(sortedOrgs);
    };
    
    loadData();
  }, []);

  const getSize = (count) => {
    const max = Math.max(...words.map(w => w.value));
    const min = Math.min(...words.map(w => w.value));
    const normalized = (count - min) / (max - min);
    return `text-${Math.max(1, Math.min(6, Math.ceil(normalized * 6)))}xl`;
  };

  const getColor = (index) => {
    const colors = [
      'text-blue-600',
      'text-blue-500',
      'text-indigo-600',
      'text-indigo-500',
      'text-purple-600',
      'text-purple-500'
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="p-8 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Home Health Organization Word Cloud</h2>
      <div className="flex flex-wrap justify-center gap-4">
        {words.map((word, index) => (
          <div
            key={word.text}
            className={`${getSize(word.value)} ${getColor(index)} font-medium p-2 hover:opacity-75 transition-opacity cursor-default`}
            title={`${word.text}: ${word.value} occurrences`}
          >
            {word.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WordCloud;