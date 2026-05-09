import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { AssetTrend } from '../api/client';

interface AssetChartProps {
  data: AssetTrend[];
}

const AssetChart: React.FC<AssetChartProps> = ({ data }) => {
  // データをRecharts用に変換（日付ごとにアセットタイプを並べる）
  const chartDataMap: { [date: string]: any } = {};
  const assetTypes = new Set<string>();

  data.forEach((item) => {
    if (!chartDataMap[item.acquired_date]) {
      chartDataMap[item.acquired_date] = { date: item.acquired_date };
    }
    chartDataMap[item.acquired_date][item.asset_type] = item.total_amount;
    assetTypes.add(item.asset_type);
  });

  const chartData = Object.values(chartDataMap).sort((a, b) => a.date.localeCompare(b.date));
  const types = Array.from(assetTypes);

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
            itemStyle={{ color: '#f1f5f9' }}
          />
          <Legend />
          {types.map((type, index) => (
            <Area 
              key={type}
              type="monotone" 
              dataKey={type} 
              stackId="1" 
              stroke={colors[index % colors.length]} 
              fill={colors[index % colors.length]} 
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AssetChart;
