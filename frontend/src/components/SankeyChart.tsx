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
    <div className="w-full h-full min-h-[450px]">
      <ResponsiveContainer width="100%" height="100%">
        <Sankey
          data={chartData}
          node={{ stroke: '#4f46e5', strokeWidth: 2, fill: '#6366f1' }}
          link={{ stroke: '#c7d2fe' }}
          nodePadding={50}
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
          linkCurvature={0.5}
        >
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.95)', 
              border: 'none', 
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
          />
        </Sankey>
      </ResponsiveContainer>
    </div>
  );
};

export default SankeyChart;
