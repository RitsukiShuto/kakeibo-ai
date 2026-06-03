import React from 'react';
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts';
import type { SankeyData } from '../api/client';
import { VIVID_PALETTE } from '../utils/constants';

interface SankeyChartProps {
  data: SankeyData | null;
}

const CustomNode = (props: any) => {
  const { x, y, width, height, index, payload } = props;
  
  // payload.value が未定義の場合は 0 にフォールバック
  const value = payload?.value || 0;
  
  // textのx位置：幅が十分にあれば箱の中（左寄り）、なければ箱の右外側
  // x位置から画面右端のノードかどうかを簡易判定（xが大きな値の場合は右端）
  const isRightMost = x > 200; 
  
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={Math.max(height, 2)} // 最低でも2pxの高さを確保
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

  // Nodes format for recharts Sankey is simple array, links are {source, target, value}
  // Recharts requires nodes to just be the array of nodes, but it mutates them, so we clone.
  const chartData = {
    nodes: data.nodes.map(n => ({ ...n, name: n.name })),
    links: data.links.map(l => ({ ...l }))
  };

  // 項目数が多い場合はpaddingを減らしてボックスの描画領域を確保する
  const nodePadding = Math.max(10, Math.min(40, Math.floor(200 / data.nodes.length)));

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <Sankey
          data={chartData}
          node={CustomNode}
          link={{ stroke: '#475569', strokeOpacity: 0.3 }}
          nodePadding={nodePadding}
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
          linkCurvature={0.5}
          iterations={32}
        >
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#0f172a', 
              border: '1px solid #1e293b', 
              borderRadius: '8px',
              color: '#f1f5f9'
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
