import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { AssetTrend } from '../api/client';

interface AssetPieChartProps {
  data: AssetTrend[];
}

const AssetPieChart: React.FC<AssetPieChartProps> = ({ data }) => {
  const pieData = useMemo(() => {
    if (!data.length) return [];
    
    // 最新の日付を特定
    const latestDate = data.reduce((max, item) => 
      item.acquired_date > max ? item.acquired_date : max, 
      data[0].acquired_date
    );

    // 最新日付のデータを抽出
    return data
      .filter(item => item.acquired_date === latestDate)
      .map(item => ({
        name: item.asset_type,
        value: item.total_amount
      }))
      .filter(item => item.value > 0);
  }, [data]);

  // Indigo系カラーパレット
  const COLORS = ['#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff'];

  if (pieData.length === 0) {
    return <div className="text-slate-400 text-xs text-center p-8">データがありません</div>;
  }

  return (
    <div className="w-full h-full min-h-[200px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {pieData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.9)', 
              border: 'none', 
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}
            formatter={(value: any) => [`¥${Number(value).toLocaleString()}`, '金額']}
          />
          <Legend 
            verticalAlign="bottom" 
            align="center" 
            iconType="circle" 
            wrapperStyle={{ fontSize: '10px', fontWeight: 'bold', paddingTop: '10px' }} 
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AssetPieChart;
