import React from 'react';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';
import type { SankeyData } from '../api/client';

interface SankeyChartProps {
  data: SankeyData | null;
}

const SankeyChart: React.FC<SankeyChartProps> = ({ data }) => {
  if (!data || !data.nodes || data.nodes.length === 0) {
    return <div className="text-slate-400 text-xs text-center p-8">データがありません</div>;
  }

  // Nodes format for recharts Sankey is simple array, links are {source, target, value}
  // Recharts requires nodes to just be the array of nodes, but it mutates them, so we clone.
  const chartData = {
    nodes: data.nodes.map(n => ({ ...n, name: n.name })),
    links: data.links.map(l => ({ ...l }))
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <Sankey
          data={chartData}
          node={{ stroke: '#4f46e5', strokeWidth: 1, fill: '#6366f1' }}
          link={{ stroke: '#334155', strokeOpacity: 0.2 }}
          nodePadding={50}
          margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
          linkCurvature={0.5}
          iterations={64}
        >
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0f172a', 
              border: '1px solid #1e293b', 
              borderRadius: '8px',
              color: '#f1f5f9'
            }}
            itemStyle={{ color: '#f1f5f9' }}
          />
        </Sankey>
      </ResponsiveContainer>
    </div>
  );
};

export default SankeyChart;
