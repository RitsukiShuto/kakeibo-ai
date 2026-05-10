import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { AssetTrend } from '../api/client';

interface AssetChartProps {
  data: AssetTrend[];
  timeframe?: '1m' | '3m' | '6m' | '1y' | 'all';
}

const AssetChart: React.FC<AssetChartProps> = ({ data, timeframe = 'all' }) => {
  const chartData = useMemo(() => {
    if (!data.length) return [];

    // 日付でフィルタリング（簡易的な実装）
    let filteredData = [...data];
    if (timeframe !== 'all') {
      const now = new Date();
      const months = timeframe === '1m' ? 1 : timeframe === '3m' ? 3 : timeframe === '6m' ? 6 : 12;
      const cutoff = new Date();
      cutoff.setMonth(now.getMonth() - months);
      const cutoffStr = cutoff.toISOString().split('T')[0];
      filteredData = data.filter(item => item.acquired_date >= cutoffStr);
    }

    // 月ごとにグルーピング
    const chartDataMap: { [month: string]: any } = {};
    const assetTypes = new Set<string>();

    filteredData.forEach((item) => {
      // YYYY-MM 形式にする
      const month = item.acquired_date.slice(0, 7);
      if (!chartDataMap[month]) {
        chartDataMap[month] = { date: month };
      }
      // 同じ月の同じアセットタイプは最新の日付のものを採用したいが、
      // ここでは簡易的に加算するか、最後の上書きを許容する。
      // 本来は月末時点の残高を表示するのが正しい。
      chartDataMap[month][item.asset_type] = item.total_amount;
      assetTypes.add(item.asset_type);
    });

    return Object.values(chartDataMap).sort((a: any, b: any) => a.date.localeCompare(b.date));
  }, [data, timeframe]);

  const assetTypes = useMemo(() => {
    const types = new Set<string>();
    data.forEach(item => types.add(item.asset_type));
    return Array.from(types);
  }, [data]);

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${(value / 10000).toLocaleString()}万`} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
            itemStyle={{ color: '#f1f5f9' }}
            formatter={(value: any) => [`${(Number(value) || 0).toLocaleString()}円`, '']}
          />
          <Legend />
          {assetTypes.map((type, index) => (
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
