import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';
import type { AssetTrend } from '../api/client';

interface AssetChartProps {
  data: AssetTrend[];
  timeframe?: '1m' | '3m' | '6m' | '1y' | 'all';
}

const AssetChart: React.FC<AssetChartProps> = ({ data, timeframe = 'all' }) => {
  const chartData = useMemo(() => {
    if (!data.length) return [];

    let filteredData = [...data];
    if (timeframe !== 'all') {
      const now = new Date();
      const months = timeframe === '1m' ? 1 : timeframe === '3m' ? 3 : timeframe === '6m' ? 6 : 12;
      const cutoff = new Date();
      cutoff.setMonth(now.getMonth() - months);
      const cutoffStr = cutoff.toISOString().split('T')[0];
      filteredData = data.filter(item => item.acquired_date >= cutoffStr);
    }

    const chartDataMap: { [month: string]: any } = {};
    const assetTypes = new Set<string>();

    filteredData.forEach((item) => {
      const month = item.acquired_date.slice(0, 7);
      if (!chartDataMap[month]) {
        chartDataMap[month] = { date: month };
      }
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

  if (chartData.length === 0) {
    return <div className="text-muted text-center p-8">データがありません。</div>;
  }

  // If there is only 1 point, an AreaChart won't render lines. We render a PieChart instead.
  if (chartData.length === 1) {
    const singleData = chartData[0];
    const pieData = assetTypes.map(type => ({
      name: type,
      value: singleData[type] || 0
    })).filter(d => d.value > 0);

    return (
      <div style={{ width: '100%', height: 300, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '8px' }}>
          {singleData.date} 現在の資産配分 (データが1件のみのため円グラフ表示)
        </div>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', color: '#f1f5f9', borderRadius: '8px' }}
              itemStyle={{ color: '#f1f5f9' }}
              formatter={(value: any) => [`${(Number(value) || 0).toLocaleString()}円`, '']}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${(value / 10000).toLocaleString()}万`} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(255,255,255,0.1)', color: '#f1f5f9', borderRadius: '8px', backdropFilter: 'blur(8px)' }}
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
              fillOpacity={0.6}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AssetChart;
