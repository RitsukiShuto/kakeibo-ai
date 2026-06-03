import React from 'react';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';
import type { SankeyData } from '../api/client';
import { VIVID_PALETTE } from '../utils/constants';

interface SankeyChartProps {
  data: SankeyData | null;
}

const CustomNode = (props: any) => {
  const { x, y, width, height, index, payload } = props;
  
  const value = payload?.value || 0;
  
  // 右端のノード（出力先がないノード）かどうかを判定
  const isRightMost = !payload.sourceLinks || payload.sourceLinks.length === 0;
  
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={Math.max(height, 2)} 
        fill={VIVID_PALETTE[index % VIVID_PALETTE.length]}
        fillOpacity={1}
        rx={2}
        ry={2}
      />
      <text
        x={isRightMost ? x - 8 : x + width + 8}
        y={y + Math.max(height, 2) / 2}
        textAnchor={isRightMost ? 'end' : 'start'}
        fontSize="12"
        fill="#f8fafc"
        fontWeight="bold"
        dy={4}
        style={{ textShadow: '0px 1px 2px rgba(0,0,0,0.8)' }}
      >
        {`${payload?.name || ''} ¥${Math.round(value).toLocaleString()}`}
      </text>
    </g>
  );
};

const SankeyChart: React.FC<SankeyChartProps> = ({ data }) => {
  if (!data || !data.nodes || data.nodes.length === 0) {
    return <div className="text-slate-400 text-xs text-center p-8">データがありません</div>;
  }

  const chartData = {
    nodes: data.nodes.map(n => ({ ...n, name: n.name })),
    links: data.links.map(l => ({ ...l }))
  };

  const nodePadding = Math.max(10, Math.min(40, Math.floor(200 / data.nodes.length)));

  return (
    <div className="w-full h-full relative" style={{ overflow: 'visible' }}>
      {/* 
        RechartsのSankeyはsvgのoverflow: hiddenによってテキストが見切れることがあるため、
        ResponsiveContainerの幅を少し小さめにし、余白(margin)を使ってテキスト領域を確保します。
      */}
      <ResponsiveContainer width="100%" height="100%">
        <Sankey
          data={chartData}
          node={CustomNode}
          link={{ stroke: '#475569', strokeOpacity: 0.3 }}
          nodePadding={nodePadding}
          nodeWidth={15}
          margin={{ top: 20, right: 180, bottom: 20, left: 160 }} 
          linkCurvature={0.5}
          iterations={32}
        >
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0f172a', 
              border: '1px solid #1e293b', 
              borderRadius: '8px',
              color: '#f1f5f9',
              zIndex: 1000
            }}
            itemStyle={{ color: '#f1f5f9' }}
            formatter={(value: any) => [`¥${Math.round(Number(value)).toLocaleString()}`, '金額']}
          />
        </Sankey>
      </ResponsiveContainer>
    </div>
  );
};

export default SankeyChart;
